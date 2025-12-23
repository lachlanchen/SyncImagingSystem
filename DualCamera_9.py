#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
import queue
import os
import sys
import platform
from datetime import datetime

# Import PIL for image conversion
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("PIL not available. Install Pillow for embedded preview support: pip install Pillow")

# Add the camera SDK paths (modify these paths according to your setup)
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE, "haikang_sdk", "Python"))
sys.path.append(os.path.join(BASE, "haikang_sdk", "Python", "MvImport"))

# Import frame camera modules
try:
    from ctypes import *
    import numpy as np
    import cv2
    from MvCameraControl_class import (
        MvCamera, MV_CC_DEVICE_INFO_LIST, MV_CC_DEVICE_INFO,
        MV_GIGE_DEVICE, MV_USB_DEVICE, MV_GENTL_CAMERALINK_DEVICE,
        MV_GENTL_CXP_DEVICE, MV_GENTL_XOF_DEVICE, MV_FRAME_OUT,
        MV_CC_RECORD_PARAM, MV_CC_INPUT_FRAME_INFO, MV_CC_PIXEL_CONVERT_PARAM,
        MVCC_INTVALUE, MVCC_ENUMVALUE, MVCC_FLOATVALUE, MvGvspPixelType
    )
    from CameraParams_const import MV_ACCESS_Exclusive
    from CameraParams_header import MV_TRIGGER_MODE_OFF, MV_FormatType_AVI
    from PixelType_header import PixelType_Gvsp_Mono8, PixelType_Gvsp_RGB8_Packed
    FRAME_CAMERA_AVAILABLE = True
except ImportError as e:
    print(f"Frame camera SDK not available: {e}")
    FRAME_CAMERA_AVAILABLE = False

# Import event camera modules
try:
    from metavision_core.event_io.raw_reader import initiate_device
    from metavision_core.event_io import EventsIterator
    from metavision_sdk_core import PeriodicFrameGenerationAlgorithm, ColorPalette
    from metavision_sdk_ui import EventLoop, BaseWindow, MTWindow, UIAction, UIKeyEvent
    EVENT_CAMERA_AVAILABLE = True
except ImportError as e:
    print(f"Event camera SDK not available: {e}")
    EVENT_CAMERA_AVAILABLE = False

# Platform-specific imports for always on top functionality
if platform.system() == "Windows":
    try:
        import win32gui
        import win32con
        WINDOWS_AVAILABLE = True
    except ImportError:
        WINDOWS_AVAILABLE = False
        print("win32gui not available. Install pywin32 for full always-on-top support")
else:
    WINDOWS_AVAILABLE = False


def set_window_always_on_top(window_title, always_on_top=True):
    """Set a window to always on top (Windows only)"""
    if not WINDOWS_AVAILABLE:
        return False
    
    try:
        hwnd = win32gui.FindWindow(None, window_title)
        if hwnd:
            if always_on_top:
                win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                                    win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
            else:
                win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0,
                                    win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
            return True
    except Exception as e:
        print(f"Error setting window always on top: {e}")
    return False


