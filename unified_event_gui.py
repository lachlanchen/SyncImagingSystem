#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import queue
import threading
import time
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import cv2
import numpy as np

try:
    import dv_processing as dv
    DAVIS_AVAILABLE = True
except Exception as e:
    dv = None
    DAVIS_AVAILABLE = False
    DAVIS_IMPORT_ERROR = str(e)

try:
    from metavision_core.event_io.raw_reader import initiate_device
    from metavision_core.event_io import EventsIterator
    from metavision_sdk_core import PeriodicFrameGenerationAlgorithm, ColorPalette
    from metavision_sdk_ui import EventLoop, BaseWindow, MTWindow, UIAction, UIKeyEvent
    EVK_AVAILABLE = True
except Exception as e:
    EVK_AVAILABLE = False
    EVK_IMPORT_ERROR = str(e)


DEFAULT_OUTPUT_DIR = "recordings"
DEFAULT_PREFIX = "session"
PREVIEW_FPS = 30.0


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def build_run_dir(base_dir: str, prefix: str) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name = f"{prefix}_{timestamp}" if prefix else timestamp
    run_dir = Path(base_dir) / name
    ensure_dir(run_dir)
    return run_dir


def device_subdir_name(label: str) -> str:
    safe = label.lower().replace(":", "_").replace(" ", "_")
    return safe


def safe_close_writer(writer) -> None:
    if writer is None:
        return
    for method_name in ("close", "finish", "flush", "release"):
        close_fn = getattr(writer, method_name, None)
        if close_fn:
            try:
                close_fn()
            except Exception:
                pass
            break


class EVKController:
    vendor = "evk"

    def __init__(self, status_cb, label):
        self.status_cb = status_cb
        self.label = label
        self.device = None
        self.iterator = None
        self.width = None
        self.height = None

        self.event_queue = queue.Queue(maxsize=200)
        self.capture_thread = None
        self.preview_thread = None
        self.window = None

        self.capturing = False
        self.preview_running = False
        self.recording = False
        self.should_exit = threading.Event()
        self.current_log_path = None

    def connect(self):
        if not EVK_AVAILABLE:
            self._notify(f"Metavision SDK not available: {EVK_IMPORT_ERROR}")
            return False
        try:
            self.device = initiate_device("")
            if self.device is None:
                self._notify("EVK device not found.")
                return False
            self.iterator = EventsIterator.from_device(device=self.device, delta_t=1000)
            self.height, self.width = self.iterator.get_size()
            self._notify(f"Connected EVK: {self.width}x{self.height}")
            return True
        except Exception as e:
            self._notify(f"EVK connect failed: {e}")
            return False

    def disconnect(self):
        self.stop_all()
        self.device = None
        self.iterator = None
        self._notify("Disconnected EVK")

    def start_capture(self):
        if self.capturing:
            return True
        if self.device is None:
            self._notify("EVK not connected")
            return False
        self.should_exit.clear()
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()
        self.capturing = True
        return True

    def stop_capture(self):
        if not self.capturing:
            return
        self.should_exit.set()
        if self.capture_thread:
            self.capture_thread.join(timeout=2.0)
        self.capturing = False

    def start_preview(self):
        if self.preview_running:
            return True
        if not self.start_capture():
            return False
        self.preview_running = True
        self.preview_thread = threading.Thread(target=self._preview_loop, daemon=True)
        self.preview_thread.start()
        self._notify("EVK preview started")
        return True

    def stop_preview(self):
        if not self.preview_running:
            return
        self.preview_running = False
        if self.window:
            try:
                self.window.set_close_flag()
            except Exception:
                pass
        if self.preview_thread:
            self.preview_thread.join(timeout=2.0)
        self.window = None
        self._notify("EVK preview stopped")

    def start_recording(self, out_dir: Path, prefix: str):
        if self.recording:
            return True
        if self.device is None:
            self._notify("EVK not connected")
            return False
        ensure_dir(out_dir)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name = f"{prefix}_{timestamp}_evk.raw" if prefix else f"evk_{timestamp}.raw"
        self.current_log_path = str(out_dir / name)
        try:
            if self.device.get_i_events_stream():
                self.device.get_i_events_stream().log_raw_data(self.current_log_path)
                self.recording = True
                self._notify(f"EVK recording: {self.current_log_path}")
                return True
        except Exception as e:
            self._notify(f"EVK record start failed: {e}")
        return False

    def stop_recording(self):
        if not self.recording:
            return
        try:
            self.device.get_i_events_stream().stop_log_raw_data()
        except Exception:
            pass
        self.recording = False
        self._notify(f"EVK recording stopped: {self.current_log_path}")

    def stop_all(self):
        if self.recording:
            self.stop_recording()
        if self.preview_running:
            self.stop_preview()
        if self.capturing:
            self.stop_capture()

    def _capture_loop(self):
        try:
            for evs in self.iterator:
                if self.should_exit.is_set():
                    break
                if self.preview_running:
                    try:
                        self.event_queue.put(evs, block=False)
                    except queue.Full:
                        pass
        except Exception as e:
            self._notify(f"EVK capture error: {e}")
        finally:
            self.capturing = False

    def _preview_loop(self):
        try:
            event_frame_gen = PeriodicFrameGenerationAlgorithm(
                sensor_width=self.width,
                sensor_height=self.height,
                fps=25,
                palette=ColorPalette.Dark
            )
            with MTWindow(
                title=f"EVK Preview - {self.label}",
                width=self.width,
                height=self.height,
                mode=BaseWindow.RenderMode.BGR,
            ) as window:
                self.window = window

                def keyboard_cb(key, scancode, action, mods):
                    if action != UIAction.RELEASE:
                        return
                    if key in (UIKeyEvent.KEY_ESCAPE, UIKeyEvent.KEY_Q):
                        window.set_close_flag()

                window.set_keyboard_callback(keyboard_cb)

                def on_cd_frame_cb(ts, cd_frame):
                    window.show_async(cd_frame)

                event_frame_gen.set_output_callback(on_cd_frame_cb)

                while self.preview_running and not self.should_exit.is_set():
                    if window.should_close():
                        break
                    try:
                        evs = self.event_queue.get(timeout=0.01)
                        EventLoop.poll_and_dispatch()
                        event_frame_gen.process_events(evs)
                    except queue.Empty:
                        EventLoop.poll_and_dispatch()
                    except Exception:
                        break
        except Exception as e:
            self._notify(f"EVK preview error: {e}")
        finally:
            self.preview_running = False
            self.window = None

    def _notify(self, msg):
        if self.status_cb:
            self.status_cb(f"EVK: {msg}")


