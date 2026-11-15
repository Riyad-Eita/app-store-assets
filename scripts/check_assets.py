#!/usr/bin/env python3
"""Check App Store images and videos against Apple's specs.

    check_assets.py PATH... [--json] [--strict]

Each file is matched to every App Store slot its size fits (screenshot, app preview, header, search results,
universal asset, In-App Event) and checked against that slot's rules. A file passes if it meets the rules of at
least one slot. Folders are scanned recursively, and each folder is also checked for too many screenshots or
previews in one slot.

Images are read with the standard library. Videos need ffprobe (part of FFmpeg).
Exit code: 0 all good, 1 at least one failure (or warning with --strict), 2 usage error.

Specs as of 2026-11-15: https://developer.apple.com/app-store/asset-best-practices/
"""
import argparse
import json
import os
import shutil
import struct
import subprocess
import sys
from collections import defaultdict

IMAGE_EXT = {".png", ".jpg", ".jpeg"}
VIDEO_EXT = {".mov", ".m4v", ".mp4"}
UNSUPPORTED_EXT = {".heic", ".heif", ".webp", ".gif", ".tif", ".tiff", ".bmp", ".avi", ".mkv", ".webm"}
MB = 1000 * 1000


def rotations(*sizes):
    out = set()
    for w, h in sizes:
        out |= {(w, h), (h, w)}
    return out


def between(lo, hi, ratio):
    """Any size from lo to hi (by width) with the given aspect ratio."""
    return lambda w, h: lo[0] <= w <= hi[0] and lo[1] <= h <= hi[1] and abs(w / h - ratio) < 0.005


# Screenshots: https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications
SCREENSHOTS = {
    "iPhone Dynamic Island, large (APP_IPHONE_67)": rotations((1320, 2868), (1290, 2796), (1260, 2736)),
    "iPhone Face ID, large (APP_IPHONE_65)": rotations((1284, 2778), (1242, 2688)),
    "iPhone Dynamic Island, medium (APP_IPHONE_61)": rotations((1206, 2622), (1179, 2556)),
    "iPhone Face ID, medium (APP_IPHONE_58)": rotations((1170, 2532), (1125, 2436), (1080, 2340)),
    "iPhone Home Button, large (APP_IPHONE_55)": rotations((1242, 2208)),
    "iPhone Home Button, medium (APP_IPHONE_47)": rotations((750, 1334)),
    "iPhone Home Button, 4\" (APP_IPHONE_40)": {(640, 1136), (640, 1096), (1136, 640), (1136, 600)},
    "iPhone Home Button, 3.5\" (APP_IPHONE_35)": {(640, 960), (640, 920), (960, 640), (960, 600)},
    "iPhone Duo, outer display": rotations((1398, 2034)),
    "iPhone Duo, inner display": rotations((2007, 2853)),
    "iPad 13\" (APP_IPAD_PRO_3GEN_129)": rotations((2064, 2752), (2048, 2732)),
    "iPad 12.9\" (APP_IPAD_PRO_129)": rotations((2048, 2732)),
    "iPad 11\" (APP_IPAD_PRO_3GEN_11)": rotations((1488, 2266), (1512, 2316), (1668, 2420), (1668, 2388), (1640, 2360)),
    "iPad 10.5\" (APP_IPAD_105)": rotations((1668, 2224)),
    "iPad 9.7\" (APP_IPAD_97)": rotations((1536, 2048), (768, 1024)) | {(1536, 2008), (768, 1004), (2048, 1496), (1024, 748)},
    "Mac (APP_DESKTOP)": {(1280, 800), (1440, 900), (2560, 1600), (2880, 1800)},
    "Apple TV (APP_APPLE_TV)": {(1920, 1080), (3840, 2160)},
    "Apple Vision Pro (APP_APPLE_VISION_PRO)": {(3840, 2160)},
    "Apple Watch": {(422, 514), (410, 502), (416, 496), (396, 484), (368, 448), (312, 390)},
}

