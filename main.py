#!/usr/bin/env python3
"""Copy the bundled happy-image JPEG to the scorer's output folder.

The image itself lives next to this file as ``entry.png`` (a JPEG despite
the name).  This script only validates it against the competition limits
and copies it, byte for byte, to ``$MAKEFUN_OUTPUT_DIR/entry.png``.
Standard library only, no network, no clock.
"""

import os
import sys
from pathlib import Path

MAX_BYTES = 1_048_576          # 1 MiB
MAX_SIDE = 1024                # longest allowed edge, in pixels
JPEG_SOI = b"\xff\xd8\xff"     # start-of-image magic
JPEG_EOI = b"\xff\xd9"         # end-of-image marker
JPEG_SOS = b"\xff\xda"         # start-of-scan marker
SOF_MARKERS = {0xC0, 0xC2}     # baseline + progressive DCT frames


def complain(message: str) -> int:
    """Print a one-line error to stderr and report failure."""
    print(f"entry: error: {message}", file=sys.stderr)
    return 1


def jpeg_dimensions(blob: bytes):
    """Return (width, height) read from the first SOF0/SOF2 segment.

    Walks the JPEG marker stream starting after the SOI marker.  Returns
    ``None`` when no SOF segment is found or the stream is truncated.
    """
    pos = 2  # skip the SOI marker
    end = len(blob)
    while pos + 1 < end:
        if blob[pos] != 0xFF:
            # Padding / stray byte: move on one byte at a time.
            pos += 1
            continue
        marker = blob[pos + 1]
        if marker == 0xFF:
            pos += 1
            continue
        if marker in (0x00, 0x01) or 0xD0 <= marker <= 0xD9:
            # Standalone markers (RSTn, SOI, EOI, TEM) carry no length.
            pos += 2
            continue
        if pos + 4 > end:
            return None
        seg_len = (blob[pos + 2] << 8) | blob[pos + 3]
        if seg_len < 2 or pos + 2 + seg_len > end:
            return None
        if marker in SOF_MARKERS:
            # SOF payload: precision (1), height (2), width (2), ...
            if seg_len < 7:
                return None
            height = (blob[pos + 5] << 8) | blob[pos + 6]
            width = (blob[pos + 7] << 8) | blob[pos + 8]
            return width, height
        if marker == 0xDA:
            # Start of scan: entropy data follows, no SOF can come after.
            return None
        pos += 2 + seg_len
    return None


def check_image(blob: bytes) -> str | None:
    """Validate the JPEG bytes; return an error string or None when fine."""
    if not blob:
        return "entry.png is empty"
    if len(blob) > MAX_BYTES:
        return f"entry.png is {len(blob)} bytes, over the 1048576 byte limit"
    if blob[:3] != JPEG_SOI:
        return "entry.png does not start with the JPEG magic bytes FF D8 FF"
    if JPEG_SOS not in blob:
        return "entry.png has no SOS (FF DA) marker"
    if blob[-2:] != JPEG_EOI:
        return "entry.png does not end with the EOI marker FF D9"
    size = jpeg_dimensions(blob)
    if size is None:
        return "entry.png has no readable SOF0/SOF2 segment"
    width, height = size
    if width <= 0 or height <= 0:
        return f"entry.png has invalid dimensions {width}x{height}"
    if width > MAX_SIDE or height > MAX_SIDE:
        return f"entry.png is {width}x{height}, over the 1024x1024 limit"
    return None


def run() -> int:
    here = Path(__file__).resolve().parent
    source = here / "entry.png"
    if not source.is_file():
        return complain("entry.png is missing next to main.py")

    try:
        blob = source.read_bytes()
    except OSError as exc:
        return complain(f"cannot read entry.png: {exc}")

    problem = check_image(blob)
    if problem is not None:
        return complain(problem)

    out_dir = (os.environ.get("MAKEFUN_OUTPUT_DIR") or "").strip() or "/output"
    target = Path(out_dir) / "entry.png"
    if target.resolve() == source.resolve():
        # Copying onto itself would prove nothing; refuse instead.
        return complain("output entry.png would overwrite the source file")
    out_path = Path(out_dir)
    if out_path.exists() and not out_path.is_dir():
        return complain(f"output path {out_dir} exists and is not a directory")
    try:
        out_path.mkdir(parents=True, exist_ok=True)
        target.write_bytes(blob)
    except OSError as exc:
        return complain(f"cannot write {target}: {exc}")

    try:
        written = target.read_bytes()
    except OSError as exc:
        return complain(f"cannot re-read {target}: {exc}")
    if written != blob:
        return complain("written entry.png differs from the source bytes")

    print(f"wrote {target} ({len(blob)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