class DavisController:
    vendor = "davis"

    def __init__(self, status_cb, label, serial=None):
        self.status_cb = status_cb
        self.label = label
        self.serial = serial
        self.camera = None
        self.event_resolution = None
        self.frame_resolution = None

        self.event_queue = queue.Queue(maxsize=200)
        self.capture_thread = None
        self.preview_thread = None
        self.preview_visualizer = None
        self.preview_running = False
        self.capturing = False
        self.stop_event = threading.Event()

        self.recording = False
        self.writer = None
        self.events_buffer = []
        self.save_npz = True
        self.current_output_dir = None

    def connect(self):
        if not DAVIS_AVAILABLE:
            self._notify(f"dv-processing not available: {DAVIS_IMPORT_ERROR}")
            return False
        try:
            if indication := (self.serial is not None):
                self.camera = dv.io.camera.open(self.serial)
            else:
                self.camera = dv.io.camera.open()
            self.event_resolution = self.camera.getEventResolution()
            self.frame_resolution = self.camera.getFrameResolution()
            self._notify(f"Connected DAVIS (events={self.event_resolution}, frames={self.frame_resolution})")
            return True
        except Exception as e:
            self._notify(f"DAVIS connect failed: {e}")
            return False

    def disconnect(self):
        self.stop_all()
        self.camera = None
        self._notify("Disconnected DAVIS")

    def start_capture(self):
        if self.capturing:
            return True
        if self.camera is None:
            self._notify("DAVIS not connected")
            return False
        self.stop_event.clear()
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()
        self.capturing = True
        return True

    def stop_capture(self):
        if not self.capturing:
            return
        self.stop_event.set()
        if self.capture_thread:
            self.capture_thread.join(timeout=2.0)
        self.capturing = False

    def start_preview(self):
        if self.preview_running:
            return True
        if not self.start_capture():
            return False
        resolution = self.event_resolution or self.frame_resolution
        if resolution is None:
            self._notify("Preview disabled: resolution not available")
            return False
        self.preview_visualizer = dv.visualization.EventVisualizer(resolution)
        self.preview_running = True
        self.preview_thread = threading.Thread(target=self._preview_loop, daemon=True)
        self.preview_thread.start()
        self._notify("DAVIS preview started")
        return True

    def stop_preview(self):
        if not self.preview_running:
            return
        self.preview_running = False
        if self.preview_thread:
            self.preview_thread.join(timeout=2.0)
        cv2.destroyWindow(self._preview_window_name())
        self._notify("DAVIS preview stopped")

    def start_recording(self, out_dir: Path, prefix: str):
        if self.recording:
            return True
        if self.camera is None:
            self._notify("DAVIS not connected")
            return False
        ensure_dir(out_dir)
        self.current_output_dir = out_dir
        aedat_path = out_dir / "output.aedat4"
        camera_name = self.camera.getCameraName() if self.camera else "DAVIS"
        cfg = dv.io.MonoCameraWriter.Config(camera_name)

        event_res = self.event_resolution or self.frame_resolution
        if event_res:
            cfg.addEventStream(event_res)
        if self.frame_resolution:
            cfg.addFrameStream(self.frame_resolution)

        try:
            self.writer = dv.io.MonoCameraWriter(str(aedat_path), cfg)
        except Exception as e:
            self._notify(f"AEDAT4 writer failed: {e}")
            return False

        self.events_buffer = []
        self.recording = True
        self._notify(f"DAVIS recording: {aedat_path}")
        if not self.start_capture():
            return False
        return True

    def stop_recording(self):
        if not self.recording:
            return
        self.recording = False
        safe_close_writer(self.writer)
        self.writer = None
        if self.save_npz and self.events_buffer and self.current_output_dir:
            events_np = np.concatenate(self.events_buffer)
            np.savez_compressed(
                self.current_output_dir / "events.npz",
                t=events_np["timestamp"],
                x=events_np["x"],
                y=events_np["y"],
                p=events_np["polarity"],
            )
        self._notify("DAVIS recording stopped")

    def stop_all(self):
        if self.recording:
            self.stop_recording()
        if self.preview_running:
            self.stop_preview()
        if self.capturing:
            self.stop_capture()

    def _capture_loop(self):
        try:
            while not self.stop_event.is_set():
                packet = self.camera.readNext()
                if isinstance(packet, dv.EventStore):
                    if self.recording and self.writer:
                        self.writer.writeEvents(packet)
                        if self.save_npz:
                            self.events_buffer.append(packet.numpy())
                    if self.preview_running:
                        try:
                            self.event_queue.put(packet, block=False)
                        except queue.Full:
                            pass
                elif isinstance(packet, dv.Frame):
                    if self.recording and self.writer:
                        self.writer.writeFrame(packet)
                elif isinstance(packet, dv.io.DataReadHandler.OutputFlag):
                    if packet == dv.io.DataReadHandler.OutputFlag.END_OF_FILE:
                        break
                else:
                    time.sleep(0.001)
        except Exception as e:
            self._notify(f"DAVIS capture error: {e}")
        finally:
            self.capturing = False

    def _preview_loop(self):
        window_name = self._preview_window_name()
        last_preview = 0.0
        while self.preview_running:
            try:
                evs = self.event_queue.get(timeout=0.05)
            except queue.Empty:
                continue
            now = time.monotonic()
            if PREVIEW_FPS > 0 and (now - last_preview) < (1.0 / PREVIEW_FPS):
                continue
            last_preview = now
            img = self.preview_visualizer.generateImage(evs)
            cv2.imshow(window_name, img)
            key = cv2.waitKey(1) & 0xFF
            if key in (27, ord("q")):
                self.preview_running = False
                break

    def _preview_window_name(self):
        return f"DAVIS Preview - {self.label}"

    def _notify(self, msg):
        if self.status_cb:
            self.status_cb(f"DAVIS: {msg}")


class UnifiedEventGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("EVK + DAVIS Event Camera GUI")
        self.root.geometry("900x650")

        self.available_devices = []
        self.connected_devices = {}

        self.device_var = tk.StringVar()
        self.connected_var = tk.StringVar()
        self.output_dir_var = tk.StringVar(value=DEFAULT_OUTPUT_DIR)
        self.prefix_var = tk.StringVar(value=DEFAULT_PREFIX)

        self.status_queue = queue.Queue()

        self._build_ui()
        self._setup_status_updates()
        self.scan_devices()

    def _build_ui(self):
        main = ttk.Frame(self.root, padding=8)
        main.pack(fill=tk.BOTH, expand=True)

        config_box = ttk.LabelFrame(main, text="Session Output")
        config_box.pack(fill=tk.X, pady=4)

        ttk.Label(config_box, text="Output Folder:").grid(row=0, column=0, padx=5, pady=4, sticky="w")
        output_entry = ttk.Entry(config_box, textvariable=self.output_dir_var, width=50)
        output_entry.grid(row=0, column=1, padx=5, pady=4, sticky="ew")
        ttk.Button(config_box, text="Browse", command=self._select_output_dir).grid(row=0, column=2, padx=5, pady=4)

        ttk.Label(config_box, text="Prefix:").grid(row=1, column=0, padx=5, pady=4, sticky="w")
        ttk.Entry(config_box, textvariable=self.prefix_var, width=20).grid(row=1, column=1, padx=5, pady=4, sticky="w")
        config_box.columnconfigure(1, weight=1)

        device_box = ttk.LabelFrame(main, text="Device Selection")
        device_box.pack(fill=tk.X, pady=4)

        ttk.Label(device_box, text="Detected Devices:").grid(row=0, column=0, padx=5, pady=4, sticky="w")
        self.device_combo = ttk.Combobox(device_box, textvariable=self.device_var, state="readonly")
        self.device_combo.grid(row=0, column=1, padx=5, pady=4, sticky="ew")
        ttk.Button(device_box, text="Scan", command=self.scan_devices).grid(row=0, column=2, padx=5, pady=4)
        ttk.Button(device_box, text="Connect", command=self.connect_selected).grid(row=0, column=3, padx=5, pady=4)
        ttk.Button(device_box, text="Disconnect", command=self.disconnect_selected).grid(row=0, column=4, padx=5, pady=4)
        device_box.columnconfigure(1, weight=1)

        connected_box = ttk.LabelFrame(main, text="Connected Devices")
        connected_box.pack(fill=tk.X, pady=4)
        self.connected_combo = ttk.Combobox(connected_box, textvariable=self.connected_var, state="readonly")
        self.connected_combo.grid(row=0, column=0, padx=5, pady=4, sticky="ew")
        connected_box.columnconfigure(0, weight=1)

        control_box = ttk.LabelFrame(main, text="Controls")
        control_box.pack(fill=tk.X, pady=4)

        ttk.Button(control_box, text="Preview (Selected)", command=self.preview_selected).grid(row=0, column=0, padx=5, pady=4)
        ttk.Button(control_box, text="Stop Preview (Selected)", command=self.stop_preview_selected).grid(row=0, column=1, padx=5, pady=4)
        ttk.Button(control_box, text="Preview All", command=self.preview_all).grid(row=0, column=2, padx=5, pady=4)
        ttk.Button(control_box, text="Stop Preview All", command=self.stop_preview_all).grid(row=0, column=3, padx=5, pady=4)

        ttk.Button(control_box, text="Record (Selected)", command=self.record_selected).grid(row=1, column=0, padx=5, pady=4)
        ttk.Button(control_box, text="Stop Record (Selected)", command=self.stop_record_selected).grid(row=1, column=1, padx=5, pady=4)
        ttk.Button(control_box, text="Record All", command=self.record_all).grid(row=1, column=2, padx=5, pady=4)
        ttk.Button(control_box, text="Stop Record All", command=self.stop_record_all).grid(row=1, column=3, padx=5, pady=4)

        status_box = ttk.LabelFrame(main, text="Status")
        status_box.pack(fill=tk.BOTH, expand=True, pady=4)

        self.status_text = tk.Text(status_box, height=10, wrap=tk.WORD, state=tk.DISABLED)
        self.status_text.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

    def _setup_status_updates(self):
        self.root.after(200, self._flush_status)

    def _flush_status(self):
        try:
            while True:
                msg = self.status_queue.get_nowait()
                self.status_text.configure(state=tk.NORMAL)
                self.status_text.insert(tk.END, msg + "\n")
                self.status_text.see(tk.END)
                self.status_text.configure(state=tk.DISABLED)
        except queue.Empty:
            pass
        self.root.after(200, self._flush_status)

    def _status(self, msg):
        self.status_queue.put(msg)

    def _select_output_dir(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_dir_var.set(folder)

    def scan_devices(self):
        devices = []
        if DAVIS_AVAILABLE:
            try:
                for desc in dv.io.camera.discover():
                    label = f"DAVIS:{desc.serialNumber}"
                    devices.append({"label": label, "vendor": "davis", "serial": desc.serialNumber})
            except Exception as e:
                self._status(f"DAVIS discovery failed: {e}")
        elif not DAVIS_AVAILABLE:
            self._status(f"DAVIS unavailable: {DAVIS_IMPORT_ERROR}")

        if EVK_AVAILABLE:
            devices.append({"label": "EVK:auto", "vendor": "evk", "serial": None})
        else:
            self._status(f"EVK unavailable: {EVK_IMPORT_ERROR}")

        self.available_devices = devices
        labels = [d["label"] for d in devices]
        self.device_combo["values"] = labels
        if labels:
            self.device_var.set(labels[0])
        self._status(f"Detected devices: {', '.join(labels) if labels else 'none'}")

    def connect_selected(self):
        label = self.device_var.get()
        if not label:
            messagebox.showwarning("No device", "Select a device first.")
            return
        if label in self.connected_devices:
            self._status(f"Already connected: {label}")
            return
        entry = next((d for d in self.available_devices if d["label"] == label), None)
        if not entry:
            messagebox.showwarning("Invalid device", "Selected device not found.")
            return

        if entry["vendor"] == "evk":
            controller = EVKController(self._status, label)
        else:
            controller = DavisController(self._status, label, serial=entry["serial"])

        if not controller.connect():
            messagebox.showerror("Connect failed", f"Failed to connect: {label}")
            return

        self.connected_devices[label] = controller
        self._update_connected_list()
        self.connected_var.set(label)
        self._status(f"Connected: {label}")

    def disconnect_selected(self):
        label = self.connected_var.get()
        if not label or label not in self.connected_devices:
            messagebox.showwarning("No device", "Select a connected device.")
            return
        controller = self.connected_devices.pop(label)
        controller.disconnect()
        self._update_connected_list()
        self._status(f"Disconnected: {label}")

    def _update_connected_list(self):
        labels = list(self.connected_devices.keys())
        self.connected_combo["values"] = labels
        if labels and self.connected_var.get() not in labels:
            self.connected_var.set(labels[0])
        if not labels:
            self.connected_var.set("")

    def get_selected_controller(self):
        label = self.connected_var.get()
        return self.connected_devices.get(label)

    def preview_selected(self):
        controller = self.get_selected_controller()
        if not controller:
            messagebox.showwarning("No device", "Select a connected device.")
            return
        controller.start_preview()

    def stop_preview_selected(self):
        controller = self.get_selected_controller()
        if not controller:
            return
        controller.stop_preview()

    def preview_all(self):
        for controller in self.connected_devices.values():
            controller.start_preview()

    def stop_preview_all(self):
        for controller in self.connected_devices.values():
            controller.stop_preview()

    def record_selected(self):
        controller = self.get_selected_controller()
        if not controller:
            messagebox.showwarning("No device", "Select a connected device.")
            return
        run_dir = build_run_dir(self.output_dir_var.get(), self.prefix_var.get())
        vendor_dir = run_dir / device_subdir_name(controller.label)
        controller.start_recording(vendor_dir, self.prefix_var.get())

    def stop_record_selected(self):
        controller = self.get_selected_controller()
        if not controller:
            return
        controller.stop_recording()

    def record_all(self):
        if not self.connected_devices:
            messagebox.showwarning("No device", "Connect at least one device.")
            return
        run_dir = build_run_dir(self.output_dir_var.get(), self.prefix_var.get())
        for controller in self.connected_devices.values():
            vendor_dir = run_dir / device_subdir_name(controller.label)
            controller.start_recording(vendor_dir, self.prefix_var.get())

    def stop_record_all(self):
        for controller in self.connected_devices.values():
            controller.stop_recording()

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.mainloop()

    def _on_close(self):
        for controller in list(self.connected_devices.values()):
            controller.stop_all()
        self.root.destroy()


if __name__ == "__main__":
    app = UnifiedEventGUI()
    app.run()
