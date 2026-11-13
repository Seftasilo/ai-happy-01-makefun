#!/usr/bin/env python3
"""ai-happy-01 entry (make.fun "Make the AI judge happy").

The art is the entry.png bundled beside this file: "Best Judge Ever!",
a small robot judge in a wig on a podium in a sunny park, holding a
giant sunflower like a trophy while children, a puppy, a kitten and a
rabbit cheer under a hand-painted banner that reads BEST JUDGE EVER!

This program copies those exact bytes to /output/entry.png. It uses only
the Python standard library, touches no network, reads no clock, and
writes the same bytes on every run, so two runs are byte-identical.
"""

import hashlib
import os
import sys


def sha256_of(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def jpeg_dimensions(data: bytes) -> tuple:
    """Return (width, height) from the first SOF marker, or (0, 0).

    Walks the JPEG marker segments after the SOI marker; SOF0/SOF2
    carry height then width as big-endian 16-bit values. Returns
    (0, 0) when no SOF marker is found, so callers can treat an
    unparseable header as a failure instead of guessing.
    """
    i = 2  # skip SOI (FF D8)
    while i + 9 < len(data):
        if data[i] != 0xFF:
            return (0, 0)
        marker = data[i + 1]
        if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
            i += 2
            continue
        seg_len = int.from_bytes(data[i + 2:i + 4], "big")
        if marker in (0xC0, 0xC1, 0xC2):
            height = int.from_bytes(data[i + 5:i + 7], "big")
            width = int.from_bytes(data[i + 7:i + 9], "big")
            return (width, height)
        i += 2 + seg_len
    return (0, 0)


def main() -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, "entry.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    if not out_dir:
        # An explicitly empty MAKEFUN_OUTPUT_DIR must not resolve the
        # target into the current working directory; fall back to the
        # default output directory instead.
        out_dir = "/output"
    target = os.path.join(out_dir, "entry.png")

    with open(source, "rb") as f:
        data = f.read()

    # An empty file is not an image at all: refuse it with a clear
    # message before any later check can misread it as a bad header.
    if len(data) == 0:
        print("entry.png: empty file (0 bytes)", file=sys.stderr)
        return 1

    # The bundled art must be a real JPEG: refuse anything else before
    # writing, so a wrong file can never be submitted silently.
    if data[:3] != b"\xff\xd8\xff":
        print("entry.png: not a JPEG file", file=sys.stderr)
        return 1

    # The gate caps the image at 1 MiB: refuse an oversize file before
    # writing, so a bad resize can never be submitted silently.
    if len(data) > 1048576:
        print(f"entry.png: {len(data)} bytes exceeds the 1 MiB gate",
              file=sys.stderr)
        return 1

    # A whole JPEG ends with the EOI marker: refuse a truncated file,
    # since the gate scores only complete images.
    if data[-2:] != b"\xff\xd9":
        print("entry.png: truncated JPEG (no EOI marker)",
              file=sys.stderr)
        return 1

    # The gate caps images at 1024x1024: refuse anything larger before
    # writing, so an oversize resize can never be submitted silently.
    width, height = jpeg_dimensions(data)
    if width == 0 or height == 0:
        print("entry.png: no SOF marker (unparseable JPEG header)",
              file=sys.stderr)
        return 1
    if width > 1024 or height > 1024:
        print(f"entry.png: {width}x{height} exceeds the 1024x1024 gate",
              file=sys.stderr)
        return 1

    # A real JPEG carries at least one SOS (start of scan) marker with
    # image data behind it: refuse a header-only file, since the gate
    # scores the picture, not an empty frame.
    if b"\xff\xda" not in data:
        print("entry.png: no SOS marker (no image data)",
              file=sys.stderr)
        return 1

    os.makedirs(out_dir, exist_ok=True)
    with open(target, "wb") as f:
        f.write(data)

    # Confirm the copy is byte-identical, not just the same length: a
    # same-length but corrupted write must fail loudly, since the gate
    # scores the exact bytes written.
    written = os.path.getsize(target)
    digest = sha256_of(target)
    if written != len(data) or digest != sha256_of(source):
        print(f"entry.png: copy failed integrity check "
              f"(wrote {written} of {len(data)} bytes)",
              file=sys.stderr)
        return 1
    print(f"entry.png: {written} bytes -> {target} (sha256 {digest})",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
