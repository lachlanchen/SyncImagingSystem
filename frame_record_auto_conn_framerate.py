#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import threading
from ctypes import *

# Make sure your Python/MvImport folder is on the path:
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE, "haikang_sdk", "Python"))
sys.path.append(os.path.join(BASE, "haikang_sdk", "Python", "MvImport"))

from MvCameraControl_class import (
    MvCamera,
    MV_CC_DEVICE_INFO_LIST,
    MV_CC_DEVICE_INFO,
    MV_GIGE_DEVICE,
    MV_USB_DEVICE,
    MV_GENTL_CAMERALINK_DEVICE,
    MV_GENTL_CXP_DEVICE,
    MV_GENTL_XOF_DEVICE,
    MV_FRAME_OUT,
    MV_CC_RECORD_PARAM,
    MV_CC_INPUT_FRAME_INFO,
    MVCC_INTVALUE,
    MVCC_ENUMVALUE,
    MVCC_FLOATVALUE,
    MvGvspPixelType
)
from CameraParams_const import MV_ACCESS_Exclusive
from CameraParams_header import MV_TRIGGER_MODE_OFF, MV_FormatType_AVI

# Global flag for recording thread
g_bExit = False

def get_device_name(device_info):
    """Extract device name from device info"""
    if device_info.nTLayerType == MV_GIGE_DEVICE:
        raw = device_info.SpecialInfo.stGigEInfo.chModelName
    elif device_info.nTLayerType == MV_USB_DEVICE:
        raw = device_info.SpecialInfo.stUsb3VInfo.chModelName
    elif device_info.nTLayerType == MV_GENTL_CAMERALINK_DEVICE:
        raw = device_info.SpecialInfo.stCMLInfo.chModelName
    elif device_info.nTLayerType == MV_GENTL_CXP_DEVICE:
        raw = device_info.SpecialInfo.stCXPInfo.chModelName
    elif device_info.nTLayerType == MV_GENTL_XOF_DEVICE:
        raw = device_info.SpecialInfo.stXoFInfo.chModelName
    else:
        return "Unknown Device"
    
    return bytes(raw).split(b'\x00', 1)[0].decode(errors='ignore')

def wait_for_device():
    """Wait for a device to be connected"""
    dev_list = MV_CC_DEVICE_INFO_LIST()
    layers = (
        MV_GIGE_DEVICE
        | MV_USB_DEVICE
        | MV_GENTL_CAMERALINK_DEVICE
        | MV_GENTL_CXP_DEVICE
        | MV_GENTL_XOF_DEVICE
    )
    
    print("Waiting for camera device...")
    dot_count = 0
    
    while True:
        ret = MvCamera.MV_CC_EnumDevices(layers, dev_list)
        if ret == 0 and dev_list.nDeviceNum > 0:
            # Device found
            print("\n")  # New line after dots
            return dev_list
        
        # Show waiting animation
        print("\rWaiting for camera device" + "." * (dot_count % 4) + "   ", end="", flush=True)
        dot_count += 1
        time.sleep(0.5)