# Creative assets: https://developer.apple.com/help/app-store-connect/reference/app-information/creative-assets-specifications
CREATIVE_IMAGES = {
    "Product page header 21:9": lambda w, h: (w, h) == (3840, 1646),
    "Search results 3:2": between((1920, 1280), (3840, 2560), 1.5),
    "Universal creative asset 16:9": lambda w, h: (w, h) == (5244, 2950),
    "In-App Event card 16:9": between((1920, 1080), (3840, 2160), 16 / 9),
    "In-App Event details 9:16": between((1080, 1920), (2160, 3840), 9 / 16),
}

# App previews: https://developer.apple.com/help/app-store-connect/reference/app-information/app-preview-specifications
PREVIEWS = {
    "iPhone app preview (Face ID, Dynamic Island, Duo)": rotations((886, 1920)),
    "iPhone app preview (Home Button 5.5\", 4\")": rotations((1080, 1920)),
    "iPhone app preview (Home Button 4.7\")": rotations((750, 1334)),
    "iPad app preview": rotations((1200, 1600), (900, 1200)),
    "Mac app preview": {(1920, 1080)},
    "Apple TV app preview": {(1920, 1080)},
    "Apple Vision Pro app preview": {(3840, 2160)},
}

CREATIVE_VIDEOS = {
    "Product page header video 21:9": lambda w, h: (w, h) == (3840, 1646),
    "Search results video 3:2": between((1920, 1280), (3840, 2560), 1.5),
    "In-App Event card video 16:9": between((1920, 1080), (3840, 2160), 16 / 9),
    "In-App Event details video 9:16": between((1080, 1920), (2160, 3840), 9 / 16),
}


# ---------------------------------------------------------------------------------------------------------- images

def read_png(f):
    """Size and whether the PNG can carry transparency (alpha channel or tRNS chunk)."""
    if f.read(8) != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG file")
    width = height = color_type = None
    while True:
        head = f.read(8)
        if len(head) < 8:
            break
        length, kind = struct.unpack(">I4s", head)
        data = f.read(length)
        f.read(4)  # CRC
        if kind == b"IHDR":
            width, height, _, color_type = struct.unpack(">IIBB", data[:10])
        elif kind == b"tRNS":
            return width, height, "has a tRNS transparency chunk"
        elif kind in (b"IDAT", b"IEND"):
            break
    if width is None:
        raise ValueError("PNG without IHDR")
    if color_type in (4, 6):
        return width, height, "has an alpha channel"
    return width, height, None


def read_jpeg(f):
    """Size and channel count from the first SOF marker."""
    if f.read(2) != b"\xff\xd8":
        raise ValueError("not a JPEG file")
    while True:
        byte = f.read(1)
        if not byte:
            raise ValueError("JPEG without a frame header")
        if byte != b"\xff":
            continue
        marker = f.read(1)
        while marker == b"\xff":
            marker = f.read(1)
        m = marker[0] if marker else 0
        if m in (0xD8, 0x01) or 0xD0 <= m <= 0xD7:
            continue
        length = struct.unpack(">H", f.read(2))[0]
        if 0xC0 <= m <= 0xCF and m not in (0xC4, 0xC8, 0xCC):
            _, height, width, channels = struct.unpack(">BHHB", f.read(6))
            return width, height, channels
        f.seek(length - 2, 1)


def check_image(path):
    errors, warnings = [], []
    ext = os.path.splitext(path)[1].lower()
    with open(path, "rb") as f:
        magic = f.read(8)
        f.seek(0)
        if magic.startswith(b"\x89PNG"):
            fmt = "png"
            w, h, alpha = read_png(f)
            if alpha:
                errors.append(alpha + " (App Store images can't have transparency; flatten to RGB)")
        elif magic.startswith(b"\xff\xd8"):
            fmt = "jpeg"
            w, h, channels = read_jpeg(f)
            if channels == 4:
                errors.append("CMYK JPEG (export as RGB)")
        else:
            return None, {}, ["not a PNG or JPEG file"], []
    if (fmt == "png") != (ext == ".png"):
        warnings.append(f"file is {fmt.upper()} but named {ext}")
    slots = [name for name, sizes in SCREENSHOTS.items() if (w, h) in sizes]
    slots += [name for name, fits in CREATIVE_IMAGES.items() if fits(w, h)]
    if not slots:
        errors.append(f"{w}×{h} fits no App Store slot")
    if "Universal creative asset 16:9" in slots and fmt != "png":
        errors.append("the universal creative asset must be PNG")
    if any(s.startswith("In-App Event") for s in slots) and os.path.getsize(path) > 500 * MB:
        errors.append("larger than 500 MB")
    return f"{w}×{h}", {"slots": slots}, errors, warnings


