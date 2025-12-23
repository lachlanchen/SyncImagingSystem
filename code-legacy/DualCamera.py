#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
import queue
import os
import sys
from datetime import datetime

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
            # Initialize SDK if not already done
            MvCamera.MV_CC_Initialize()
            
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
        """Disconnect camera"""
        if self.cam:
            self.stop_grabbing()
            self.cam.MV_CC_CloseDevice()
            self.cam.MV_CC_DestroyHandle()
            self.cam = None
            self._notify_status("Frame camera disconnected")
    
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
            return False
            
        ret = self.cam.MV_CC_StartGrabbing()
        if ret == 0:
            self.is_grabbing = True
            self.exit_flag = False
            self.recording_thread = threading.Thread(target=self._recording_worker, daemon=True)
            self.recording_thread.start()
            self._notify_status("Frame grabbing started")
            return True
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
            
            self.cam.MV_CC_StopGrabbing()
            self.is_grabbing = False
            self._notify_status("Frame grabbing stopped")
    
    def start_recording(self, filename=None):
        """Start recording"""
        if not filename:
            device_name = self._get_device_name(self.device_info).replace(" ", "_")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{device_name}_{timestamp}.avi"
        
        self.current_filename = filename
        self.command_queue.put(('START_RECORDING', filename))
    
    def stop_recording(self):
        """Stop recording"""
        self.command_queue.put(('STOP_RECORDING',))
    
    def start_preview(self):
        """Start preview"""
        if not self.is_grabbing:
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
        """Preview worker thread"""
        window_name = f"Frame Camera Preview"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        
        while not self.exit_flag and self.show_preview:
            try:
                frame = self.frame_queue.get(timeout=0.1)
                cv2.imshow(window_name, frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == 27:  # ESC
                    self.show_preview = False
                    break
                    
            except queue.Empty:
                if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
                    self.show_preview = False
                    break
            except Exception as e:
                break
        
        cv2.destroyWindow(window_name)
    
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
    """Modified version of EventCameraRecorder for GUI integration"""
    
    def __init__(self, status_callback=None):
        self.device = None
        self.mv_iterator = None
        self.height = None
        self.width = None
        
        self.is_recording = False
        self.should_exit = False
        self.visualization_running = False
        
        self.record_lock = threading.Lock()
        self.event_queue = queue.Queue(maxsize=1000)
        self.status_callback = status_callback
        
        self.current_log_path = None
        
        # Threads
        self.event_thread = None
        self.viz_thread = None
    
    def find_cameras(self):
        """Find available event cameras"""
        if not EVENT_CAMERA_AVAILABLE:
            return []
        
        try:
            device = initiate_device("")
            if device is None:
                return []
            return [("Event Camera", device)]
        except:
            return []
    
    def connect_camera(self, device=None):
        """Connect to event camera"""
        if not EVENT_CAMERA_AVAILABLE:
            return False
        
        try:
            if device is None:
                self.device = initiate_device("")
            else:
                self.device = device
            
            if self.device is None:
                return False
            
            self.mv_iterator = EventsIterator.from_device(device=self.device, delta_t=1000)
            self.height, self.width = self.mv_iterator.get_size()
            
            self._notify_status(f"Event camera connected: {self.width}x{self.height}")
            return True
            
        except Exception as e:
            self._notify_status(f"Event camera connection failed: {e}")
            return False
    
    def disconnect_camera(self):
        """Disconnect camera"""
        self.stop_all()
        self.device = None
        self.mv_iterator = None
        self._notify_status("Event camera disconnected")
    
    def start_capture(self):
        """Start capturing events"""
        if not self.device:
            return False
        
        self.should_exit = False
        self.event_thread = threading.Thread(target=self._event_processing_thread, daemon=True)
        self.event_thread.start()
        self._notify_status("Event capture started")
        return True
    
    def stop_capture(self):
        """Stop capturing events"""
        self.should_exit = True
        if self.event_thread:
            self.event_thread.join(timeout=2.0)
        self._notify_status("Event capture stopped")
    
    def start_recording(self, output_dir=""):
        """Start recording events"""
        with self.record_lock:
            if self.is_recording:
                return False
            
            if self.device and self.device.get_i_events_stream():
                self.current_log_path = "recording_" + time.strftime("%y%m%d_%H%M%S", time.localtime()) + ".raw"
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
            
            self.device.get_i_events_stream().stop_log_raw_data()
            self.is_recording = False
            self._notify_status(f"Recording stopped: {self.current_log_path}")
            return True
    
    def start_visualization(self):
        """Start event visualization"""
        if not self.device or self.visualization_running:
            return False
        
        self.viz_thread = threading.Thread(target=self._visualization_thread, daemon=True)
        self.viz_thread.start()
        return True
    
    def stop_visualization(self):
        """Stop visualization"""
        self.visualization_running = False
        if self.viz_thread:
            self.viz_thread.join(timeout=2.0)
    
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
        """Thread for reading events from camera"""
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
    
    def _visualization_thread(self):
        """Thread for event visualization"""
        try:
            event_frame_gen = PeriodicFrameGenerationAlgorithm(
                sensor_width=self.width, sensor_height=self.height, 
                fps=25, palette=ColorPalette.Dark
            )
            
            with MTWindow(title="Event Camera Preview", width=self.width, height=self.height,
                         mode=BaseWindow.RenderMode.BGR) as window:
                
                def keyboard_cb(key, scancode, action, mods):
                    if action != UIAction.RELEASE:
                        return
                    if key == UIKeyEvent.KEY_ESCAPE or key == UIKeyEvent.KEY_Q:
                        window.set_close_flag()
                
                window.set_keyboard_callback(keyboard_cb)
                
                def on_cd_frame_cb(ts, cd_frame):
                    window.show_async(cd_frame)
                
                event_frame_gen.set_output_callback(on_cd_frame_cb)
                
                self.visualization_running = True
                self._notify_status("Event visualization started")
                
                while not self.should_exit:
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
            self._notify_status(f"Visualization error: {e}")
        finally:
            self.visualization_running = False
            self._notify_status("Event visualization stopped")
    
    def _notify_status(self, message):
        """Notify status callback"""
        if self.status_callback:
            self.status_callback(f"Event: {message}")
    
    def get_status(self):
        """Get current status"""
        return {
            'connected': self.device is not None,
            'capturing': self.event_thread is not None and self.event_thread.is_alive(),
            'recording': self.is_recording,
            'visualizing': self.visualization_running
        }


class DualCameraGUI:
    """Main GUI application"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Dual Camera Control System")
        self.root.geometry("1200x800")
        
        # Camera controllers
        self.frame_camera = FrameCameraController(self.update_status)
        self.event_camera = EventCameraController(self.update_status)
        
        # GUI variables
        self.frame_cameras_list = []
        self.event_cameras_list = []
        
        # Status update queue
        self.status_queue = queue.Queue()
        
        self.create_widgets()
        self.setup_status_update()
        
        # Auto-scan for cameras
        self.scan_cameras()
    
    def create_widgets(self):
        """Create GUI widgets"""
        # Main notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame camera tab
        self.frame_tab = ttk.Frame(notebook)
        notebook.add(self.frame_tab, text="Frame Camera")
        self.create_frame_camera_tab()
        
        # Event camera tab
        self.event_tab = ttk.Frame(notebook)
        notebook.add(self.event_tab, text="Event Camera")
        self.create_event_camera_tab()
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def create_frame_camera_tab(self):
        """Create frame camera control tab"""
        # Connection frame
        conn_frame = ttk.LabelFrame(self.frame_tab, text="Connection")
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
        control_frame = ttk.LabelFrame(self.frame_tab, text="Control")
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.frame_grab_btn = ttk.Button(control_frame, text="Start Grabbing", command=self.toggle_frame_grabbing)
        self.frame_grab_btn.grid(row=0, column=0, padx=5, pady=5)
        
        self.frame_preview_btn = ttk.Button(control_frame, text="Start Preview", command=self.toggle_frame_preview)
        self.frame_preview_btn.grid(row=0, column=1, padx=5, pady=5)
        
        self.frame_record_btn = ttk.Button(control_frame, text="Start Recording", command=self.toggle_frame_recording)
        self.frame_record_btn.grid(row=0, column=2, padx=5, pady=5)
        
        # Parameters frame
        param_frame = ttk.LabelFrame(self.frame_tab, text="Parameters")
        param_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Exposure
        ttk.Label(param_frame, text="Exposure (μs):").grid(row=0, column=0, padx=5, pady=5)
        self.exposure_var = tk.DoubleVar()
        self.exposure_scale = ttk.Scale(param_frame, from_=100, to=10000, variable=self.exposure_var, 
                                       orient=tk.HORIZONTAL, command=self.on_exposure_change)
        self.exposure_scale.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.exposure_label = ttk.Label(param_frame, text="1000")
        self.exposure_label.grid(row=0, column=2, padx=5, pady=5)
        
        # Gain
        ttk.Label(param_frame, text="Gain (dB):").grid(row=1, column=0, padx=5, pady=5)
        self.gain_var = tk.DoubleVar()
        self.gain_scale = ttk.Scale(param_frame, from_=0, to=20, variable=self.gain_var,
                                   orient=tk.HORIZONTAL, command=self.on_gain_change)
        self.gain_scale.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.gain_label = ttk.Label(param_frame, text="0")
        self.gain_label.grid(row=1, column=2, padx=5, pady=5)
        
        param_frame.columnconfigure(1, weight=1)
        
        # Status frame
        frame_status_frame = ttk.LabelFrame(self.frame_tab, text="Status")
        frame_status_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.frame_status_text = tk.Text(frame_status_frame, height=8, state=tk.DISABLED)
        frame_status_scroll = ttk.Scrollbar(frame_status_frame, orient=tk.VERTICAL, command=self.frame_status_text.yview)
        self.frame_status_text.configure(yscrollcommand=frame_status_scroll.set)
        
        self.frame_status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        frame_status_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_event_camera_tab(self):
        """Create event camera control tab"""
        # Connection frame
        conn_frame = ttk.LabelFrame(self.event_tab, text="Connection")
        conn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.event_connect_btn = ttk.Button(conn_frame, text="Connect Event Camera", command=self.connect_event_camera)
        self.event_connect_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Control frame
        control_frame = ttk.LabelFrame(self.event_tab, text="Control")
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.event_capture_btn = ttk.Button(control_frame, text="Start Capture", command=self.toggle_event_capture)
        self.event_capture_btn.grid(row=0, column=0, padx=5, pady=5)
        
        self.event_viz_btn = ttk.Button(control_frame, text="Start Visualization", command=self.toggle_event_visualization)
        self.event_viz_btn.grid(row=0, column=1, padx=5, pady=5)
        
        self.event_record_btn = ttk.Button(control_frame, text="Start Recording", command=self.toggle_event_recording)
        self.event_record_btn.grid(row=0, column=2, padx=5, pady=5)
        
        # Bias parameters frame
        bias_frame = ttk.LabelFrame(self.event_tab, text="Bias Parameters")
        bias_frame.pack(fill=tk.X, padx=5, pady=5)
        
        bias_names = ['bias_diff', 'bias_diff_off', 'bias_diff_on', 'bias_fo', 'bias_hpf', 'bias_refr']
        self.bias_vars = {}
        self.bias_scales = {}
        
        for i, bias_name in enumerate(bias_names):
            row = i // 2
            col = (i % 2) * 3
            
            ttk.Label(bias_frame, text=f"{bias_name}:").grid(row=row, column=col, padx=5, pady=2)
            var = tk.IntVar()
            scale = ttk.Scale(bias_frame, from_=0, to=255, variable=var, orient=tk.HORIZONTAL,
                             command=lambda val, name=bias_name: self.on_bias_change(name, val))
            scale.grid(row=row, column=col+1, padx=5, pady=2, sticky="ew")
            
            self.bias_vars[bias_name] = var
            self.bias_scales[bias_name] = scale
        
        bias_frame.columnconfigure(1, weight=1)
        bias_frame.columnconfigure(4, weight=1)
        
        # Status frame
        event_status_frame = ttk.LabelFrame(self.event_tab, text="Status")
        event_status_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.event_status_text = tk.Text(event_status_frame, height=8, state=tk.DISABLED)
        event_status_scroll = ttk.Scrollbar(event_status_frame, orient=tk.VERTICAL, command=self.event_status_text.yview)
        self.event_status_text.configure(yscrollcommand=event_status_scroll.set)
        
        self.event_status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        event_status_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    
    def scan_cameras(self):
        """Scan for available cameras"""
        # Frame cameras
        self.frame_cameras_list = self.frame_camera.find_cameras()
        frame_names = [f"{idx}: {name}" for idx, name, _ in self.frame_cameras_list]
        self.frame_camera_combo['values'] = frame_names
        if frame_names:
            self.frame_camera_combo.current(0)
        
        # Event cameras
        self.event_cameras_list = self.event_camera.find_cameras()
        
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
    
    def connect_event_camera(self):
        """Connect to event camera"""
        if self.event_camera.connect_camera():
            self.event_connect_btn.config(text="Disconnect Event Camera", command=self.disconnect_event_camera)
            self.update_event_parameters()
        else:
            messagebox.showerror("Error", "Failed to connect to event camera!")
    
    def disconnect_event_camera(self):
        """Disconnect event camera"""
        self.event_camera.disconnect_camera()
        self.event_connect_btn.config(text="Connect Event Camera", command=self.connect_event_camera)
    
    def update_frame_parameters(self):
        """Update frame camera parameter ranges"""
        exposure_range = self.frame_camera.get_exposure_range()
        if exposure_range:
            min_exp, max_exp, cur_exp = exposure_range
            self.exposure_scale.config(from_=min_exp, to=max_exp)
            self.exposure_var.set(cur_exp)
            self.exposure_label.config(text=f"{cur_exp:.0f}")
        
        gain_range = self.frame_camera.get_gain_range()
        if gain_range:
            min_gain, max_gain, cur_gain = gain_range
            self.gain_scale.config(from_=min_gain, to=max_gain)
            self.gain_var.set(cur_gain)
            self.gain_label.config(text=f"{cur_gain:.1f}")
    
    def update_event_parameters(self):
        """Update event camera bias values"""
        bias_values = self.event_camera.get_bias_values()
        for bias_name, var in self.bias_vars.items():
            if bias_name in bias_values:
                var.set(bias_values[bias_name])
    
    def toggle_frame_grabbing(self):
        """Toggle frame grabbing"""
        if not self.frame_camera.is_grabbing:
            if self.frame_camera.start_grabbing():
                self.frame_grab_btn.config(text="Stop Grabbing")
        else:
            self.frame_camera.stop_grabbing()
            self.frame_grab_btn.config(text="Start Grabbing")
            self.frame_preview_btn.config(text="Start Preview")
            self.frame_record_btn.config(text="Start Recording")
    
    def toggle_frame_preview(self):
        """Toggle frame preview"""
        if not self.frame_camera.show_preview:
            if self.frame_camera.start_preview():
                self.frame_preview_btn.config(text="Stop Preview")
        else:
            self.frame_camera.stop_preview()
            self.frame_preview_btn.config(text="Start Preview")
    
    def toggle_frame_recording(self):
        """Toggle frame recording"""
        if not self.frame_camera.is_recording:
            self.frame_camera.start_recording()
            self.frame_record_btn.config(text="Stop Recording")
        else:
            self.frame_camera.stop_recording()
            self.frame_record_btn.config(text="Start Recording")
    
    def toggle_event_capture(self):
        """Toggle event capture"""
        status = self.event_camera.get_status()
        if not status['capturing']:
            if self.event_camera.start_capture():
                self.event_capture_btn.config(text="Stop Capture")
        else:
            self.event_camera.stop_capture()
            self.event_capture_btn.config(text="Start Capture")
    
    def toggle_event_visualization(self):
        """Toggle event visualization"""
        if not self.event_camera.visualization_running:
            if self.event_camera.start_visualization():
                self.event_viz_btn.config(text="Stop Visualization")
        else:
            self.event_camera.stop_visualization()
            self.event_viz_btn.config(text="Start Visualization")
    
    def toggle_event_recording(self):
        """Toggle event recording"""
        if not self.event_camera.is_recording:
            if self.event_camera.start_recording():
                self.event_record_btn.config(text="Stop Recording")
        else:
            self.event_camera.stop_recording()
            self.event_record_btn.config(text="Start Recording")
    
    def on_exposure_change(self, value):
        """Handle exposure change"""
        exposure = float(value)
        self.exposure_label.config(text=f"{exposure:.0f}")
        if self.frame_camera.set_exposure(exposure):
            pass  # Success
    
    def on_gain_change(self, value):
        """Handle gain change"""
        gain = float(value)
        self.gain_label.config(text=f"{gain:.1f}")
        if self.frame_camera.set_gain(gain):
            pass  # Success
    
    def on_bias_change(self, bias_name, value):
        """Handle bias change"""
        bias_value = int(float(value))
        self.event_camera.set_bias_value(bias_name, bias_value)
    
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
                    
                    # Also add to appropriate status text
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    full_message = f"[{timestamp}] {message}\n"
                    
                    if message.startswith("Frame:"):
                        self.frame_status_text.config(state=tk.NORMAL)
                        self.frame_status_text.insert(tk.END, full_message)
                        self.frame_status_text.see(tk.END)
                        self.frame_status_text.config(state=tk.DISABLED)
                    elif message.startswith("Event:"):
                        self.event_status_text.config(state=tk.NORMAL)
                        self.event_status_text.insert(tk.END, full_message)
                        self.event_status_text.see(tk.END)
                        self.event_status_text.config(state=tk.DISABLED)
            except queue.Empty:
                pass
            
            # Schedule next update
            self.root.after(100, update)
        
        # Start the update loop
        update()
    
    def run(self):
        """Run the GUI application"""
        def on_closing():
            # Cleanup
            try:
                self.frame_camera.disconnect_camera()
                self.event_camera.disconnect_camera()
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