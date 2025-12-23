#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import threading
import queue
from ctypes import *
from datetime import datetime

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

class CameraRecorder:
    """Handles camera recording in a separate thread"""
    
    def __init__(self, camera_handle, device_info):
        self.cam = camera_handle
        self.device_info = device_info
        self.recording_thread = None
        self.command_queue = queue.Queue()
        self.is_recording = False
        self.is_grabbing = False
        self.exit_flag = False
        self.current_filename = None
        self.record_params = None
        self.stats_lock = threading.Lock()
        self.stats = {
            'frames_captured': 0,
            'recording_start_time': None,
            'last_fps': 0.0
        }
        
    def get_device_name(self):
        """Extract device name from device info"""
        if self.device_info.nTLayerType == MV_GIGE_DEVICE:
            raw = self.device_info.SpecialInfo.stGigEInfo.chModelName
        elif self.device_info.nTLayerType == MV_USB_DEVICE:
            raw = self.device_info.SpecialInfo.stUsb3VInfo.chModelName
        elif self.device_info.nTLayerType == MV_GENTL_CAMERALINK_DEVICE:
            raw = self.device_info.SpecialInfo.stCMLInfo.chModelName
        elif self.device_info.nTLayerType == MV_GENTL_CXP_DEVICE:
            raw = self.device_info.SpecialInfo.stCXPInfo.chModelName
        elif self.device_info.nTLayerType == MV_GENTL_XOF_DEVICE:
            raw = self.device_info.SpecialInfo.stXoFInfo.chModelName
        else:
            return "Unknown_Device"
        
        return bytes(raw).split(b'\x00', 1)[0].decode(errors='ignore')
    
    def setup_recording_params(self):
        """Setup recording parameters from camera"""
        record_param = MV_CC_RECORD_PARAM()
        memset(byref(record_param), 0, sizeof(MV_CC_RECORD_PARAM))
        
        # Get width
        st_param = MVCC_INTVALUE()
        memset(byref(st_param), 0, sizeof(MVCC_INTVALUE))
        ret = self.cam.MV_CC_GetIntValue("Width", st_param)
        if ret != 0:
            raise Exception(f"Get width failed! ret=0x{ret:08x}")
        record_param.nWidth = st_param.nCurValue
        
        # Get height
        ret = self.cam.MV_CC_GetIntValue("Height", st_param)
        if ret != 0:
            raise Exception(f"Get height failed! ret=0x{ret:08x}")
        record_param.nHeight = st_param.nCurValue
        
        # Get pixel format
        st_enum_value = MVCC_ENUMVALUE()
        memset(byref(st_enum_value), 0, sizeof(MVCC_ENUMVALUE))
        ret = self.cam.MV_CC_GetEnumValue("PixelFormat", st_enum_value)
        if ret != 0:
            raise Exception(f"Get PixelFormat failed! ret=0x{ret:08x}")
        record_param.enPixelType = MvGvspPixelType(st_enum_value.nCurValue)
        
        # Get frame rate
        st_float_value = MVCC_FLOATVALUE()
        memset(byref(st_float_value), 0, sizeof(MVCC_FLOATVALUE))
        ret = self.cam.MV_CC_GetFloatValue("ResultingFrameRate", st_float_value)
        if ret != 0:
            ret = self.cam.MV_CC_GetFloatValue("AcquisitionFrameRate", st_float_value)
            if ret != 0:
                st_float_value.fCurValue = 30.0  # Default fallback
        record_param.fFrameRate = st_float_value.fCurValue
        
        # Set recording parameters
        record_param.nBitRate = 5000  # Bitrate in kbps
        record_param.enRecordFmtType = MV_FormatType_AVI
        
        self.record_params = record_param
        return record_param
    
    def recording_worker(self):
        """Worker thread that handles frame capture and recording"""
        frame_out = MV_FRAME_OUT()
        memset(byref(frame_out), 0, sizeof(frame_out))
        
        input_frame_info = MV_CC_INPUT_FRAME_INFO()
        memset(byref(input_frame_info), 0, sizeof(MV_CC_INPUT_FRAME_INFO))
        
        last_status_time = time.time()
        
        while not self.exit_flag:
            # Check for commands
            try:
                cmd = self.command_queue.get_nowait()
                if cmd == 'START_RECORDING':
                    if not self.is_recording and self.is_grabbing:
                        # Generate new filename
                        device_name = self.get_device_name().replace(" ", "_")
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        self.current_filename = f"{device_name}_{timestamp}.avi"
                        self.record_params.strFilePath = self.current_filename.encode('ascii')
                        
                        # Start recording
                        ret = self.cam.MV_CC_StartRecord(self.record_params)
                        if ret == 0:
                            self.is_recording = True
                            with self.stats_lock:
                                self.stats['frames_captured'] = 0
                                self.stats['recording_start_time'] = time.time()
                            print(f"\nStarted recording to: {self.current_filename}")
                        else:
                            print(f"\nError starting recording: 0x{ret:08x}")
                
                elif cmd == 'STOP_RECORDING':
                    if self.is_recording:
                        ret = self.cam.MV_CC_StopRecord()
                        if ret == 0:
                            self.is_recording = False
                            with self.stats_lock:
                                frames = self.stats['frames_captured']
                                duration = time.time() - self.stats['recording_start_time']
                            print(f"\nStopped recording. Saved {frames} frames ({duration:.1f}s) to: {self.current_filename}")
                        else:
                            print(f"\nError stopping recording: 0x{ret:08x}")
                
                elif cmd == 'EXIT':
                    self.exit_flag = True
                    
            except queue.Empty:
                pass
            
            # Capture frames if grabbing
            if self.is_grabbing:
                ret = self.cam.MV_CC_GetImageBuffer(frame_out, 100)  # 100ms timeout
                if frame_out.pBufAddr and ret == 0:
                    # If recording, save the frame
                    if self.is_recording:
                        input_frame_info.pData = cast(frame_out.pBufAddr, POINTER(c_ubyte))
                        input_frame_info.nDataLen = frame_out.stFrameInfo.nFrameLen
                        
                        ret = self.cam.MV_CC_InputOneFrame(input_frame_info)
                        if ret == 0:
                            with self.stats_lock:
                                self.stats['frames_captured'] += 1
                    
                    # Free the buffer
                    self.cam.MV_CC_FreeImageBuffer(frame_out)
                    
                    # Print status periodically
                    current_time = time.time()
                    if current_time - last_status_time >= 1.0:
                        with self.stats_lock:
                            if self.is_recording and self.stats['recording_start_time']:
                                elapsed = current_time - self.stats['recording_start_time']
                                fps = self.stats['frames_captured'] / elapsed if elapsed > 0 else 0
                                self.stats['last_fps'] = fps
                                print(f"\rRecording: {elapsed:.1f}s | {self.stats['frames_captured']} frames | {fps:.1f} fps", 
                                      end="", flush=True)
                        last_status_time = current_time
            else:
                # Sleep a bit if not grabbing to avoid busy waiting
                time.sleep(0.01)
    
    def start_grabbing(self):
        """Start the camera grabbing and worker thread"""
        if not self.is_grabbing:
            ret = self.cam.MV_CC_StartGrabbing()
            if ret == 0:
                self.is_grabbing = True
                self.exit_flag = False
                self.recording_thread = threading.Thread(target=self.recording_worker)
                self.recording_thread.daemon = True
                self.recording_thread.start()
                print("Started camera grabbing")
                return True
            else:
                print(f"Error starting grabbing: 0x{ret:08x}")
                return False
        return True
    
    def stop_grabbing(self):
        """Stop grabbing and clean up thread"""
        if self.is_grabbing:
            # Stop any ongoing recording first
            if self.is_recording:
                self.stop_recording()
            
            # Signal thread to exit
            self.command_queue.put('EXIT')
            
            # Wait for thread to finish
            if self.recording_thread:
                self.recording_thread.join(timeout=2.0)
            
            # Stop grabbing
            self.cam.MV_CC_StopGrabbing()
            self.is_grabbing = False
            print("\nStopped camera grabbing")
    
    def start_recording(self):
        """Start recording video"""
        if self.is_grabbing:
            self.command_queue.put('START_RECORDING')
        else:
            print("Camera must be grabbing before recording can start")
    
    def stop_recording(self):
        """Stop recording video"""
        if self.is_recording:
            self.command_queue.put('STOP_RECORDING')
        else:
            print("Not currently recording")
    
    def get_status(self):
        """Get current recording status"""
        with self.stats_lock:
            return {
                'is_grabbing': self.is_grabbing,
                'is_recording': self.is_recording,
                'frames_captured': self.stats['frames_captured'],
                'current_fps': self.stats['last_fps'],
                'current_file': self.current_filename if self.is_recording else None
            }

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
            print("\n")  # New line after dots
            return dev_list
        
        # Show waiting animation
        print("\rWaiting for camera device" + "." * (dot_count % 4) + "   ", end="", flush=True)
        dot_count += 1
        time.sleep(0.5)