# ---------------------------------------------------------------------------------------------------------- videos

def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", path],
                         capture_output=True, text=True)
    if out.returncode:
        raise ValueError("ffprobe failed: " + out.stderr.strip())
    return json.loads(out.stdout)


def rate(text):
    num, _, den = (text or "0/1").partition("/")
    return float(num) / float(den or 1) if float(den or 1) else 0.0


def audio_errors(streams, allow_pcm):
    errors = []
    channels = sum(int(s.get("channels") or 0) for s in streams)
    if not (len(streams) == 1 and channels == 2) and not (len(streams) == 2 and channels == 2):
        errors.append(f"audio must be stereo: one 2-channel track or two mono tracks (found {len(streams)} track(s), "
                      f"{channels} channel(s))")
    for s in streams:
        codec = s.get("codec_name", "")
        if not (codec == "aac" or (allow_pcm and codec.startswith("pcm_s"))):
            errors.append(f"audio codec {codec} (needs AAC" + (" or PCM)" if allow_pcm else ")"))
        if s.get("sample_rate") not in ("44100", "48000"):
            errors.append(f"audio sample rate {s.get('sample_rate')} Hz (needs 44.1 or 48 kHz)")
    return errors


def preview_rules(v, audio, duration, size):
    errors, warnings = [], []
    if not 15 <= duration <= 30.05:
        errors.append(f"length {duration:.2f} s (app previews: 15–30 s)")
    fps = max(rate(v.get("r_frame_rate")), rate(v.get("avg_frame_rate")))
    if fps > 30.01:
        errors.append(f"{fps:.2f} fps (app previews: max 30; variable-rate recordings: re-encode with fps=30)")
    codec, profile = v.get("codec_name"), (v.get("profile") or "")
    if codec == "h264":
        if v.get("level", 0) > 40:
            errors.append(f"H.264 level {v['level'] / 10:.1f} (max 4.0; encode with -level 4.0, or ProRes 422 HQ above 1080p)")
        if profile not in ("High", "Main", "Constrained Baseline", "Baseline"):
            errors.append(f"H.264 profile {profile} (up to High)")
    elif codec == "prores":
        if profile != "HQ":
            errors.append(f"ProRes profile {profile} (only ProRes 422 HQ)")
    else:
        errors.append(f"codec {codec} (needs H.264 or ProRes 422 HQ)")
    if v.get("field_order") not in (None, "progressive", "unknown"):
        errors.append("interlaced video (needs progressive)")
    if size > 500 * MB:
        errors.append(f"{size / MB:.0f} MB (max 500)")
    if audio:
        errors += audio_errors(audio, allow_pcm=codec == "prores")
    else:
        warnings.append("no audio track (the spec describes stereo audio; a silent stereo track is the safe choice)")
    return errors, warnings


def creative_rules(name, v, audio, duration, size):
    errors = []
    if not 5 <= duration <= 30.05:
        errors.append(f"length {duration:.2f} s (5–30 s)")
    fps = rate(v.get("avg_frame_rate")) or rate(v.get("r_frame_rate"))
    if not any(abs(fps - target) < 0.1 for target in (29.97, 30, 59.94, 60)):
        errors.append(f"{fps:.2f} fps (30 or 60)")
    if name.startswith("In-App Event") and size > 500 * MB:
        errors.append(f"{size / MB:.0f} MB (max 500)")
    if audio:
        errors += audio_errors(audio, allow_pcm="details" in name)
    return errors, []


