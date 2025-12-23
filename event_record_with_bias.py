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
with configurable bias settings
"""
from metavision_core.event_io.raw_reader import initiate_device
from metavision_core.event_io import EventsIterator
from metavision_sdk_core import PeriodicFrameGenerationAlgorithm, ColorPalette
from metavision_sdk_ui import EventLoop, BaseWindow, MTWindow, UIAction, UIKeyEvent
import argparse
import time
import os


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Metavision RAW file Recorder sample with bias settings.',
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


def set_camera_biases(device, args):
    """Set camera bias values"""
    bias_interface = device.get_i_ll_biases()
    
    if bias_interface is None:
        print("Warning: Could not get bias interface. Bias settings will not be applied.")
        return
    
    try:
        # Contrast settings
        bias_interface.set('bias_diff', args.bias_diff)
        bias_interface.set('bias_diff_off', args.bias_diff_off)
        bias_interface.set('bias_diff_on', args.bias_diff_on)
        
        # Bandwidth settings
        bias_interface.set('bias_fo', args.bias_fo)
        bias_interface.set('bias_hpf', args.bias_hpf)
        
        # Advance settings
        bias_interface.set('bias_refr', args.bias_refr)
        
        print("Bias settings applied successfully:")
        print(f"  Contrast:")
        print(f"    bias_diff: {args.bias_diff}")
        print(f"    bias_diff_off: {args.bias_diff_off}")
        print(f"    bias_diff_on: {args.bias_diff_on}")
        print(f"  Bandwidth:")
        print(f"    bias_fo: {args.bias_fo}")
        print(f"    bias_hpf: {args.bias_hpf}")
        print(f"  Advance:")
        print(f"    bias_refr: {args.bias_refr}")
        
        # Print all current bias values for verification
        print("\nAll current bias values:")
        all_biases = bias_interface.get_all_biases()
        for bias_name, bias_value in all_biases.items():
            print(f"  {bias_name}: {bias_value}")
            
    except Exception as e:
        print(f"Warning: Could not set some bias values. Error: {e}")
        print("Some bias settings might not be available on this camera model.")


def main():
    """ Main """
    args = parse_args()
    
    # HAL Device on live camera
    device = initiate_device("")
    
    # Set camera biases
    set_camera_biases(device, args)
    
    # Start the recording
    if device.get_i_events_stream():
        log_path = "recording_" + time.strftime("%y%m%d_%H%M%S", time.localtime()) + ".raw"
        if args.output_dir != "":
            log_path = os.path.join(args.output_dir, log_path)
        print(f'\nRecording to {log_path}')
        device.get_i_events_stream().log_raw_data(log_path)
    
    # Events iterator on Device
    mv_iterator = EventsIterator.from_device(device=device)
    height, width = mv_iterator.get_size()  # Camera Geometry
    
    # Window - Graphical User Interface
    with MTWindow(title="Metavision Events Viewer", width=width, height=height,
                  mode=BaseWindow.RenderMode.BGR) as window:
        def keyboard_cb(key, scancode, action, mods):
            if key == UIKeyEvent.KEY_ESCAPE or key == UIKeyEvent.KEY_Q:
                window.set_close_flag()
        
        window.set_keyboard_callback(keyboard_cb)
        
        # Event Frame Generator
        event_frame_gen = PeriodicFrameGenerationAlgorithm(sensor_width=width, sensor_height=height, fps=25,
                                                           palette=ColorPalette.Dark)
        
        def on_cd_frame_cb(ts, cd_frame):
            window.show_async(cd_frame)
        
        event_frame_gen.set_output_callback(on_cd_frame_cb)
        
        # Process events
        for evs in mv_iterator:
            # Dispatch system events to the window
            EventLoop.poll_and_dispatch()
            event_frame_gen.process_events(evs)
            
            if window.should_close():
                # Stop the recording
                device.get_i_events_stream().stop_log_raw_data()
                break


if __name__ == "__main__":
    main()