def setup_camera(device_info):
    """Setup camera with optimal settings"""
    cam = MvCamera()
    
    # Create handle
    if cam.MV_CC_CreateHandle(device_info) != 0:
        print("Failed to create device handle.")
        return None
    
    # Open device
    if cam.MV_CC_OpenDevice(MV_ACCESS_Exclusive, 0) != 0:
        print("Failed to open device.")
        cam.MV_CC_DestroyHandle()
        return None
    
    # For GigE, set optimal packet size
    if device_info.nTLayerType == MV_GIGE_DEVICE:
        pkt = cam.MV_CC_GetOptimalPacketSize()
        if pkt > 0:
            cam.MV_CC_SetIntValue("GevSCPSPacketSize", pkt)
    
    # Turn off trigger mode
    cam.MV_CC_SetEnumValue("TriggerMode", MV_TRIGGER_MODE_OFF)
    
    # Enable frame rate control if available
    st_bool = c_bool(False)
    ret = cam.MV_CC_GetBoolValue("AcquisitionFrameRateEnable", st_bool)
    if ret == 0 and not st_bool.value:
        cam.MV_CC_SetBoolValue("AcquisitionFrameRateEnable", True)
    
    return cam

def print_camera_info(cam, recorder):
    """Print camera information"""
    print("\n" + "="*60)
    print("CAMERA INFORMATION")
    print("="*60)
    
    device_name = recorder.get_device_name()
    print(f"Device: {device_name}")
    
    # Get resolution
    st_int = MVCC_INTVALUE()
    memset(byref(st_int), 0, sizeof(MVCC_INTVALUE))
    if cam.MV_CC_GetIntValue("Width", st_int) == 0:
        width = st_int.nCurValue
        if cam.MV_CC_GetIntValue("Height", st_int) == 0:
            height = st_int.nCurValue
            print(f"Resolution: {width}×{height}")
    
    # Get frame rate
    st_float = MVCC_FLOATVALUE()
    memset(byref(st_float), 0, sizeof(MVCC_FLOATVALUE))
    if cam.MV_CC_GetFloatValue("ResultingFrameRate", st_float) == 0:
        print(f"Frame rate: {st_float.fCurValue:.2f} fps")
    elif cam.MV_CC_GetFloatValue("AcquisitionFrameRate", st_float) == 0:
        print(f"Frame rate: {st_float.fCurValue:.2f} fps (set)")
    
    print("="*60)

