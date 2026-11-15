import contextlib
import io
import json
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import check_assets  # noqa: E402

HAS_FFMPEG = bool(shutil.which("ffmpeg") and shutil.which("ffprobe"))


def png(path, w, h, color_type=2, trns=False):
    """A tiny valid PNG header + one empty IDAT; enough for the checker, which never decodes pixels."""
    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))
    body = chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, color_type, 0, 0, 0))
    if trns:
        body += chunk(b"tRNS", b"\x00\x00")
    body += chunk(b"IDAT", zlib.compress(b"")) + chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n" + body)


def jpeg(path, w, h, channels=3):
    app0 = b"\xff\xe0" + struct.pack(">H", 16) + b"JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
    sof = b"\xff\xc0" + struct.pack(">HBHHB", 8 + 3 * channels, 8, h, w, channels) + b"\x01\x11\x00" * channels
    with open(path, "wb") as f:
        f.write(b"\xff\xd8" + app0 + sof + b"\xff\xd9")


def video(path, w, h, seconds, fps=30, audio="stereo"):
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"color=c=gray:s={w}x{h}:r={fps}:d={seconds}"]
    if audio:
        layout = "stereo" if audio == "stereo" else "mono"
        cmd += ["-f", "lavfi", "-i", f"anullsrc=channel_layout={layout}:sample_rate=48000", "-shortest",
                "-c:a", "aac", "-b:a", "256k"]
    cmd += ["-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-profile:v", "high", path]
    subprocess.run(cmd, check=True)


class Base(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.dir)

    def path(self, name):
        return os.path.join(self.dir, name)

    def run_checker(self, *paths, strict=False):
        args = [*paths, "--json"] + (["--strict"] if strict else [])
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = check_assets.main(args)
        return code, json.loads(out.getvalue())

    def one(self, path, **kw):
        code, report = self.run_checker(path, **kw)
        return code, report["files"][0]


class ImageTests(Base):
    def test_iphone_screenshot_passes(self):
        png(self.path("a.png"), 1320, 2868)
        code, r = self.one(self.path("a.png"))
        self.assertEqual(code, 0)
        self.assertIn("iPhone Dynamic Island, large (APP_IPHONE_67)", r["slots"])

    def test_landscape_and_jpeg_pass(self):
        jpeg(self.path("a.jpg"), 2868, 1320)
        self.assertEqual(self.one(self.path("a.jpg"))[0], 0)

    def test_alpha_channel_fails(self):
        png(self.path("a.png"), 1320, 2868, color_type=6)
        code, r = self.one(self.path("a.png"))
        self.assertEqual(code, 1)
        self.assertIn("alpha", r["errors"][0])

    def test_trns_transparency_fails(self):
        png(self.path("a.png"), 2064, 2752, color_type=2, trns=True)
        self.assertEqual(self.one(self.path("a.png"))[0], 1)

    def test_unknown_size_fails(self):
        png(self.path("a.png"), 1080, 1080)
        code, r = self.one(self.path("a.png"))
        self.assertEqual(code, 1)
        self.assertIn("fits no App Store slot", r["errors"][0])

    def test_universal_asset_must_be_png(self):
        jpeg(self.path("u.jpg"), 5244, 2950)
        code, r = self.one(self.path("u.jpg"))
        self.assertEqual(code, 1)
        self.assertTrue(any("must be PNG" in e for e in r["errors"]))
        png(self.path("u.png"), 5244, 2950)
        self.assertEqual(self.one(self.path("u.png"))[0], 0)

    def test_search_results_range(self):
        png(self.path("s.png"), 2880, 1920)
        code, r = self.one(self.path("s.png"))
        self.assertEqual(code, 0)
        self.assertIn("Search results 3:2", r["slots"])
        png(self.path("small.png"), 1500, 1000)
        self.assertEqual(self.one(self.path("small.png"))[0], 1)

    def test_header_and_events(self):
        png(self.path("h.png"), 3840, 1646)
        self.assertIn("Product page header 21:9", self.one(self.path("h.png"))[1]["slots"])
        png(self.path("d.png"), 1080, 1920)
        self.assertIn("In-App Event details 9:16", self.one(self.path("d.png"))[1]["slots"])

    def test_mac_is_landscape_only(self):
        png(self.path("m.png"), 2880, 1800)
        self.assertEqual(self.one(self.path("m.png"))[0], 0)
        png(self.path("p.png"), 1800, 2880)
        self.assertEqual(self.one(self.path("p.png"))[0], 1)

    def test_cmyk_jpeg_fails(self):
        jpeg(self.path("c.jpg"), 1320, 2868, channels=4)
        self.assertEqual(self.one(self.path("c.jpg"))[0], 1)

    def test_wrong_extension_warns_and_strict_fails(self):
        jpeg(self.path("a.png"), 1320, 2868)
        code, r = self.one(self.path("a.png"))
        self.assertEqual(code, 0)
        self.assertTrue(r["warnings"])
        self.assertEqual(self.one(self.path("a.png"), strict=True)[0], 1)

    def test_unsupported_format_fails(self):
        open(self.path("a.heic"), "wb").close()
        self.assertEqual(self.one(self.path("a.heic"))[0], 1)

    def test_more_than_ten_screenshots_in_a_folder_fail(self):
        for i in range(11):
            png(self.path(f"{i:02d}.png"), 1320, 2868)
        code, report = self.run_checker(self.dir)
        self.assertEqual(code, 1)
        self.assertEqual(report["failed"], 11)

    def test_ten_screenshots_are_fine_and_other_files_are_ignored(self):
        for i in range(10):
            png(self.path(f"{i:02d}.png"), 1320, 2868)
        open(self.path("notes.txt"), "w").close()
        code, report = self.run_checker(self.dir)
        self.assertEqual(code, 0)
        self.assertEqual(len(report["files"]), 10)


