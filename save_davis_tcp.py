#!/usr/bin/env python3
import time
from pathlib import Path

import cv2
import dv
import numpy as np


HOST = "127.0.0.1"
EVENTS_PORT = 7777
FRAMES_PORT = 7778

OUT_DIR = Path("davis_output")
EVENTS_DIR = OUT_DIR / "events"
FRAMES_DIR = OUT_DIR / "frames"

SAVE_EVENTS_NPZ = True
SAVE_FRAMES_PNG = True
SAVE_AEDAT4 = False

EVENTS_PER_CHUNK = 500_000


def save_events_npz(events_np: np.ndarray, path: Path) -> None:
    np.savez_compressed(
        path,
        t=events_np["timestamp"],
        x=events_np["x"],
        y=events_np["y"],
        p=events_np["polarity"],
    )


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)
    if SAVE_EVENTS_NPZ:
        EVENTS_DIR.mkdir(exist_ok=True)
    if SAVE_FRAMES_PNG:
        FRAMES_DIR.mkdir(exist_ok=True)

    print(f"Connecting to DV TCP servers at {HOST}:{EVENTS_PORT} and {HOST}:{FRAMES_PORT}")
    event_input = dv.io.NetworkEventInput(host=HOST, port=EVENTS_PORT)
    frame_input = dv.io.NetworkFrameInput(host=HOST, port=FRAMES_PORT)

    aedat_writer = None
    if SAVE_AEDAT4:
        aedat_path = OUT_DIR / "output.aedat4"
        aedat_writer = dv.io.AedatFileWriter(str(aedat_path))
        print(f"Writing AEDAT4 to {aedat_path}")

    event_chunks = []
    event_chunk_count = 0
    chunk_index = 0
    frame_index = 0

    try:
        while True:
            got_data = False

            events = event_input.read()
            if events is not None and not events.isEmpty():
                got_data = True
                if aedat_writer:
                    aedat_writer.writeEvents(events)
                if SAVE_EVENTS_NPZ:
                    ev_np = events.numpy()
                    event_chunks.append(ev_np)
                    event_chunk_count += len(ev_np)
                    if event_chunk_count >= EVENTS_PER_CHUNK:
                        events_np = np.concatenate(event_chunks)
                        out_path = EVENTS_DIR / f"events_{chunk_index:06d}.npz"
                        save_events_npz(events_np, out_path)
                        print(f"[EVENTS] wrote {len(events_np)} events to {out_path.name}")
                        event_chunks.clear()
                        event_chunk_count = 0
                        chunk_index += 1

            frame = frame_input.read()
            if frame is not None:
                got_data = True
                if aedat_writer:
                    aedat_writer.writeFrame(frame)
                if SAVE_FRAMES_PNG:
                    img = frame.image
                    ts = frame.timestamp
                    out_path = FRAMES_DIR / f"frame_{frame_index:06d}_{ts}.png"
                    cv2.imwrite(str(out_path), img)
                    print(f"[FRAME] saved {out_path.name}")
                    frame_index += 1

            if not got_data:
                time.sleep(0.001)
    except KeyboardInterrupt:
        print("Stopping capture...")
    finally:
        if SAVE_EVENTS_NPZ and event_chunks:
            events_np = np.concatenate(event_chunks)
            out_path = EVENTS_DIR / f"events_{chunk_index:06d}.npz"
            save_events_npz(events_np, out_path)
            print(f"[EVENTS] wrote {len(events_np)} events to {out_path.name}")
        if aedat_writer:
            aedat_writer.close()
        print("Done.")


if __name__ == "__main__":
    main()