class FrameCameraController:
    """Modified version of CameraRecorder for GUI integration"""
    
    def __init__(self, status_callback=None):
        self.cam = None
        self.device_info = None
        self.recording_thread = None
        self.preview_thread = None
        self.command_queue = queue.Queue()
        self.frame_queue = queue.Queue(maxsize=5)
        self.is_recording = False
        self.is_grabbing = False
        self.show_preview = False
        self.exit_flag = False
        self.current_filename = None
        self.record_params = None
        self.stats_lock = threading.Lock()
        self.status_callback = status_callback
        self.preview_queue = queue.Queue(maxsize=2)  # Thread-safe preview queue
        
        # Always on top state (now for external preview option)
        self.preview_always_on_top = False
        
        self.stats = {
            'frames_captured': 0,
            'frames_displayed': 0,
            'recording_start_time': None,
            'last_fps': 0.0
        }
        
        # For pixel format conversion
        self.convert_param = MV_CC_PIXEL_CONVERT_PARAM()
        self.rgb_buffer = None
        self.rgb_buffer_size = 0
    
    def find_cameras(self):
        """Find available frame cameras"""
        if not FRAME_CAMERA_AVAILABLE:
            return []
        
        try:
            # Initialize SDK
            MvCamera.MV_CC_Initialize()
        except:
            pass
        
        dev_list = MV_CC_DEVICE_INFO_LIST()
        layers = (MV_GIGE_DEVICE | MV_USB_DEVICE | MV_GENTL_CAMERALINK_DEVICE | 
                 MV_GENTL_CXP_DEVICE | MV_GENTL_XOF_DEVICE)
        
        ret = MvCamera.MV_CC_EnumDevices(layers, dev_list)
        if ret == 0:
            cameras = []
            for i in range(dev_list.nDeviceNum):
                device_info = cast(dev_list.pDeviceInfo[i], POINTER(MV_CC_DEVICE_INFO)).contents
                name = self._get_device_name(device_info)
                cameras.append((i, name, device_info))
            return cameras
        return []
    
    def _get_device_name(self, device_info):
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
            return "Unknown_Device"
        
        return bytes(raw).split(b'\x00', 1)[0].decode(errors='ignore')
    
    def connect_camera(self, device_info):
        """Connect to a specific camera"""
        if not FRAME_CAMERA_AVAILABLE:
            return False
            
        try:
            # Force disconnect any existing camera first
            self.force_disconnect()
            
            # Initialize SDK if not already done
            try:
                MvCamera.MV_CC_Initialize()
            except:
                pass
            
            self.cam = MvCamera()
            self.device_info = device_info
            
            # Create handle
            if self.cam.MV_CC_CreateHandle(device_info) != 0:
                return False
            
            # Open device
            if self.cam.MV_CC_OpenDevice(MV_ACCESS_Exclusive, 0) != 0:
                self.cam.MV_CC_DestroyHandle()
                return False
            
            # For GigE, set optimal packet size
            if device_info.nTLayerType == MV_GIGE_DEVICE:
                pkt = self.cam.MV_CC_GetOptimalPacketSize()
                if pkt > 0:
                    self.cam.MV_CC_SetIntValue("GevSCPSPacketSize", pkt)
            
            # Turn off trigger mode
            self.cam.MV_CC_SetEnumValue("TriggerMode", MV_TRIGGER_MODE_OFF)
            
            # Setup recording parameters
            self._setup_recording_params()
            
            self._notify_status("Frame camera connected")
            return True
            
        except Exception as e:
            self._notify_status(f"Frame camera connection failed: {e}")
            return False
    
    def disconnect_camera(self):
        """Disconnect camera gracefully"""
        self.force_disconnect()
        self._notify_status("Frame camera disconnected")
    
    def force_disconnect(self):
        """Force disconnect with brutal cleanup"""
        try:
            # Stop all operations first
            self.stop_grabbing()
            
            # Give threads time to finish
            time.sleep(0.1)
            
            # Force close camera
            if self.cam:
                try:
                    self.cam.MV_CC_CloseDevice()
                except:
                    pass
                try:
                    self.cam.MV_CC_DestroyHandle()
                except:
                    pass
                self.cam = None
            
            # Reset all flags
            self.device_info = None
            self.is_recording = False
            self.is_grabbing = False
            self.show_preview = False
            self.exit_flag = True
            
            # Clear queues
            while not self.command_queue.empty():
                try:
                    self.command_queue.get_nowait()
                except:
                    break
            while not self.frame_queue.empty():
                try:
                    self.frame_queue.get_nowait()
                except:
                    break
            while not self.preview_queue.empty():
                try:
                    self.preview_queue.get_nowait()
                except:
                    break
                    
        except Exception as e:
            print(f"Error in force disconnect: {e}")
    
    def _setup_recording_params(self):
        """Setup recording parameters"""
        if not self.cam:
            return
            
        record_param = MV_CC_RECORD_PARAM()
        memset(byref(record_param), 0, sizeof(MV_CC_RECORD_PARAM))
        
        # Get camera parameters
        st_param = MVCC_INTVALUE()
        memset(byref(st_param), 0, sizeof(MVCC_INTVALUE))
        
        # Width
        ret = self.cam.MV_CC_GetIntValue("Width", st_param)
        if ret == 0:
            record_param.nWidth = st_param.nCurValue
        
        # Height
        ret = self.cam.MV_CC_GetIntValue("Height", st_param)
        if ret == 0:
            record_param.nHeight = st_param.nCurValue
        
        # Pixel format
        st_enum_value = MVCC_ENUMVALUE()
        memset(byref(st_enum_value), 0, sizeof(MVCC_ENUMVALUE))
        ret = self.cam.MV_CC_GetEnumValue("PixelFormat", st_enum_value)
        if ret == 0:
            record_param.enPixelType = MvGvspPixelType(st_enum_value.nCurValue)
        
        # Frame rate
        st_float_value = MVCC_FLOATVALUE()
        memset(byref(st_float_value), 0, sizeof(MVCC_FLOATVALUE))
        ret = self.cam.MV_CC_GetFloatValue("ResultingFrameRate", st_float_value)
        if ret != 0:
            ret = self.cam.MV_CC_GetFloatValue("AcquisitionFrameRate", st_float_value)
            if ret != 0:
                st_float_value.fCurValue = 30.0
        record_param.fFrameRate = st_float_value.fCurValue
        
        record_param.nBitRate = 5000
        record_param.enRecordFmtType = MV_FormatType_AVI
        
        # Setup RGB buffer
        self.rgb_buffer_size = record_param.nWidth * record_param.nHeight * 3
        self.rgb_buffer = (c_ubyte * self.rgb_buffer_size)()
        
        self.record_params = record_param
    
    def start_grabbing(self):
        """Start grabbing frames"""
        if not self.cam or self.is_grabbing:
            return self.is_grabbing
            
        ret = self.cam.MV_CC_StartGrabbing()
        if ret == 0:
            self.is_grabbing = True
            self.exit_flag = False
            self.recording_thread = threading.Thread(target=self._recording_worker, daemon=True)
            self.recording_thread.start()
            self._notify_status("Frame grabbing started")
            return True
        else:
            self._notify_status(f"Failed to start grabbing: 0x{ret:08x}")
            return False
    
    def stop_grabbing(self):
        """Stop grabbing frames"""
        if self.is_grabbing:
            if self.is_recording:
                self.stop_recording()
            
            self.stop_preview()
            self.exit_flag = True
            
            if self.recording_thread:
                self.recording_thread.join(timeout=2.0)
            
            try:
                self.cam.MV_CC_StopGrabbing()
            except:
                pass
            self.is_grabbing = False
            self._notify_status("Frame grabbing stopped")
    
    def start_recording(self, filename=None):
        """Start recording"""
        # Auto-start grabbing if needed
        if not self.is_grabbing:
            if not self.start_grabbing():
                return False
        
        if not filename:
            device_name = self._get_device_name(self.device_info).replace(" ", "_")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{device_name}_{timestamp}.avi"
        
        self.current_filename = filename
        self.command_queue.put(('START_RECORDING', filename))
        return True
    
    def stop_recording(self):
        """Stop recording"""
        self.command_queue.put(('STOP_RECORDING',))
    
    def start_preview(self):
        """Start preview with auto-start grabbing"""
        # Auto-start grabbing if needed
        if not self.is_grabbing:
            if not self.start_grabbing():
                return False
            
        if not self.show_preview:
            self.show_preview = True
            self.preview_thread = threading.Thread(target=self._preview_worker, daemon=True)
            self.preview_thread.start()
            return True
        return False
    
    def stop_preview(self):
        """Stop preview"""
        if self.show_preview:
            self.show_preview = False
            if self.preview_thread:
                self.preview_thread.join(timeout=2.0)
            # Send None to clear preview
            try:
                self.preview_queue.put_nowait(None)
            except:
                pass
    
    def set_preview_callback(self, callback):
        """Set callback for embedded preview updates"""
        self.preview_callback = callback
    
    def toggle_preview_always_on_top(self):
        """Toggle always on top for preview window (now creates external window)"""
        if not self.show_preview:
            self._notify_status("Start preview first to use external window")
            return
        
        self.preview_always_on_top = not self.preview_always_on_top
        if self.preview_always_on_top:
            # Switch to external window
            self._notify_status("Switching to external frame preview window")
            self._create_external_preview()
        else:
            # Switch back to embedded
            self._notify_status("Switching to embedded frame preview")
            self._close_external_preview()
    
    def _create_external_preview(self):
        """Create external OpenCV preview window"""
        if hasattr(self, 'external_preview_active') and self.external_preview_active:
            return
        
        self.external_preview_active = True
        threading.Thread(target=self._external_preview_worker, daemon=True).start()
    
    def _close_external_preview(self):
        """Close external preview window"""
        if hasattr(self, 'external_preview_active'):
            self.external_preview_active = False
        try:
            cv2.destroyWindow("Frame Camera Preview (External)")
        except:
            pass
    
    def _external_preview_worker(self):
        """External preview worker thread"""
        window_name = "Frame Camera Preview (External)"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        
        if WINDOWS_AVAILABLE:
            time.sleep(0.1)
            set_window_always_on_top(window_name, True)
        
        self._notify_status("External frame preview: Press ESC to close, 'T' to return to embedded")
        
        while (hasattr(self, 'external_preview_active') and self.external_preview_active and 
               not self.exit_flag and self.show_preview):
            try:
                frame = self.frame_queue.get(timeout=0.1)
                
                # Add overlay text
                overlay_frame = frame.copy()
                status_text = "External Preview - Press 'T' to return to embedded, ESC to close"
                cv2.putText(overlay_frame, status_text, (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                
                cv2.imshow(window_name, overlay_frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == 27:  # ESC
                    self.external_preview_active = False
                    break
                elif key == ord('t') or key == ord('T'):  # Return to embedded
                    self.preview_always_on_top = False
                    self.external_preview_active = False
                    self._notify_status("Returned to embedded frame preview")
                    break
                    
            except queue.Empty:
                if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
                    self.external_preview_active = False
                    break
            except Exception as e:
                break
        
        cv2.destroyWindow(window_name)
        self.external_preview_active = False
    
    def get_exposure_range(self):
        """Get exposure time range"""
        if not self.cam:
            return None
        
        st_float = MVCC_FLOATVALUE()
        memset(byref(st_float), 0, sizeof(MVCC_FLOATVALUE))
        ret = self.cam.MV_CC_GetFloatValue("ExposureTime", st_float)
        if ret == 0:
            return (st_float.fMin, st_float.fMax, st_float.fCurValue)
        return None
    
    def set_exposure(self, value):
        """Set exposure time"""
        if not self.cam:
            return False
        
        self.cam.MV_CC_SetEnumValue("ExposureAuto", 0)
        ret = self.cam.MV_CC_SetFloatValue("ExposureTime", float(value))
        return ret == 0
    
    def get_gain_range(self):
        """Get gain range"""
        if not self.cam:
            return None
        
        st_float = MVCC_FLOATVALUE()
        memset(byref(st_float), 0, sizeof(MVCC_FLOATVALUE))
        ret = self.cam.MV_CC_GetFloatValue("Gain", st_float)
        if ret == 0:
            return (st_float.fMin, st_float.fMax, st_float.fCurValue)
        return None
    
    def set_gain(self, value):
        """Set gain"""
        if not self.cam:
            return False
        
        self.cam.MV_CC_SetEnumValue("GainAuto", 0)
        ret = self.cam.MV_CC_SetFloatValue("Gain", float(value))
        return ret == 0
    
    def _recording_worker(self):
        """Recording worker thread"""
        frame_out = MV_FRAME_OUT()
        memset(byref(frame_out), 0, sizeof(frame_out))
        
        input_frame_info = MV_CC_INPUT_FRAME_INFO()
        memset(byref(input_frame_info), 0, sizeof(MV_CC_INPUT_FRAME_INFO))
        
        while not self.exit_flag:
            # Process commands
            try:
                cmd_data = self.command_queue.get_nowait()
                cmd = cmd_data[0]
                
                if cmd == 'START_RECORDING':
                    filename = cmd_data[1]
                    if not self.is_recording and self.is_grabbing:
                        self.record_params.strFilePath = filename.encode('ascii')
                        ret = self.cam.MV_CC_StartRecord(self.record_params)
                        if ret == 0:
                            self.is_recording = True
                            with self.stats_lock:
                                self.stats['frames_captured'] = 0
                                self.stats['recording_start_time'] = time.time()
                            self._notify_status(f"Recording started: {filename}")
                
                elif cmd == 'STOP_RECORDING':
                    if self.is_recording:
                        ret = self.cam.MV_CC_StopRecord()
                        if ret == 0:
                            self.is_recording = False
                            self._notify_status("Recording stopped")
            except queue.Empty:
                pass
            
            # Capture frames
            if self.is_grabbing:
                ret = self.cam.MV_CC_GetImageBuffer(frame_out, 100)
                if frame_out.pBufAddr and ret == 0:
                    if self.is_recording:
                        input_frame_info.pData = cast(frame_out.pBufAddr, POINTER(c_ubyte))
                        input_frame_info.nDataLen = frame_out.stFrameInfo.nFrameLen
                        
                        ret = self.cam.MV_CC_InputOneFrame(input_frame_info)
                        if ret == 0:
                            with self.stats_lock:
                                self.stats['frames_captured'] += 1
                    
                    if self.show_preview:
                        img = self._convert_to_display_format(frame_out.stFrameInfo, frame_out.pBufAddr)
                        if img is not None:
                            try:
                                self.frame_queue.put_nowait(img)
                            except queue.Full:
                                pass
                    
                    self.cam.MV_CC_FreeImageBuffer(frame_out)
            else:
                time.sleep(0.01)
    
    def _preview_worker(self):
        """Preview worker thread - now uses embedded preview with thread-safe updates"""
        self._notify_status("Frame preview started (embedded mode)")
        
        while not self.exit_flag and self.show_preview:
            try:
                frame = self.frame_queue.get(timeout=0.1)
                
                # Send frame to preview queue for thread-safe GUI update
                try:
                    self.preview_queue.put_nowait(frame)
                except queue.Full:
                    # Remove old frame and add new one
                    try:
                        self.preview_queue.get_nowait()
                        self.preview_queue.put_nowait(frame)
                    except:
                        pass
                    
            except queue.Empty:
                continue
            except Exception as e:
                break
        
        # Send None to clear preview when stopped
        try:
            self.preview_queue.put_nowait(None)
        except:
            pass
        
        self._notify_status("Frame preview stopped")
    
    def _convert_to_display_format(self, frame_info, raw_data):
        """Convert raw camera data to displayable format"""
        memset(byref(self.convert_param), 0, sizeof(self.convert_param))
        self.convert_param.nWidth = frame_info.nWidth
        self.convert_param.nHeight = frame_info.nHeight
        self.convert_param.pSrcData = raw_data
        self.convert_param.nSrcDataLen = frame_info.nFrameLen
        self.convert_param.enSrcPixelType = frame_info.enPixelType
        self.convert_param.enDstPixelType = PixelType_Gvsp_RGB8_Packed
        self.convert_param.pDstBuffer = self.rgb_buffer
        self.convert_param.nDstBufferSize = self.rgb_buffer_size
        
        ret = self.cam.MV_CC_ConvertPixelType(self.convert_param)
        if ret != 0:
            return None
        
        img_buff = np.frombuffer(self.rgb_buffer, dtype=np.uint8, count=self.convert_param.nDstLen)
        img = img_buff.reshape((frame_info.nHeight, frame_info.nWidth, 3))
        img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        
        return img_bgr
    
    def _notify_status(self, message):
        """Notify status callback"""
        if self.status_callback:
            self.status_callback(f"Frame: {message}")
    
    def get_status(self):
        """Get current status"""
        with self.stats_lock:
            return {
                'connected': self.cam is not None,
                'grabbing': self.is_grabbing,
                'recording': self.is_recording,
                'previewing': self.show_preview,
                'frames_captured': self.stats['frames_captured'],
                'fps': self.stats['last_fps']
            }


class EventCameraController:
    """Modified version of EventCameraRecorder for GUI integration - simplified connection like old working code"""
    
    def __init__(self, status_callback=None):
        self.device = None
        self.mv_iterator = None
        self.height = None
        self.width = None
        
        self.is_recording = False
        self.should_exit = False
        self.visualization_running = False
        self.capturing = False
        
        self.record_lock = threading.Lock()
        self.event_queue = queue.Queue(maxsize=1000)
        self.status_callback = status_callback
        self.preview_queue = queue.Queue(maxsize=2)  # Thread-safe preview queue
        
        self.current_log_path = None
        
        # Threads
        self.event_thread = None
        self.viz_thread = None
        
        # Window reference for external preview
        self.window = None
        self.window_always_on_top = False
        self.external_preview_active = False
    
    def find_cameras(self):
        """Find available event cameras - simplified approach"""
        if not EVENT_CAMERA_AVAILABLE:
            return []
        
        # Don't actually try to enumerate - just return a placeholder
        # The actual connection test will happen in connect_camera()
        return [(0, "Event Camera (Auto-detect)", "")]
    
    def connect_camera(self, device_path=""):
        """Connect to event camera - using simple approach from old working code"""
        if not EVENT_CAMERA_AVAILABLE:
            self._notify_status("Event camera SDK not available")
            return False
        
        try:
            self._notify_status("Connecting to event camera...")
            
            # Simple cleanup first
            self.stop_all()
            
            # Use the exact same approach as the old working code
            self.device = initiate_device("")
            
            if self.device is None:
                self._notify_status("Event camera connection failed: initiate_device returned None")
                return False
            
            # Test the connection by creating iterator - exactly like old code
            self.mv_iterator = EventsIterator.from_device(device=self.device, delta_t=1000)
            self.height, self.width = self.mv_iterator.get_size()
            
            self._notify_status(f"Event camera connected successfully: {self.width}x{self.height}")
            return True
            
        except Exception as e:
            self._notify_status(f"Event camera connection failed: {e}")
            # Clean up failed attempt
            try:
                if self.device:
                    self.device = None
                self.mv_iterator = None
            except:
                pass
            return False
    
    def disconnect_camera(self):
        """Disconnect camera gracefully"""
        self.stop_all()
        self.device = None
        self.mv_iterator = None
        self._notify_status("Event camera disconnected")
    
    def start_capture(self):
        """Start capturing events"""
        if not self.device or self.capturing:
            return self.capturing
        
        self.should_exit = False
        self.capturing = True
        self.event_thread = threading.Thread(target=self._event_processing_thread, daemon=True)
        self.event_thread.start()
        self._notify_status("Event capture started")
        return True
    
    def stop_capture(self):
        """Stop capturing events"""
        if self.capturing:
            self.should_exit = True
            self.capturing = False
            if self.event_thread:
                self.event_thread.join(timeout=2.0)
            self._notify_status("Event capture stopped")
    
    def start_recording(self, output_dir="", filename_prefix=""):
        """Start recording events"""
        # Auto-start capture if needed
        if not self.capturing:
            if not self.start_capture():
                return False
        
        with self.record_lock:
            if self.is_recording:
                return False
            
            if self.device and self.device.get_i_events_stream():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                if filename_prefix:
                    self.current_log_path = f"{filename_prefix}_{timestamp}.raw"
                else:
                    self.current_log_path = f"recording_{timestamp}.raw"
                
                if output_dir:
                    self.current_log_path = os.path.join(output_dir, self.current_log_path)
                
                self.device.get_i_events_stream().log_raw_data(self.current_log_path)
                self.is_recording = True
                self._notify_status(f"Recording started: {self.current_log_path}")
                return True
        return False
    
    def stop_recording(self):
        """Stop recording events"""
        with self.record_lock:
            if not self.is_recording:
                return False
            
            try:
                self.device.get_i_events_stream().stop_log_raw_data()
            except:
                pass
            self.is_recording = False
            self._notify_status(f"Recording stopped: {self.current_log_path}")
            return True
    
    def start_visualization(self):
        """Start event visualization with auto-start capture"""
        # Auto-start capture if needed
        if not self.capturing:
            if not self.start_capture():
                return False
        
        if not self.device or self.visualization_running:
            return False
        
        self.viz_thread = threading.Thread(target=self._visualization_thread, daemon=True)
        self.viz_thread.start()
        return True
    
    def stop_visualization(self):
        """Stop visualization"""
        if self.visualization_running:
            self.visualization_running = False
            
            # Force close window
            if self.window:
                try:
                    self.window.set_close_flag()
                except:
                    pass
                self.window = None
            
            if self.viz_thread:
                self.viz_thread.join(timeout=3.0)
            
            # Send None to clear preview
            try:
                self.preview_queue.put_nowait(None)
            except:
                pass
    
    def set_preview_callback(self, callback):
        """Set callback for embedded preview updates"""
        self.preview_callback = callback
    
    def toggle_visualization_always_on_top(self):
        """Toggle always on top for visualization window (now creates external window)"""
        if not self.visualization_running:
            self._notify_status("Start visualization first to use external window")
            return
        
        self.window_always_on_top = not self.window_always_on_top
        if self.window_always_on_top:
            # Switch to external window
            self._notify_status("Switching to external event preview window")
            self._create_external_visualization()
        else:
            # Switch back to embedded
            self._notify_status("Switching to embedded event preview")
            self._close_external_visualization()
    
    def _create_external_visualization(self):
        """Create external MTWindow for visualization"""
        if self.external_preview_active:
            return
        
        self.external_preview_active = True
        threading.Thread(target=self._external_visualization_worker, daemon=True).start()
    
    def _close_external_visualization(self):
        """Close external visualization window"""
        self.external_preview_active = False
        if self.window:
            try:
                self.window.set_close_flag()
            except:
                pass
            self.window = None
    
    def _external_visualization_worker(self):
        """External visualization worker using MTWindow"""
        try:
            event_frame_gen = PeriodicFrameGenerationAlgorithm(
                sensor_width=self.width, sensor_height=self.height, 
                fps=25, palette=ColorPalette.Dark
            )
            
            with MTWindow(title="Event Camera Preview (External)", width=self.width, height=self.height,
                         mode=BaseWindow.RenderMode.BGR) as window:
                
                self.window = window
                
                if WINDOWS_AVAILABLE:
                    time.sleep(0.2)
                    set_window_always_on_top("Event Camera Preview (External)", True)
                
                def keyboard_cb(key, scancode, action, mods):
                    if action != UIAction.RELEASE:
                        return
                    if key == UIKeyEvent.KEY_ESCAPE or key == UIKeyEvent.KEY_Q:
                        window.set_close_flag()
                    elif key == UIKeyEvent.KEY_T:
                        # Return to embedded
                        self.window_always_on_top = False
                        self.external_preview_active = False
                        window.set_close_flag()
                
                window.set_keyboard_callback(keyboard_cb)
                
                def on_cd_frame_cb(ts, cd_frame):
                    overlay_frame = cd_frame.copy()
                    status_text = "External Preview - Press 'T' to return to embedded, ESC to close"
                    cv2.putText(overlay_frame, status_text, (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                    window.show_async(overlay_frame)
                
                event_frame_gen.set_output_callback(on_cd_frame_cb)
                
                self._notify_status("External event visualization started - Press 'T' to return to embedded")
                
                while (not self.should_exit and self.visualization_running and 
                       self.external_preview_active):
                    if window.should_close():
                        break
                    
                    try:
                        evs = self.event_queue.get(timeout=0.01)
                        EventLoop.poll_and_dispatch()
                        event_frame_gen.process_events(evs)
                    except queue.Empty:
                        EventLoop.poll_and_dispatch()
                    except Exception as e:
                        break
            
        except Exception as e:
            self._notify_status(f"External visualization error: {e}")
        finally:
            self.external_preview_active = False
            self.window = None
            self._notify_status("External event visualization stopped")
    
    def stop_all(self):
        """Stop all operations"""
        if self.is_recording:
            self.stop_recording()
        self.stop_visualization()
        self.stop_capture()
    
    def get_bias_values(self):
        """Get current bias values"""
        if not self.device:
            return {}
        
        bias_interface = self.device.get_i_ll_biases()
        if bias_interface is None:
            return {}
        
        try:
            return bias_interface.get_all_biases()
        except:
            return {}
    
    def set_bias_value(self, bias_name, value):
        """Set a bias value"""
        if not self.device:
            return False
        
        bias_interface = self.device.get_i_ll_biases()
        if bias_interface is None:
            return False
        
        try:
            bias_interface.set(bias_name, int(value))
            return True
        except:
            return False
    
    def _event_processing_thread(self):
        """Thread for reading events from camera - exactly like old working code"""
        try:
            for evs in self.mv_iterator:
                if self.should_exit:
                    break
                
                try:
                    self.event_queue.put(evs, block=False)
                except queue.Full:
                    pass
                
                if self.should_exit:
                    break
        except Exception as e:
            self._notify_status(f"Event processing error: {e}")
        finally:
            self.capturing = False
    
    def _visualization_thread(self):
        """Thread for event visualization - now uses embedded preview with thread-safe updates"""
        try:
            event_frame_gen = PeriodicFrameGenerationAlgorithm(
                sensor_width=self.width, sensor_height=self.height, 
                fps=25, palette=ColorPalette.Dark
            )
            
            self.visualization_running = True
            self._notify_status("Event visualization started (embedded mode)")
            
            def on_cd_frame_cb(ts, cd_frame):
                # Send frame to preview queue for thread-safe GUI update
                try:
                    self.preview_queue.put_nowait(cd_frame)
                except queue.Full:
                    # Remove old frame and add new one
                    try:
                        self.preview_queue.get_nowait()
                        self.preview_queue.put_nowait(cd_frame)
                    except:
                        pass
            
            event_frame_gen.set_output_callback(on_cd_frame_cb)
            
            # Simple event loop for embedded preview
            while not self.should_exit and self.visualization_running:
                try:
                    evs = self.event_queue.get(timeout=0.01)
                    event_frame_gen.process_events(evs)
                except queue.Empty:
                    continue
                except Exception as e:
                    break
            
        except Exception as e:
            self._notify_status(f"Visualization error: {e}")
        finally:
            self.visualization_running = False
            # Send None to clear preview when stopped
            try:
                self.preview_queue.put_nowait(None)
            except:
                pass
            self._notify_status("Event visualization stopped")
    
    def _notify_status(self, message):
        """Notify status callback"""
        if self.status_callback:
            self.status_callback(f"Event: {message}")
    
    def get_status(self):
        """Get current status"""
        return {
            'connected': self.device is not None,
            'capturing': self.capturing,
            'recording': self.is_recording,
            'visualizing': self.visualization_running
        }


class DualCameraGUI:
    """Main GUI application"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Dual Camera Control System")
        
        # Use full screen width with better sizing
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        main_width = screen_width - 100  # Leave small margin
        main_height = screen_height - 100  # Leave space for taskbar
        self.root.geometry(f"{main_width}x{main_height}+50+50")
        
        # Camera controllers
        self.frame_camera = FrameCameraController(self.update_status)
        self.event_camera = EventCameraController(self.update_status)
        
        # GUI variables
        self.frame_cameras_list = []
        self.event_cameras_list = []
        
        # Status update queue
        self.status_queue = queue.Queue()
        
        # Parameter variables for text boxes
        self.exposure_text_var = tk.StringVar()
        self.gain_text_var = tk.StringVar()
        self.bias_text_vars = {}
        
        # Filename prefix variable
        self.filename_prefix_var = tk.StringVar()
        self.filename_prefix_var.set("sync_recording")
        
        # Unified control flags
        self.unified_preview_active = False
        self.unified_recording_active = False
        
        self.create_widgets()
        self.setup_status_update()
        self.setup_preview_updates()  # Setup thread-safe preview updates
        
        # Auto-scan for cameras
        self.scan_cameras()
    
    def create_widgets(self):
        """Create GUI widgets with draggable splitter and embedded preview areas"""
        # Create main paned window for draggable splitter
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left side: Controls (scrollable) - initially 40% of width
        controls_frame = ttk.Frame(main_paned)
        main_paned.add(controls_frame, weight=2)  # 40% of space
        
        # Create scrollable area for controls
        controls_canvas = tk.Canvas(controls_frame)
        controls_scrollbar = ttk.Scrollbar(controls_frame, orient="vertical", command=controls_canvas.yview)
        scrollable_controls = ttk.Frame(controls_canvas)
        
        scrollable_controls.bind(
            "<Configure>",
            lambda e: controls_canvas.configure(scrollregion=controls_canvas.bbox("all"))
        )
        
        controls_canvas.create_window((0, 0), window=scrollable_controls, anchor="nw")
        controls_canvas.configure(yscrollcommand=controls_scrollbar.set)
        
        controls_canvas.pack(side="left", fill="both", expand=True)
        controls_scrollbar.pack(side="right", fill="y")
        
        # Right side: Preview areas - initially 60% of width
        preview_frame = ttk.Frame(main_paned)
        main_paned.add(preview_frame, weight=3)  # 60% of space
        
        # Create vertical paned window for preview areas
        preview_paned = ttk.PanedWindow(preview_frame, orient=tk.VERTICAL)
        preview_paned.pack(fill=tk.BOTH, expand=True)
        
        # Event camera preview (top right)
        self.event_preview_frame = ttk.LabelFrame(preview_paned, text="Event Camera Preview")
        preview_paned.add(self.event_preview_frame, weight=1)
        
        self.event_preview_label = ttk.Label(self.event_preview_frame, text="Event preview will appear here\nStart visualization to see camera feed", 
                                           justify=tk.CENTER, background='black', foreground='white')
        self.event_preview_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame camera preview (bottom right)
        self.frame_preview_frame = ttk.LabelFrame(preview_paned, text="Frame Camera Preview")
        preview_paned.add(self.frame_preview_frame, weight=1)
        
        self.frame_preview_label = ttk.Label(self.frame_preview_frame, text="Frame preview will appear here\nStart preview to see camera feed", 
                                           justify=tk.CENTER, background='black', foreground='white')
        self.frame_preview_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create control sections in scrollable area
        # Filename prefix section
        prefix_section = ttk.LabelFrame(scrollable_controls, text="Recording Settings")
        prefix_section.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(prefix_section, text="Filename Prefix:").grid(row=0, column=0, padx=5, pady=5)
        prefix_entry = ttk.Entry(prefix_section, textvariable=self.filename_prefix_var, width=30)
        prefix_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        prefix_section.columnconfigure(1, weight=1)
        
        # Frame camera section
        frame_section = ttk.LabelFrame(scrollable_controls, text="Frame Camera")
        frame_section.pack(fill=tk.X, padx=5, pady=5)
        self.create_frame_camera_section(frame_section)
        
        # Event camera section
        event_section = ttk.LabelFrame(scrollable_controls, text="Event Camera")
        event_section.pack(fill=tk.X, padx=5, pady=5)
        self.create_event_camera_section(event_section)
        
        # Unified controls section
        unified_section = ttk.LabelFrame(scrollable_controls, text="Unified Controls")
        unified_section.pack(fill=tk.X, padx=5, pady=5)
        self.create_unified_controls_section(unified_section)
        
        # Preview controls section
        aot_section = ttk.LabelFrame(scrollable_controls, text="Preview Controls")
        aot_section.pack(fill=tk.X, padx=5, pady=5)
        self.create_always_on_top_section(aot_section)
        
        # Status section
        status_section = ttk.LabelFrame(scrollable_controls, text="Status Log")
        status_section.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.create_status_section(status_section)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready - Drag the splitter to resize preview areas")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def setup_preview_updates(self):
        """Setup thread-safe preview updates"""
        def update_previews():
            # Update frame camera preview
            try:
                while True:
                    frame = self.frame_camera.preview_queue.get_nowait()
                    self.update_frame_preview(frame)
            except queue.Empty:
                pass
            
            # Update event camera preview
            try:
                while True:
                    frame = self.event_camera.preview_queue.get_nowait()
                    self.update_event_preview(frame)
            except queue.Empty:
                pass
            
            # Schedule next update
            self.root.after(50, update_previews)  # 20 FPS max for GUI updates
        
        # Start the preview update loop
        update_previews()
    
    def update_frame_preview(self, frame):
        """Update frame camera preview in GUI - thread-safe"""
        try:
            if frame is not None and PIL_AVAILABLE:
                # Convert OpenCV frame to tkinter format
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Get preview label dimensions
                label_width = self.frame_preview_label.winfo_width()
                label_height = self.frame_preview_label.winfo_height()
                
                if label_width > 1 and label_height > 1:  # Valid dimensions
                    # Resize frame to fit label while maintaining aspect ratio
                    h, w = frame_rgb.shape[:2]
                    aspect = w / h
                    
                    if label_width / label_height > aspect:
                        new_height = label_height - 10
                        new_width = int(new_height * aspect)
                    else:
                        new_width = label_width - 10
                        new_height = int(new_width / aspect)
                    
                    frame_resized = cv2.resize(frame_rgb, (new_width, new_height))
                    
                    # Convert to PIL and then to tkinter
                    pil_image = Image.fromarray(frame_resized)
                    tk_image = ImageTk.PhotoImage(pil_image)
                    
                    # Update label
                    self.frame_preview_label.configure(image=tk_image, text="")
                    self.frame_preview_label.image = tk_image  # Keep a reference
            elif frame is None:
                # Clear preview
                self.frame_preview_label.configure(image="", text="Frame preview stopped\nStart preview to see camera feed")
                self.frame_preview_label.image = None
        except Exception as e:
            pass  # Silently handle errors to avoid spam
    
    def update_event_preview(self, frame):
        """Update event camera preview in GUI - thread-safe"""
        try:
            if frame is not None and PIL_AVAILABLE:
                # Get preview label dimensions
                label_width = self.event_preview_label.winfo_width()
                label_height = self.event_preview_label.winfo_height()
                
                if label_width > 1 and label_height > 1:  # Valid dimensions
                    # Resize frame to fit label while maintaining aspect ratio
                    h, w = frame.shape[:2]
                    aspect = w / h
                    
                    if label_width / label_height > aspect:
                        new_height = label_height - 10
                        new_width = int(new_height * aspect)
                    else:
                        new_width = label_width - 10
                        new_height = int(new_width / aspect)
                    
                    frame_resized = cv2.resize(frame, (new_width, new_height))
                    
                    # Convert BGR to RGB for PIL
                    frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
                    
                    # Convert to PIL and then to tkinter
                    pil_image = Image.fromarray(frame_rgb)
                    tk_image = ImageTk.PhotoImage(pil_image)
                    
                    # Update label
                    self.event_preview_label.configure(image=tk_image, text="")
                    self.event_preview_label.image = tk_image  # Keep a reference
            elif frame is None:
                # Clear preview
                self.event_preview_label.configure(image="", text="Event preview stopped\nStart visualization to see camera feed")
                self.event_preview_label.image = None
        except Exception as e:
            pass  # Silently handle errors to avoid spam
    
    def create_frame_camera_section(self, parent):
        """Create frame camera control section"""
        # Connection frame
        conn_frame = ttk.LabelFrame(parent, text="Connection")
        conn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(conn_frame, text="Camera:").grid(row=0, column=0, padx=5, pady=5)
        self.frame_camera_var = tk.StringVar()
        self.frame_camera_combo = ttk.Combobox(conn_frame, textvariable=self.frame_camera_var, state="readonly")
        self.frame_camera_combo.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Button(conn_frame, text="Scan", command=self.scan_cameras).grid(row=0, column=2, padx=5, pady=5)
        self.frame_connect_btn = ttk.Button(conn_frame, text="Connect", command=self.connect_frame_camera)
        self.frame_connect_btn.grid(row=0, column=3, padx=5, pady=5)
        
        conn_frame.columnconfigure(1, weight=1)
        
        # Control frame
        control_frame = ttk.LabelFrame(parent, text="Individual Controls")
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.frame_grab_btn = ttk.Button(control_frame, text="Start Grabbing", command=self.toggle_frame_grabbing)
        self.frame_grab_btn.grid(row=0, column=0, padx=5, pady=5)
        
        self.frame_preview_btn = ttk.Button(control_frame, text="Start Preview", command=self.toggle_frame_preview)
        self.frame_preview_btn.grid(row=0, column=1, padx=5, pady=5)
        
        self.frame_record_btn = ttk.Button(control_frame, text="Start Recording", command=self.toggle_frame_recording)
        self.frame_record_btn.grid(row=0, column=2, padx=5, pady=5)
        
        # Parameters frame
        param_frame = ttk.LabelFrame(parent, text="Parameters")
        param_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Exposure
        ttk.Label(param_frame, text="Exposure (μs):").grid(row=0, column=0, padx=5, pady=5)
        self.exposure_var = tk.DoubleVar()
        self.exposure_scale = ttk.Scale(param_frame, from_=100, to=10000, variable=self.exposure_var, 
                                       orient=tk.HORIZONTAL, command=self.on_exposure_scale_change)
        self.exposure_scale.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        self.exposure_entry = ttk.Entry(param_frame, textvariable=self.exposure_text_var, width=10)
        self.exposure_entry.grid(row=0, column=2, padx=5, pady=5)
        self.exposure_entry.bind('<Return>', self.on_exposure_entry_change)
        self.exposure_entry.bind('<FocusOut>', self.on_exposure_entry_change)
        
        # Gain
        ttk.Label(param_frame, text="Gain (dB):").grid(row=1, column=0, padx=5, pady=5)
        self.gain_var = tk.DoubleVar()
        self.gain_scale = ttk.Scale(param_frame, from_=0, to=20, variable=self.gain_var,
                                   orient=tk.HORIZONTAL, command=self.on_gain_scale_change)
        self.gain_scale.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        self.gain_entry = ttk.Entry(param_frame, textvariable=self.gain_text_var, width=10)
        self.gain_entry.grid(row=1, column=2, padx=5, pady=5)
        self.gain_entry.bind('<Return>', self.on_gain_entry_change)
        self.gain_entry.bind('<FocusOut>', self.on_gain_entry_change)
        
        param_frame.columnconfigure(1, weight=1)
    
    def create_event_camera_section(self, parent):
        """Create event camera control section"""
        # Connection frame
        conn_frame = ttk.LabelFrame(parent, text="Connection")
        conn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(conn_frame, text="Camera:").grid(row=0, column=0, padx=5, pady=5)
        self.event_camera_var = tk.StringVar()
        self.event_camera_combo = ttk.Combobox(conn_frame, textvariable=self.event_camera_var, state="readonly")
        self.event_camera_combo.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        self.event_connect_btn = ttk.Button(conn_frame, text="Connect", command=self.connect_event_camera)
        self.event_connect_btn.grid(row=0, column=2, padx=5, pady=5)
        
        conn_frame.columnconfigure(1, weight=1)
        
        # Control frame
        control_frame = ttk.LabelFrame(parent, text="Individual Controls")
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.event_capture_btn = ttk.Button(control_frame, text="Start Capture", command=self.toggle_event_capture)
        self.event_capture_btn.grid(row=0, column=0, padx=5, pady=5)
        
        self.event_viz_btn = ttk.Button(control_frame, text="Start Visualization", command=self.toggle_event_visualization)
        self.event_viz_btn.grid(row=0, column=1, padx=5, pady=5)
        
        self.event_record_btn = ttk.Button(control_frame, text="Start Recording", command=self.toggle_event_recording)
        self.event_record_btn.grid(row=0, column=2, padx=5, pady=5)
        
        # Bias parameters frame
        bias_frame = ttk.LabelFrame(parent, text="Bias Parameters")
        bias_frame.pack(fill=tk.X, padx=5, pady=5)
        
        bias_names = ['bias_diff', 'bias_diff_off', 'bias_diff_on', 'bias_fo', 'bias_hpf', 'bias_refr']
        self.bias_vars = {}
        self.bias_scales = {}
        self.bias_entries = {}
        
        for i, bias_name in enumerate(bias_names):
            row = i // 2
            col = (i % 2) * 4
            
            ttk.Label(bias_frame, text=f"{bias_name}:").grid(row=row, column=col, padx=5, pady=2)
            var = tk.IntVar()
            scale = ttk.Scale(bias_frame, from_=0, to=255, variable=var, orient=tk.HORIZONTAL,
                             command=lambda val, name=bias_name: self.on_bias_scale_change(name, val))
            scale.grid(row=row, column=col+1, padx=5, pady=2, sticky="ew")
            
            # Text entry for bias
            text_var = tk.StringVar()
            entry = ttk.Entry(bias_frame, textvariable=text_var, width=8)
            entry.grid(row=row, column=col+2, padx=5, pady=2)
            entry.bind('<Return>', lambda e, name=bias_name: self.on_bias_entry_change(name))
            entry.bind('<FocusOut>', lambda e, name=bias_name: self.on_bias_entry_change(name))
            
            self.bias_vars[bias_name] = var
            self.bias_scales[bias_name] = scale
            self.bias_text_vars[bias_name] = text_var
            self.bias_entries[bias_name] = entry
        
        bias_frame.columnconfigure(1, weight=1)
        bias_frame.columnconfigure(5, weight=1)
    
    def create_unified_controls_section(self, parent):
        """Create unified controls section"""
        ttk.Label(parent, text="Control both cameras simultaneously:", 
                 font=('TkDefaultFont', 10, 'bold')).pack(padx=5, pady=5)
        
        controls_frame = ttk.Frame(parent)
        controls_frame.pack(padx=5, pady=5)
        
        self.unified_preview_btn = ttk.Button(controls_frame, text="Start Unified Preview", 
                                             command=self.toggle_unified_preview)
        self.unified_preview_btn.grid(row=0, column=0, padx=10, pady=5)
        
        self.unified_record_btn = ttk.Button(controls_frame, text="Start Unified Recording", 
                                            command=self.toggle_unified_recording)
        self.unified_record_btn.grid(row=0, column=1, padx=10, pady=5)
    
    def create_always_on_top_section(self, parent):
        """Create preview controls section"""
        info_text = "Preview Controls:"
        if not WINDOWS_AVAILABLE:
            info_text += " (Windows only - install pywin32 for external window support)"
        
        ttk.Label(parent, text=info_text, font=('TkDefaultFont', 9)).pack(padx=5, pady=2)
        
        controls_frame = ttk.Frame(parent)
        controls_frame.pack(padx=5, pady=5)
        
        ttk.Button(controls_frame, text="Frame: Switch to External Window", 
                  command=self.frame_camera.toggle_preview_always_on_top).grid(row=0, column=0, padx=5, pady=2)
        
        ttk.Button(controls_frame, text="Event: Switch to External Window", 
                  command=self.event_camera.toggle_visualization_always_on_top).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(parent, text="• Default: Embedded previews in main window\n• External: Separate always-on-top windows", 
                 font=('TkDefaultFont', 8)).pack(padx=5, pady=2)
    
    def create_status_section(self, parent):
        """Create status section"""
        self.status_text = tk.Text(parent, height=12, state=tk.DISABLED)
        status_scroll = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=status_scroll.set)
        
        self.status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        status_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    
    def scan_cameras(self):
        """Scan for available cameras"""
        # Frame cameras
        self.frame_cameras_list = self.frame_camera.find_cameras()
        frame_names = [f"{idx}: {name}" for idx, name, _ in self.frame_cameras_list]
        self.frame_camera_combo['values'] = frame_names
        if frame_names:
            self.frame_camera_combo.current(0)
        
        # Event cameras - simplified approach
        self.event_cameras_list = self.event_camera.find_cameras()
        event_names = [f"{idx}: {name}" for idx, name, _ in self.event_cameras_list]
        self.event_camera_combo['values'] = event_names
        if event_names:
            self.event_camera_combo.current(0)
        
        # Update status
        frame_count = len(self.frame_cameras_list)
        event_count = len(self.event_cameras_list)
        self.update_status(f"Found {frame_count} frame cameras, {event_count} event cameras")
    
    def connect_frame_camera(self):
        """Connect to selected frame camera"""
        if not self.frame_cameras_list:
            messagebox.showerror("Error", "No frame cameras found!")
            return
        
        selected_idx = self.frame_camera_combo.current()
        if selected_idx < 0:
            messagebox.showerror("Error", "Please select a camera!")
            return
        
        idx, name, device_info = self.frame_cameras_list[selected_idx]
        
        if self.frame_camera.connect_camera(device_info):
            self.frame_connect_btn.config(text="Disconnect", command=self.disconnect_frame_camera)
            self.update_frame_parameters()
        else:
            messagebox.showerror("Error", "Failed to connect to frame camera!")
    
    def disconnect_frame_camera(self):
        """Disconnect frame camera"""
        self.frame_camera.disconnect_camera()
        self.frame_connect_btn.config(text="Connect", command=self.connect_frame_camera)
        self.reset_frame_button_states()
    
    def connect_event_camera(self):
        """Connect to event camera - simplified approach"""
        if self.event_camera.connect_camera():
            self.event_connect_btn.config(text="Disconnect", command=self.disconnect_event_camera)
            self.update_event_parameters()
        else:
            messagebox.showerror("Error", "Failed to connect to event camera!")
    
    def disconnect_event_camera(self):
        """Disconnect event camera"""
        self.event_camera.disconnect_camera()
        self.event_connect_btn.config(text="Connect", command=self.connect_event_camera)
        self.reset_event_button_states()
    
    def reset_frame_button_states(self):
        """Reset frame camera button states"""
        self.frame_grab_btn.config(text="Start Grabbing")
        self.frame_preview_btn.config(text="Start Preview")
        self.frame_record_btn.config(text="Start Recording")
    
    def reset_event_button_states(self):
        """Reset event camera button states"""
        self.event_capture_btn.config(text="Start Capture")
        self.event_viz_btn.config(text="Start Visualization")
        self.event_record_btn.config(text="Start Recording")
    
    def update_frame_parameters(self):
        """Update frame camera parameter ranges"""
        exposure_range = self.frame_camera.get_exposure_range()
        if exposure_range:
            min_exp, max_exp, cur_exp = exposure_range
            self.exposure_scale.config(from_=min_exp, to=max_exp)
            self.exposure_var.set(cur_exp)
            self.exposure_text_var.set(f"{cur_exp:.0f}")
        
        gain_range = self.frame_camera.get_gain_range()
        if gain_range:
            min_gain, max_gain, cur_gain = gain_range
            self.gain_scale.config(from_=min_gain, to=max_gain)
            self.gain_var.set(cur_gain)
            self.gain_text_var.set(f"{cur_gain:.1f}")
    
    def update_event_parameters(self):
        """Update event camera bias values"""
        bias_values = self.event_camera.get_bias_values()
        for bias_name, var in self.bias_vars.items():
            if bias_name in bias_values:
                value = bias_values[bias_name]
                var.set(value)
                self.bias_text_vars[bias_name].set(str(value))
    
    def toggle_frame_grabbing(self):
        """Toggle frame grabbing"""
        if not self.frame_camera.is_grabbing:
            if self.frame_camera.start_grabbing():
                self.frame_grab_btn.config(text="Stop Grabbing")
        else:
            self.frame_camera.stop_grabbing()
            self.reset_frame_button_states()
    
    def toggle_frame_preview(self):
        """Toggle frame preview with auto-start grabbing"""
        if not self.frame_camera.show_preview:
            if self.frame_camera.start_preview():
                self.frame_preview_btn.config(text="Stop Preview")
                # Update grabbing button if auto-started
                if self.frame_camera.is_grabbing:
                    self.frame_grab_btn.config(text="Stop Grabbing")
        else:
            self.frame_camera.stop_preview()
            self.frame_preview_btn.config(text="Start Preview")
    
    def toggle_frame_recording(self):
        """Toggle frame recording with auto-start grabbing"""
        if not self.frame_camera.is_recording:
            prefix = self.filename_prefix_var.get()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{prefix}_frame_{timestamp}.avi" if prefix else None
            
            if self.frame_camera.start_recording(filename):
                self.frame_record_btn.config(text="Stop Recording")
                # Update grabbing button if auto-started
                if self.frame_camera.is_grabbing:
                    self.frame_grab_btn.config(text="Stop Grabbing")
        else:
            self.frame_camera.stop_recording()
            self.frame_record_btn.config(text="Start Recording")
    
    def toggle_event_capture(self):
        """Toggle event capture"""
        if not self.event_camera.capturing:
            if self.event_camera.start_capture():
                self.event_capture_btn.config(text="Stop Capture")
        else:
            self.event_camera.stop_capture()
            self.reset_event_button_states()
    
    def toggle_event_visualization(self):
        """Toggle event visualization with auto-start capture"""
        if not self.event_camera.visualization_running:
            if self.event_camera.start_visualization():
                self.event_viz_btn.config(text="Stop Visualization")
                # Update capture button if auto-started
                if self.event_camera.capturing:
                    self.event_capture_btn.config(text="Stop Capture")
        else:
            self.event_camera.stop_visualization()
            self.event_viz_btn.config(text="Start Visualization")
    
    def toggle_event_recording(self):
        """Toggle event recording with auto-start capture"""
        if not self.event_camera.is_recording:
            prefix = self.filename_prefix_var.get()
            if self.event_camera.start_recording(filename_prefix=prefix):
                self.event_record_btn.config(text="Stop Recording")
                # Update capture button if auto-started
                if self.event_camera.capturing:
                    self.event_capture_btn.config(text="Stop Capture")
        else:
            self.event_camera.stop_recording()
            self.event_record_btn.config(text="Start Recording")
    
    def toggle_unified_preview(self):
        """Toggle unified preview for both cameras"""
        if not self.unified_preview_active:
            # Start unified preview
            frame_started = False
            event_started = False
            
            # Start frame camera preview if connected
            if self.frame_camera.cam is not None:
                frame_started = self.frame_camera.start_preview()
                if frame_started:
                    self.frame_preview_btn.config(text="Stop Preview")
                    if self.frame_camera.is_grabbing:
                        self.frame_grab_btn.config(text="Stop Grabbing")
            
            # Start event camera preview if connected
            if self.event_camera.device is not None:
                event_started = self.event_camera.start_visualization()
                if event_started:
                    self.event_viz_btn.config(text="Stop Visualization")
                    if self.event_camera.capturing:
                        self.event_capture_btn.config(text="Stop Capture")
            
            if frame_started or event_started:
                self.unified_preview_active = True
                self.unified_preview_btn.config(text="Stop Unified Preview")
                self.update_status("Unified preview started")
            else:
                self.update_status("No cameras available for unified preview")
        else:
            # Stop unified preview
            if self.frame_camera.show_preview:
                self.frame_camera.stop_preview()
                self.frame_preview_btn.config(text="Start Preview")
            
            if self.event_camera.visualization_running:
                self.event_camera.stop_visualization()
                self.event_viz_btn.config(text="Start Visualization")
            
            self.unified_preview_active = False
            self.unified_preview_btn.config(text="Start Unified Preview")
            self.update_status("Unified preview stopped")
    
    def toggle_unified_recording(self):
        """Toggle unified recording for both cameras"""
        if not self.unified_recording_active:
            # Start unified recording
            frame_started = False
            event_started = False
            prefix = self.filename_prefix_var.get()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Start frame camera recording if connected
            if self.frame_camera.cam is not None:
                filename = f"{prefix}_frame_{timestamp}.avi" if prefix else None
                frame_started = self.frame_camera.start_recording(filename)
                if frame_started:
                    self.frame_record_btn.config(text="Stop Recording")
                    if self.frame_camera.is_grabbing:
                        self.frame_grab_btn.config(text="Stop Grabbing")
            
            # Start event camera recording if connected
            if self.event_camera.device is not None:
                event_started = self.event_camera.start_recording(filename_prefix=f"{prefix}_event" if prefix else "")
                if event_started:
                    self.event_record_btn.config(text="Stop Recording")
                    if self.event_camera.capturing:
                        self.event_capture_btn.config(text="Stop Capture")
            
            if frame_started or event_started:
                self.unified_recording_active = True
                self.unified_record_btn.config(text="Stop Unified Recording")
                self.update_status("Unified recording started")
            else:
                self.update_status("No cameras available for unified recording")
        else:
            # Stop unified recording
            if self.frame_camera.is_recording:
                self.frame_camera.stop_recording()
                self.frame_record_btn.config(text="Start Recording")
            
            if self.event_camera.is_recording:
                self.event_camera.stop_recording()
                self.event_record_btn.config(text="Start Recording")
            
            self.unified_recording_active = False
            self.unified_record_btn.config(text="Start Unified Recording")
            self.update_status("Unified recording stopped")
    
    def on_exposure_scale_change(self, value):
        """Handle exposure scale change"""
        exposure = float(value)
        self.exposure_text_var.set(f"{exposure:.0f}")
        if self.frame_camera.set_exposure(exposure):
            pass  # Success
    
    def on_exposure_entry_change(self, event=None):
        """Handle exposure text entry change"""
        try:
            exposure = float(self.exposure_text_var.get())
            # Get current range
            exposure_range = self.frame_camera.get_exposure_range()
            if exposure_range:
                min_exp, max_exp, _ = exposure_range
                # Clamp to valid range
                exposure = max(min_exp, min(max_exp, exposure))
                self.exposure_var.set(exposure)
                self.exposure_text_var.set(f"{exposure:.0f}")
                self.frame_camera.set_exposure(exposure)
        except ValueError:
            # Reset to current scale value
            self.exposure_text_var.set(f"{self.exposure_var.get():.0f}")
    
    def on_gain_scale_change(self, value):
        """Handle gain scale change"""
        gain = float(value)
        self.gain_text_var.set(f"{gain:.1f}")
        if self.frame_camera.set_gain(gain):
            pass  # Success
    
    def on_gain_entry_change(self, event=None):
        """Handle gain text entry change"""
        try:
            gain = float(self.gain_text_var.get())
            # Get current range
            gain_range = self.frame_camera.get_gain_range()
            if gain_range:
                min_gain, max_gain, _ = gain_range
                # Clamp to valid range
                gain = max(min_gain, min(max_gain, gain))
                self.gain_var.set(gain)
                self.gain_text_var.set(f"{gain:.1f}")
                self.frame_camera.set_gain(gain)
        except ValueError:
            # Reset to current scale value
            self.gain_text_var.set(f"{self.gain_var.get():.1f}")
    
    def on_bias_scale_change(self, bias_name, value):
        """Handle bias scale change"""
        bias_value = int(float(value))
        self.bias_text_vars[bias_name].set(str(bias_value))
        self.event_camera.set_bias_value(bias_name, bias_value)
    
    def on_bias_entry_change(self, bias_name):
        """Handle bias text entry change"""
        try:
            bias_value = int(self.bias_text_vars[bias_name].get())
            # Clamp to valid range (0-255)
            bias_value = max(0, min(255, bias_value))
            self.bias_vars[bias_name].set(bias_value)
            self.bias_text_vars[bias_name].set(str(bias_value))
            self.event_camera.set_bias_value(bias_name, bias_value)
        except ValueError:
            # Reset to current scale value
            self.bias_text_vars[bias_name].set(str(self.bias_vars[bias_name].get()))
    
    def update_status(self, message):
        """Update status message"""
        self.status_queue.put(message)
    
    def setup_status_update(self):
        """Setup periodic status updates"""
        def update():
            try:
                while True:
                    message = self.status_queue.get_nowait()
                    self.status_var.set(message)
                    
                    # Also add to status text
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    full_message = f"[{timestamp}] {message}\n"
                    
                    self.status_text.config(state=tk.NORMAL)
                    self.status_text.insert(tk.END, full_message)
                    self.status_text.see(tk.END)
                    self.status_text.config(state=tk.DISABLED)
            except queue.Empty:
                pass
            
            # Schedule next update
            self.root.after(100, update)
        
        # Start the update loop
        update()
    
    def run(self):
        """Run the GUI application"""
        def on_closing():
            # Cleanup with force disconnect
            try:
                self.frame_camera.force_disconnect()
                self.event_camera.stop_all()
                time.sleep(0.2)  # Give time for cleanup
            except:
                pass
            self.root.destroy()
        
        self.root.protocol("WM_DELETE_WINDOW", on_closing)
        self.root.mainloop()


def main():
    """Main function"""
    app = DualCameraGUI()
    app.run()


if __name__ == "__main__":
    main()