def check_and_set_frame_rate(cam, desired_fps=None):
    """Check if frame rate is adjustable and optionally set it"""
    frame_rate_info = {}
    
    # Check if AcquisitionFrameRateEnable exists
    st_bool = c_bool(False)
    ret = cam.MV_CC_GetBoolValue("AcquisitionFrameRateEnable", st_bool)
    if ret == 0:
        frame_rate_info['has_frame_rate_enable'] = True
        frame_rate_info['frame_rate_enabled'] = st_bool.value
        
        # Enable frame rate control if not already enabled
        if not st_bool.value:
            ret = cam.MV_CC_SetBoolValue("AcquisitionFrameRateEnable", True)
            if ret == 0:
                print("Enabled frame rate control")
                frame_rate_info['frame_rate_enabled'] = True
            else:
                print(f"Warning: Could not enable frame rate control (0x{ret:08x})")
    else:
        frame_rate_info['has_frame_rate_enable'] = False
        print("Note: Camera does not support AcquisitionFrameRateEnable")
    
    # Get current frame rate settings
    st_float_value = MVCC_FLOATVALUE()
    memset(byref(st_float_value), 0, sizeof(MVCC_FLOATVALUE))
    
    # Try to get AcquisitionFrameRate (settable parameter)
    ret = cam.MV_CC_GetFloatValue("AcquisitionFrameRate", st_float_value)
    if ret == 0:
        frame_rate_info['adjustable'] = True
        frame_rate_info['current_set_fps'] = st_float_value.fCurValue
        frame_rate_info['min_fps'] = st_float_value.fMin
        frame_rate_info['max_fps'] = st_float_value.fMax
        
        print(f"\nFrame Rate Settings:")
        print(f"  Current set FPS: {st_float_value.fCurValue:.2f}")
        print(f"  Adjustable range: {st_float_value.fMin:.2f} - {st_float_value.fMax:.2f} fps")
        
        # Set desired frame rate if specified
        if desired_fps is not None:
            if st_float_value.fMin <= desired_fps <= st_float_value.fMax:
                ret = cam.MV_CC_SetFloatValue("AcquisitionFrameRate", desired_fps)
                if ret == 0:
                    print(f"  Successfully set frame rate to {desired_fps} fps")
                    frame_rate_info['current_set_fps'] = desired_fps
                else:
                    print(f"  Error setting frame rate: 0x{ret:08x}")
            else:
                print(f"  Cannot set {desired_fps} fps - out of range!")
                print(f"  Using closest value: {max(st_float_value.fMin, min(desired_fps, st_float_value.fMax)):.2f} fps")
                closest_fps = max(st_float_value.fMin, min(desired_fps, st_float_value.fMax))
                ret = cam.MV_CC_SetFloatValue("AcquisitionFrameRate", closest_fps)
                if ret == 0:
                    frame_rate_info['current_set_fps'] = closest_fps
    else:
        frame_rate_info['adjustable'] = False
        print("\nFrame rate is not directly adjustable on this camera")
    
    # Get resulting frame rate (actual achieved frame rate)
    ret = cam.MV_CC_GetFloatValue("ResultingFrameRate", st_float_value)
    if ret == 0:
        frame_rate_info['resulting_fps'] = st_float_value.fCurValue
        print(f"  Resulting FPS: {st_float_value.fCurValue:.2f}")
    
    return frame_rate_info

def recording_thread(cam, record_duration=10):
    """Thread function to capture frames and record video"""
    global g_bExit
    
    frame_out = MV_FRAME_OUT()
    memset(byref(frame_out), 0, sizeof(frame_out))
    
    input_frame_info = MV_CC_INPUT_FRAME_INFO()
    memset(byref(input_frame_info), 0, sizeof(MV_CC_INPUT_FRAME_INFO))
    
    start_time = time.time()
    frame_count = 0
    last_print_time = time.time()
    
    while not g_bExit and (time.time() - start_time) < record_duration:
        ret = cam.MV_CC_GetImageBuffer(frame_out, 1000)
        if frame_out.pBufAddr and ret == 0:
            frame_count += 1
            
            # Print status every second
            if time.time() - last_print_time >= 1.0:
                elapsed = time.time() - start_time
                fps = frame_count / elapsed if elapsed > 0 else 0
                print(f"\rRecording: {elapsed:.1f}/{record_duration}s | {frame_count} frames | {fps:.1f} fps", end="", flush=True)
                last_print_time = time.time()
            
            # Input frame data to recording
            input_frame_info.pData = cast(frame_out.pBufAddr, POINTER(c_ubyte))
            input_frame_info.nDataLen = frame_out.stFrameInfo.nFrameLen
            
            ret = cam.MV_CC_InputOneFrame(input_frame_info)
            if ret != 0:
                print(f"\nWarning: Input frame failed! ret=0x{ret:08x}")
            
            cam.MV_CC_FreeImageBuffer(frame_out)
        elif ret != 0:
            # Only print error if it's not a timeout
            if ret != 0x80000007:  # MV_E_NODATA
                print(f"\nError getting frame: 0x{ret:08x}")
    
    print(f"\nTotal frames recorded: {frame_count}")