@unittest.skipUnless(HAS_FFMPEG, "needs ffmpeg and ffprobe")
class VideoTests(Base):
    def test_iphone_preview_passes(self):
        video(self.path("p.mp4"), 886, 1920, 16)
        code, r = self.one(self.path("p.mp4"))
        self.assertEqual(code, 0, r)
        self.assertEqual(r["slots"], ["iPhone app preview (Face ID, Dynamic Island, Duo)"])

    def test_preview_too_short_fails(self):
        video(self.path("p.mp4"), 886, 1920, 10)
        code, r = self.one(self.path("p.mp4"))
        self.assertEqual(code, 1)
        self.assertTrue(any("15–30 s" in e for e in r["errors"]))

    def test_preview_60fps_fails(self):
        video(self.path("p.mp4"), 886, 1920, 16, fps=60)
        code, r = self.one(self.path("p.mp4"))
        self.assertEqual(code, 1)
        self.assertTrue(any("max 30" in e for e in r["errors"]))

    def test_preview_mono_audio_fails(self):
        video(self.path("p.mp4"), 886, 1920, 16, audio="mono")
        self.assertEqual(self.one(self.path("p.mp4"))[0], 1)

    def test_preview_without_audio_warns(self):
        video(self.path("p.mp4"), 886, 1920, 16, audio=None)
        code, r = self.one(self.path("p.mp4"))
        self.assertEqual(code, 0)
        self.assertTrue(any("no audio" in w for w in r["warnings"]))

    def test_1920x1080_short_clip_is_a_valid_event_card(self):
        # Too short for a Mac preview, fine as an In-App Event card video.
        video(self.path("e.mp4"), 1920, 1080, 8, audio=None)
        code, r = self.one(self.path("e.mp4"))
        self.assertEqual(code, 0, r)
        self.assertEqual(r["slots"], ["In-App Event card video 16:9"])

    def test_header_video_60fps_passes(self):
        video(self.path("h.mp4"), 3840, 1646, 6, fps=60, audio=None)
        self.assertEqual(self.one(self.path("h.mp4"))[0], 0)

    def test_reel_sized_video_fails(self):
        video(self.path("r.mp4"), 1080, 1350, 6)
        self.assertEqual(self.one(self.path("r.mp4"))[0], 1)


if __name__ == "__main__":
    unittest.main()