def check_video(path):
    data = probe(path)
    streams = data.get("streams", [])
    v = next((s for s in streams if s.get("codec_type") == "video"), None)
    if not v:
        return None, {}, ["no video stream"], []
    audio = [s for s in streams if s.get("codec_type") == "audio"]
    w, h = int(v["width"]), int(v["height"])
    duration = float(data["format"].get("duration") or v.get("duration") or 0)
    size = os.path.getsize(path)
    fps = rate(v.get("avg_frame_rate"))
    label = f"{w}×{h}, {duration:.1f} s, {fps:.0f} fps"

    candidates = [(n, "preview") for n, s in PREVIEWS.items() if (w, h) in s]
    candidates += [(n, "creative") for n, fits in CREATIVE_VIDEOS.items() if fits(w, h)]
    if not candidates:
        return label, {"slots": []}, [f"{w}×{h} fits no app preview or creative video slot"], []

    results = []
    for name, kind in candidates:
        errs, warns = (preview_rules(v, audio, duration, size) if kind == "preview"
                       else creative_rules(name, v, audio, duration, size))
        results.append((name, errs, warns))
    passing = [r for r in results if not r[1]]
    if passing:
        warnings = sorted({w for r in passing for w in r[2]})
        return label, {"slots": [r[0] for r in passing]}, [], warnings
    errors = [f"as {name}: {e}" for name, errs, _ in results for e in errs]
    return label, {"slots": []}, errors, []


# ---------------------------------------------------------------------------------------------------------- main

def collect(paths):
    files = []
    for p in paths:
        if os.path.isdir(p):
            for root, dirs, names in os.walk(p):
                dirs[:] = sorted(d for d in dirs if not d.startswith("."))
                files += [os.path.join(root, n) for n in sorted(names) if not n.startswith(".")]
        elif os.path.exists(p):
            files.append(p)
        else:
            raise SystemExit(f"check_assets: no such file or folder: {p}")
    return files


def main(argv=None):
    ap = argparse.ArgumentParser(description="Check App Store images and videos against Apple's specs.")
    ap.add_argument("paths", nargs="+", help="files or folders")
    ap.add_argument("--json", action="store_true", help="print results as JSON")
    ap.add_argument("--strict", action="store_true", help="treat warnings as failures")
    args = ap.parse_args(argv)

    results = []
    for path in collect(args.paths):
        ext = os.path.splitext(path)[1].lower()
        if ext in UNSUPPORTED_EXT:
            results.append({"file": path, "info": None, "slots": [], "warnings": [],
                            "errors": [f"{ext} isn't accepted (images: .png/.jpg/.jpeg, videos: .mov/.m4v/.mp4)"]})
            continue
        if ext not in IMAGE_EXT | VIDEO_EXT:
            continue
        if ext in VIDEO_EXT and not shutil.which("ffprobe"):
            results.append({"file": path, "info": None, "slots": [], "warnings": [],
                            "errors": ["ffprobe not found (install FFmpeg to check videos)"]})
            continue
        try:
            info, extra, errors, warnings = (check_image if ext in IMAGE_EXT else check_video)(path)
        except (ValueError, OSError, struct.error, KeyError) as e:
            info, extra, errors, warnings = None, {}, [f"can't read: {e}"], []
        results.append({"file": path, "info": info, "slots": extra.get("slots", []),
                        "errors": errors, "warnings": warnings, "video": ext in VIDEO_EXT})

    # Per folder: at most 10 screenshots and 3 previews in one slot (per language, which is usually a folder).
    groups = defaultdict(list)
    for r in results:
        if not r["errors"] and r["slots"]:
            groups[(os.path.dirname(r["file"]), r["slots"][0], r.get("video"))].append(r)
    for (folder, slot, video), members in groups.items():
        limit = 3 if video and slot in PREVIEWS else 10 if not video and slot in SCREENSHOTS else None
        if limit and len(members) > limit:
            what = "app previews" if video else "screenshots"
            for r in members:
                r["errors"].append(f"{len(members)} {what} for {slot} in {folder or '.'} (max {limit})")

    for r in results:
        r["ok"] = not (r["errors"] or (args.strict and r["warnings"]))
        r.pop("video", None)
    failed = sum(not r["ok"] for r in results)
    if args.json:
        print(json.dumps({"files": results, "failed": failed}, indent=2, ensure_ascii=False))
    else:
        for r in results:
            mark = "FAIL" if not r["ok"] else "warn" if r["warnings"] else "ok  "
            slots = "; ".join(r["slots"]) or "-"
            print(f"{mark}  {r['file']}  {r['info'] or ''}  [{slots}]")
            for e in r["errors"]:
                print(f"        x {e}")
            for w in r["warnings"]:
                print(f"        ! {w}")
        print(f"\n{len(results)} file(s), {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