def setup_and_record_camera(device_info, device_index):
    """Setup camera and start recording"""
    global g_bExit
    
    # Create handle & open device
    cam = MvCamera()
    if cam.MV_CC_CreateHandle(device_info) != 0:
        print("Failed to create device handle.")
        return False
    
    if cam.MV_CC_OpenDevice(MV_ACCESS_Exclusive, 0) != 0:
        print("Failed to open device.")
        cam.MV_CC_DestroyHandle()
        return False

    try:
        # For GigE, set optimal packet size
        if device_info.nTLayerType == MV_GIGE_DEVICE:
            pkt = cam.MV_CC_GetOptimalPacketSize()
            if pkt > 0:
                cam.MV_CC_SetIntValue("GevSCPSPacketSize", pkt)

        # Turn off trigger
        cam.MV_CC_SetEnumValue("TriggerMode", MV_TRIGGER_MODE_OFF)

        # Check and potentially set frame rate
        print("\n" + "="*50)
        print("CAMERA FRAME RATE SETTINGS")
        print("="*50)
        
        # Ask user if they want to adjust frame rate
        while True:
            choice = input("\nDo you want to adjust frame rate? (y/n): ").lower()
            if choice in ['y', 'n']:
                break
        
        if choice == 'y':
            while True:
                try:
                    desired_fps = float(input("Enter desired frame rate (e.g., 30): "))
                    break
                except ValueError:
                    print("Please enter a valid number")
            
            frame_rate_info = check_and_set_frame_rate(cam, desired_fps)
        else:
            frame_rate_info = check_and_set_frame_rate(cam)
        
        print("="*50)

        # Get camera parameters for recording
        record_param = MV_CC_RECORD_PARAM()
        memset(byref(record_param), 0, sizeof(MV_CC_RECORD_PARAM))
        
        # Get width
        st_param = MVCC_INTVALUE()
        memset(byref(st_param), 0, sizeof(MVCC_INTVALUE))
        ret = cam.MV_CC_GetIntValue("Width", st_param)
        if ret != 0:
            raise Exception(f"Get width failed! ret=0x{ret:08x}")
        record_param.nWidth = st_param.nCurValue
        
        # Get height
        ret = cam.MV_CC_GetIntValue("Height", st_param)
        if ret != 0:
            raise Exception(f"Get height failed! ret=0x{ret:08x}")
        record_param.nHeight = st_param.nCurValue
        
        # Get pixel format
        st_enum_value = MVCC_ENUMVALUE()
        memset(byref(st_enum_value), 0, sizeof(MVCC_ENUMVALUE))
        ret = cam.MV_CC_GetEnumValue("PixelFormat", st_enum_value)
        if ret != 0:
            raise Exception(f"Get PixelFormat failed! ret=0x{ret:08x}")
        record_param.enPixelType = MvGvspPixelType(st_enum_value.nCurValue)
        
        # Get actual frame rate for recording
        st_float_value = MVCC_FLOATVALUE()
        memset(byref(st_float_value), 0, sizeof(MVCC_FLOATVALUE))
        ret = cam.MV_CC_GetFloatValue("ResultingFrameRate", st_float_value)
        if ret != 0:
            # If ResultingFrameRate not available, try AcquisitionFrameRate
            ret = cam.MV_CC_GetFloatValue("AcquisitionFrameRate", st_float_value)
            if ret != 0:
                raise Exception(f"Get frame rate failed! ret=0x{ret:08x}")
        record_param.fFrameRate = st_float_value.fCurValue
        
        # Set recording parameters
        record_param.nBitRate = 5000  # Bitrate in kbps
        record_param.enRecordFmtType = MV_FormatType_AVI
        
        # Create filename with timestamp
        device_name = get_device_name(device_info).replace(" ", "_")
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"{device_name}_{timestamp}.avi"
        record_param.strFilePath = filename.encode('ascii')
        
        print(f"\nRecording parameters:")
        print(f"  Device: {get_device_name(device_info)}")
        print(f"  Resolution: {record_param.nWidth}×{record_param.nHeight}")
        print(f"  Frame rate: {record_param.fFrameRate:.2f} fps")
        print(f"  Bit rate: {record_param.nBitRate} kbps")
        print(f"  File: {filename}")
        
        # Get recording duration from user
        while True:
            try:
                duration_input = input("\nEnter recording duration in seconds (or 'q' to quit): ")
                if duration_input.lower() == 'q':
                    return True  # Exit gracefully
                duration = int(duration_input) if duration_input else 10
                if duration <= 0:
                    print("Duration must be positive.")
                    continue
                break
            except ValueError:
                print("Please enter a valid number or 'q' to quit.")
        
        # Start recording
        ret = cam.MV_CC_StartRecord(record_param)
        if ret != 0:
            raise Exception(f"Start recording failed! ret=0x{ret:08x}")
        
        # Start grabbing
        ret = cam.MV_CC_StartGrabbing()
        if ret != 0:
            cam.MV_CC_StopRecord()
            raise Exception(f"Start grabbing failed! ret=0x{ret:08x}")
        
        # Start recording thread
        print(f"\nRecording for {duration} seconds...")
        g_bExit = False
        
        thread_handle = threading.Thread(target=recording_thread, args=(cam, duration))
        thread_handle.start()
        
        # Wait for recording to complete
        thread_handle.join()
        
        # Stop everything
        g_bExit = True
        print("\nStopping recording...")
        cam.MV_CC_StopGrabbing()
        cam.MV_CC_StopRecord()
        
        print(f"Video saved as: {filename}")
        
    except Exception as e:
        print(f"Error during recording: {e}")
        return False
    
    finally:
        # Clean up
        cam.MV_CC_CloseDevice()
        cam.MV_CC_DestroyHandle()
    
    return False  # Continue recording loop