def print_help():
    """Print available commands"""
    print("\n" + "="*60)
    print("AVAILABLE COMMANDS")
    print("="*60)
    print("  g     - Start grabbing (preview mode)")
    print("  s     - Stop grabbing")
    print("  r     - Start recording")
    print("  t     - Stop recording")
    print("  i     - Show camera info")
    print("  status - Show current status")
    print("  h     - Show this help")
    print("  q     - Quit")
    print("="*60)

def main():
    # Initialize SDK
    MvCamera.MV_CC_Initialize()
    
    try:
        # Wait for device
        dev_list = wait_for_device()
        
        # Select device
        if dev_list.nDeviceNum == 1:
            print("Found 1 device, auto-connecting...")
            device_index = 0
        else:
            print(f"Found {dev_list.nDeviceNum} devices:")
            for i in range(dev_list.nDeviceNum):
                info = cast(dev_list.pDeviceInfo[i], POINTER(MV_CC_DEVICE_INFO)).contents
                # Quick device name extraction
                if info.nTLayerType == MV_USB_DEVICE:
                    name = bytes(info.SpecialInfo.stUsb3VInfo.chModelName).split(b'\x00', 1)[0].decode()
                else:
                    name = "Camera " + str(i)
                print(f"  [{i}] {name}")
            
            while True:
                try:
                    device_index = int(input(f"Select device [0-{dev_list.nDeviceNum-1}]: "))
                    if 0 <= device_index < dev_list.nDeviceNum:
                        break
                except ValueError:
                    pass
        
        # Get device info and setup camera
        device_info = cast(dev_list.pDeviceInfo[device_index], POINTER(MV_CC_DEVICE_INFO)).contents
        cam = setup_camera(device_info)
        if not cam:
            return
        
        # Create recorder
        recorder = CameraRecorder(cam, device_info)
        recorder.setup_recording_params()
        
        # Print camera info
        print_camera_info(cam, recorder)
        
        # Print help
        print_help()
        
        # Main command loop
        print("\nReady for commands. Type 'h' for help.")
        
        while True:
            try:
                cmd = input("\n> ").strip().lower()
                
                if cmd == 'q':
                    break
                
                elif cmd == 'g':
                    if recorder.start_grabbing():
                        print("Camera is now grabbing frames (preview mode)")
                
                elif cmd == 's':
                    recorder.stop_grabbing()
                
                elif cmd == 'r':
                    if not recorder.is_grabbing:
                        print("Start grabbing first (press 'g')")
                    else:
                        recorder.start_recording()
                
                elif cmd == 't':
                    recorder.stop_recording()
                
                elif cmd == 'i':
                    print_camera_info(cam, recorder)
                
                elif cmd == 'status':
                    status = recorder.get_status()
                    print("\n" + "-"*40)
                    print("CURRENT STATUS:")
                    print(f"  Grabbing: {'Yes' if status['is_grabbing'] else 'No'}")
                    print(f"  Recording: {'Yes' if status['is_recording'] else 'No'}")
                    if status['is_recording']:
                        print(f"  File: {status['current_file']}")
                        print(f"  Frames: {status['frames_captured']}")
                        print(f"  FPS: {status['current_fps']:.1f}")
                    print("-"*40)
                
                elif cmd == 'h':
                    print_help()
                
                elif cmd == '':
                    continue
                
                else:
                    print(f"Unknown command: '{cmd}'. Type 'h' for help.")
                    
            except KeyboardInterrupt:
                print("\nInterrupted by user")
                break
            except Exception as e:
                print(f"Error: {e}")
        
        # Cleanup
        print("\nCleaning up...")
        recorder.stop_grabbing()
        cam.MV_CC_CloseDevice()
        cam.MV_CC_DestroyHandle()
        
    finally:
        # Finalize SDK
        MvCamera.MV_CC_Finalize()
        print("Camera SDK finalized.")

if __name__ == "__main__":
    main()