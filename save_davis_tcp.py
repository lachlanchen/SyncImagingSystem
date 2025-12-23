#!/usr/bin/env python3
import time
from datetime import datetime
from pathlib import Path

import cv2
try:
    import dv_processing as dv
    DV_MODULE = "dv_processing"
except ImportError:
    import dv
    DV_MODULE = "dv"
import numpy as np


HOST = "127.0.0.1"
EVENTS_PORT = 7777
FRAMES_PORT = 7778

OUT_DIR = Path("davis_output")

SAVE_EVENTS_NPZ = True
SAVE_FRAMES_VIDEO = True
SAVE_AEDAT4 = True

CAPTURE_SECONDS = 3.0
VIDEO_FPS = 30.0
VIDEO_FOURCC = "MJPG"


def _create_network_input(cls, host: str, port: int):
    try:
        return cls(host=host, port=port)
    except TypeError:
        try:
            return cls(address=host, port=port)
        except TypeError:
            return cls(host, port)


def save_events_npz(events_np: np.ndarray, path: Path) -> None:
    np.savez_compressed(
        path,
        t=events_np["timestamp"],
        x=events_np["x"],
        y=events_np["y"],
        p=events_np["polarity"],
    )


def build_inputs():
    if DV_MODULE == "dv_processing" and hasattr(dv, "io") and hasattr(dv.io, "NetworkReader"):
        event_input = _create_network_input(dv.io.NetworkReader, HOST, EVENTS_PORT)
        frame_input = _create_network_input(dv.io.NetworkReader, HOST, FRAMES_PORT)
        return "dv_processing", event_input, frame_input
    try:
        from dv.NetworkInput import NetworkInput

        event_input = NetworkInput(address=HOST, port=EVENTS_PORT, as_numpy=True)
        frame_input = NetworkInput(address=HOST, port=FRAMES_PORT)
        return "dv_python", event_input, frame_input
    except Exception:
        if hasattr(dv, "NetworkFrameInput"):
            event_input = dv.NetworkNumpyEventPacketInput(address=HOST, port=EVENTS_PORT)
            frame_input = dv.NetworkFrameInput(address=HOST, port=FRAMES_PORT)
            return "dv_python", event_input, frame_input
    raise RuntimeError("Unsupported dv package: missing dv.io and NetworkFrameInput")


def read_events(backend: str, event_input):
    if backend == "dv_processing":
        events = event_input.getNextEventBatch()
        if events is None or events.isEmpty():
            return None, None
        return events.numpy(), events
    try:
        events_np = next(event_input)
    except StopIteration:
        return None, None
    if events_np is None or len(events_np) == 0:
        return None, None
    return events_np, None


def read_frame(backend: str, frame_input):
    if backend == "dv_processing":
        return frame_input.getNextFrame()
    try:
        return next(frame_input)
    except StopIteration:
        return None


def _get_frame_image(frame):
    img = frame.image
    if callable(img):
        return img()
    return img


def _get_frame_timestamp(frame):
    ts = frame.timestamp
    if callable(ts):
        return ts()
    return ts


def _safe_call(obj, method_name):
    try:
        return getattr(obj, method_name)()
    except Exception:
        return None


def build_aedat_writer(backend: str, event_input, frame_input, run_dir: Path):
    if not SAVE_AEDAT4:
        return None
    if backend != "dv_processing":
        print("SAVE_AEDAT4 requires dv-processing; disabling AEDAT4 output.")
        return None
    if not hasattr(dv.io, "MonoCameraWriter"):
        print("MonoCameraWriter not available; disabling AEDAT4 output.")
        return None

    camera_name = _safe_call(event_input, "getCameraName") or _safe_call(frame_input, "getCameraName") or "DV"
    cfg = dv.io.MonoCameraWriter.Config(camera_name)

    event_res = _safe_call(event_input, "getEventResolution")
    frame_res = _safe_call(frame_input, "getFrameResolution")
    if event_res is None and frame_res is not None:
        event_res = frame_res
    if frame_res is None and event_res is not None:
        frame_res = event_res

    if event_res is not None:
        cfg.addEventStream(event_res)
    if frame_res is not None:
        cfg.addFrameStream(frame_res)

    aedat_path = run_dir / "output.aedat4"
    writer = dv.io.MonoCameraWriter(str(aedat_path), cfg)
    print(f"Writing AEDAT4 to {aedat_path}")
    return writer


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)
    run_dir = OUT_DIR / datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir.mkdir(parents=True, exist_ok=True)
    events_file = run_dir / "events.npz"
    frames_file = run_dir / "frames.avi"

    print(f"Connecting to DV TCP servers at {HOST}:{EVENTS_PORT} and {HOST}:{FRAMES_PORT}")
    backend, event_input, frame_input = build_inputs()
    print(f"Using dv backend: {backend} ({DV_MODULE})")
    print(f"Output directory: {run_dir}")

    aedat_writer = build_aedat_writer(backend, event_input, frame_input, run_dir)

    event_chunks = []
    frame_index = 0
    start_time = time.monotonic()
    video_writer = None
    video_is_color = None

    try:
        while True:
            got_data = False

            events_np, events_obj = read_events(backend, event_input)
            if events_np is not None:
                got_data = True
                if aedat_writer and events_obj is not None:
                    aedat_writer.writeEvents(events_obj)
                if SAVE_EVENTS_NPZ:
                    event_chunks.append(events_np)

            frame = read_frame(backend, frame_input)
            if frame is not None:
                got_data = True
                if aedat_writer:
                    aedat_writer.writeFrame(frame)
                if SAVE_FRAMES_VIDEO:
                    img = _get_frame_image(frame)
                    ts = _get_frame_timestamp(frame)
                    if img.ndim == 3 and img.shape[2] == 4:
                        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                    if img.ndim == 3 and img.shape[2] == 1:
                        img = img[:, :, 0]
                    if video_writer is None:
                        height, width = img.shape[:2]
                        video_is_color = img.ndim == 3
                        fourcc = cv2.VideoWriter_fourcc(*VIDEO_FOURCC)
                        video_writer = cv2.VideoWriter(
                            str(frames_file),
                            fourcc,
                            VIDEO_FPS,
                            (width, height),
                            isColor=video_is_color,
                        )
                        if not video_writer.isOpened():
                            raise RuntimeError(f"Failed to open video writer for {frames_file}")
                    if video_is_color and img.ndim == 2:
                        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
                    if not video_is_color and img.ndim == 3:
                        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    video_writer.write(img)
                    print(f"[FRAME] wrote frame {frame_index:06d} ts={ts}")
                    frame_index += 1

            if CAPTURE_SECONDS is not None:
                if (time.monotonic() - start_time) >= CAPTURE_SECONDS:
                    print(f"Capture time reached ({CAPTURE_SECONDS:.1f}s).")
                    break

            if not got_data:
                time.sleep(0.001)
    except KeyboardInterrupt:
        print("Stopping capture...")
    finally:
        if SAVE_EVENTS_NPZ and event_chunks:
            events_np = np.concatenate(event_chunks)
            save_events_npz(events_np, events_file)
            print(f"[EVENTS] wrote {len(events_np)} events to {events_file.name}")
        if aedat_writer:
            for method_name in ("close", "finish", "flush", "release"):
                close_fn = getattr(aedat_writer, method_name, None)
                if close_fn:
                    try:
                        close_fn()
                    except Exception:
                        pass
                    break
        if video_writer is not None:
            video_writer.release()
        print("Done.")


if __name__ == "__main__":
    main()
