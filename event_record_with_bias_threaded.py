# Copyright (c) Prophesee S.A.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.
"""
Sample code that demonstrates how to use Metavision SDK to record events from a live camera in a RAW file
with configurable bias settings and non-blocking operation
"""
from metavision_core.event_io.raw_reader import initiate_device
from metavision_core.event_io import EventsIterator
from metavision_sdk_core import PeriodicFrameGenerationAlgorithm, ColorPalette
from metavision_sdk_ui import EventLoop, BaseWindow, MTWindow, UIAction, UIKeyEvent
import argparse
import time
import os
import threading
import queue
import sys


class EventCameraRecorder:
    def __init__(self, device, output_dir="", bias_args=None):
        self.device = device
        self.output_dir = output_dir
        self.bias_args = bias_args
        
        # Control flags
        self.is_recording = False
        self.should_exit = False
        self.visualization_running = False
        
        # Threading
        self.record_lock = threading.Lock()
        self.event_queue = queue.Queue(maxsize=1000)
        
        # Get camera geometry
        self.mv_iterator = None
        self.height = None
        self.width = None
        
        # Window reference
        self.window = None
        
        # Current log path
        self.current_log_path = None
        
    def initialize_camera(self):
        """Initialize camera and get geometry"""
        try:
            self.mv_iterator = EventsIterator.from_device(device=self.device, delta_t=1000)
            self.height, self.width = self.mv_iterator.get_size()
            print(f"Camera initialized: {self.width}x{self.height}")
            return True
        except Exception as e:
            print(f"Failed to initialize camera: {e}")
            return False
            
    def set_camera_biases(self):
        """Set camera bias values"""
        if self.bias_args is None:
            return
            
        bias_interface = self.device.get_i_ll_biases()
        
        if bias_interface is None:
            print("Warning: Could not get bias interface. Bias settings will not be applied.")
            return
        
        try:
            # Contrast settings
            bias_interface.set('bias_diff', self.bias_args.bias_diff)
            bias_interface.set('bias_diff_off', self.bias_args.bias_diff_off)
            bias_interface.set('bias_diff_on', self.bias_args.bias_diff_on)
            
            # Bandwidth settings
            bias_interface.set('bias_fo', self.bias_args.bias_fo)
            bias_interface.set('bias_hpf', self.bias_args.bias_hpf)
            
            # Advance settings
            bias_interface.set('bias_refr', self.bias_args.bias_refr)
            
            print("Bias settings applied successfully:")
            print(f"  Contrast:")
            print(f"    bias_diff: {self.bias_args.bias_diff}")
            print(f"    bias_diff_off: {self.bias_args.bias_diff_off}")
            print(f"    bias_diff_on: {self.bias_args.bias_diff_on}")
            print(f"  Bandwidth:")
            print(f"    bias_fo: {self.bias_args.bias_fo}")
            print(f"    bias_hpf: {self.bias_args.bias_hpf}")
            print(f"  Advance:")
            print(f"    bias_refr: {self.bias_args.bias_refr}")
            
            # Print all current bias values for verification
            print("\nAll current bias values:")
            all_biases = bias_interface.get_all_biases()
            for bias_name, bias_value in all_biases.items():
                print(f"  {bias_name}: {bias_value}")
                
        except Exception as e:
            print(f"Warning: Could not set some bias values. Error: {e}")
            print("Some bias settings might not be available on this camera model.")
    
    def start_recording(self):
        """Start recording events to a RAW file"""
        with self.record_lock:
            if self.is_recording:
                print("Already recording!")
                return
            
            if self.device.get_i_events_stream():
                self.current_log_path = "recording_" + time.strftime("%y%m%d_%H%M%S", time.localtime()) + ".raw"
                if self.output_dir != "":
                    self.current_log_path = os.path.join(self.output_dir, self.current_log_path)
                
                print(f'Started recording to {self.current_log_path}')
                self.device.get_i_events_stream().log_raw_data(self.current_log_path)
                self.is_recording = True
    
    def stop_recording(self):
        """Stop recording events"""
        with self.record_lock:
            if not self.is_recording:
                print("Not currently recording!")
                return
            
            self.device.get_i_events_stream().stop_log_raw_data()
            print(f'Stopped recording. File saved: {self.current_log_path}')
            self.is_recording = False
            self.current_log_path = None
    
    def visualization_thread(self):
        """Thread for event visualization"""
        try:
            # Event Frame Generator
            event_frame_gen = PeriodicFrameGenerationAlgorithm(sensor_width=self.width, sensor_height=self.height, 
                                                               fps=25, palette=ColorPalette.Dark)
            
            # Create window - using regular Window instead of MTWindow for thread safety
            with MTWindow(title="Metavision Events Viewer", width=self.width, height=self.height,
                         mode=BaseWindow.RenderMode.BGR) as window:
                
                self.window = window
                
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
                print("Visualization started")
                
                # Process events
                while not self.should_exit:
                    if window.should_close():
                        break
                        
                    try:
                        # Get events from queue with timeout
                        evs = self.event_queue.get(timeout=0.01)
                        
                        # Dispatch system events to the window
                        EventLoop.poll_and_dispatch()
                        event_frame_gen.process_events(evs)
                        
                    except queue.Empty:
                        # No events available, just poll window events
                        EventLoop.poll_and_dispatch()
                    except Exception as e:
                        print(f"Visualization error: {e}")
                        break
            
        except Exception as e:
            print(f"Failed to start visualization: {e}")
        finally:
            self.visualization_running = False
            self.window = None
            print("Visualization thread ended")
    
    def event_processing_thread(self):
        """Thread for reading events from camera"""
        try:
            print("Event processing started")
            for evs in self.mv_iterator:
                if self.should_exit:
                    break
                
                # Try to put events in queue for visualization
                try:
                    self.event_queue.put(evs, block=False)
                except queue.Full:
                    # Skip if queue is full (visualization is slower than event rate)
                    pass
                
                # Check if we should stop
                if self.should_exit:
                    break
                    
        except Exception as e:
            print(f"Event processing error: {e}")
        finally:
            print("Event processing thread ended")
    
    def control_loop(self):
        """Main control loop for terminal commands"""
        print("\n=== Event Camera Recorder Control ===")
        print("Commands:")
        print("  start - Start recording")
        print("  stop  - Stop recording")
        print("  status - Show recording status")
        print("  exit  - Exit program")
        print("=====================================\n")
        
        while not self.should_exit:
            try:
                command = input("Enter command: ").strip().lower()
                
                if command == "start":
                    self.start_recording()
                elif command == "stop":
                    self.stop_recording()
                elif command == "status":
                    with self.record_lock:
                        if self.is_recording:
                            print(f"Recording to: {self.current_log_path}")
                        else:
                            print("Not recording")
                        print(f"Visualization: {'Running' if self.visualization_running else 'Stopped'}")
                elif command == "exit":
                    print("Exiting...")
                    self.should_exit = True
                    break
                else:
                    print("Unknown command. Use: start, stop, status, or exit")
                    
            except KeyboardInterrupt:
                print("\nReceived interrupt signal. Exiting...")
                self.should_exit = True
                break
            except EOFError:
                # Handle case where input is not available (e.g., running in non-interactive mode)
                print("No input available. Keeping program running. Press Ctrl+C to exit.")
                time.sleep(1)
            except Exception as e:
                print(f"Error: {e}")
    
    def run(self):
        """Main run method"""
        # Initialize camera first
        if not self.initialize_camera():
            print("Failed to initialize camera. Exiting.")
            return
            
        # Set camera biases
        self.set_camera_biases()
        
        # Start event processing thread (not daemon)
        event_thread = threading.Thread(target=self.event_processing_thread)
        event_thread.start()
        
        # Start visualization thread (not daemon)
        viz_thread = threading.Thread(target=self.visualization_thread)
        viz_thread.start()
        
        # Give threads time to start
        time.sleep(0.5)
        
        # Run control loop in main thread
        try:
            self.control_loop()
        finally:
            # Cleanup
            self.should_exit = True
            
            # Stop recording if active
            if self.is_recording:
                self.stop_recording()
            
            # Wait for threads to finish
            print("Waiting for threads to finish...")
            event_thread.join(timeout=5.0)
            viz_thread.join(timeout=5.0)
            
            print("Program ended")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Metavision RAW file Recorder with non-blocking operation.',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        '-o', '--output-dir', default="", help="Directory where to create RAW file with recorded event data")
    
    # Bias settings arguments
    parser.add_argument('--bias-diff', type=int, default=0, help="Bias diff value (default: 0)")
    parser.add_argument('--bias-diff-off', type=int, default=100, help="Bias diff off value (default: 100)")
    parser.add_argument('--bias-diff-on', type=int, default=50, help="Bias diff on value (default: 50)")
    parser.add_argument('--bias-fo', type=int, default=0, help="Bias fo (cutoff frequency) value (default: 0)")
    parser.add_argument('--bias-hpf', type=int, default=0, help="Bias hpf value (default: 0)")
    parser.add_argument('--bias-refr', type=int, default=0, help="Bias refr value (default: 0)")
    
    args = parser.parse_args()
    return args


def main():
    """Main function"""
    args = parse_args()
    
    try:
        # HAL Device on live camera
        print("Initializing camera...")
        device = initiate_device("")
        
        if device is None:
            print("Failed to open camera device!")
            return
            
        # Create and run recorder
        recorder = EventCameraRecorder(device, args.output_dir, args)
        recorder.run()
        
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()