def main():
    # Initialize SDK
    MvCamera.MV_CC_Initialize()
    
    try:
        while True:
            # Wait for device to be connected
            dev_list = wait_for_device()
            
            if dev_list.nDeviceNum == 1:
                # Auto-connect to single device
                print("Found 1 device, auto-connecting...")
                device_info = cast(dev_list.pDeviceInfo[0], POINTER(MV_CC_DEVICE_INFO)).contents
                device_name = get_device_name(device_info)
                print(f"Connected to: {device_name}")
                
                # Start recording loop
                if setup_and_record_camera(device_info, 0):
                    break  # User chose to quit
                    
            else:
                # Multiple devices found, let user choose
                print(f"Found {dev_list.nDeviceNum} devices:")
                for i in range(dev_list.nDeviceNum):
                    info = cast(dev_list.pDeviceInfo[i], POINTER(MV_CC_DEVICE_INFO)).contents
                    name = get_device_name(info)
                    print(f"  [{i}] {name}")
                
                while True:
                    try:
                        choice = input(f"Select device [0-{dev_list.nDeviceNum-1}] or 'q' to quit: ")
                        if choice.lower() == 'q':
                            return
                        
                        idx = int(choice)
                        if 0 <= idx < dev_list.nDeviceNum:
                            device_info = cast(dev_list.pDeviceInfo[idx], POINTER(MV_CC_DEVICE_INFO)).contents
                            if setup_and_record_camera(device_info, idx):
                                return  # User chose to quit
                            break
                        else:
                            print("Invalid index.")
                    except ValueError:
                        print("Please enter a valid number or 'q' to quit.")
            
            # Ask if user wants to record another video
            if input("\nRecord another video? (y/n): ").lower() != 'y':
                break
                
    finally:
        # Finalize SDK
        MvCamera.MV_CC_Finalize()
        print("\nCamera SDK finalized.")

if __name__ == "__main__":
    main()