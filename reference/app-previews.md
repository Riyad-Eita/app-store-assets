# App previews

Source: [App preview specifications](https://developer.apple.com/help/app-store-connect/reference/app-information/app-preview-specifications)
and [asset best practices → App previews](https://developer.apple.com/app-store/asset-best-practices/#app-previews).

## Rules

- Optional, up to **3 per device size and language**. Previews always play **before** the screenshots, and up to 3 can
  show in search results.
- A preview whose aspect ratio differs from the screenshots moves to the "A Closer Look" section.
- Only screen captures of the app itself. Captions, narration, touch indicators and other overlays are allowed
  (Guideline 2.3.4).
- If a language has no preview, the one from the next best language is shown.
- Processing takes up to 24 hours after upload. Previews aren't available for iMessage-only apps.

## Technical requirements

| | H.264 | ProRes 422 (HQ only) |
|---|---|---|
| Container | `.mov`, `.m4v`, `.mp4` | `.mov` |
| Bit rate | 10–12 Mbps target | VBR ~220 Mbps |
| Video | Progressive, up to High Profile Level 4.0 | Progressive, no external references |
| Frame rate | max 30 fps | max 30 fps |
| Audio | Stereo AAC 256 kbps, 44.1 or 48 kHz | Stereo PCM (16/24/32-bit) or AAC 256 kbps, 44.1 or 48 kHz |

- Length **15–30 s**. Max file size **500 MB**.
- Stereo means one track with two channels (L, R) or two mono tracks (L, R). All tracks must be enabled.
- The **poster frame** defaults to 5 s. Set it in App Store Connect, or set `previewFrameTimeCode` on the
  `appPreview` in the API.
- iOS previews can be portrait or landscape. Previews for Mac, Apple TV and Apple Vision Pro are landscape only.

## Accepted resolutions

Use the accepted resolution, not the device's screen resolution. `Preview type` is the API's `previewType`.

| Device | Accepted (portrait / landscape) | Preview type |
|---|---|---|
| Every iPhone with Face ID or Dynamic Island, and iPhone Duo | **886×1920** / 1920×886 | `IPHONE_67`, `IPHONE_65`, `IPHONE_61`, `IPHONE_58` |
| iPhone with Home Button, large (5.5") | 1080×1920 / 1920×1080 | `IPHONE_55` |
| iPhone with Home Button, medium (4.7") | 750×1334 / 1334×750 | `IPHONE_47` |
| iPhone with Home Button, 4" | 1080×1920 / 1920×1080 | `IPHONE_40` |
| iPhone 3.5" | not supported | — |
| iPad 13", 11", 10.5" | **1200×1600** / 1600×1200 | `IPAD_PRO_3GEN_129`, `IPAD_PRO_3GEN_11`, `IPAD_105` |
| iPad 12.9" (2nd gen) | 1200×1600 or 900×1200 (and landscape) | `IPAD_PRO_129` |
| iPad 9.7" | 900×1200 / 1200×900 | `IPAD_97` |
| Mac | 1920×1080 | `DESKTOP` |
| Apple TV | 1920×1080 | `APPLE_TV` |
| Apple Vision Pro | 3840×2160 | `APPLE_VISION_PRO` |

Upload only the largest set when the UI is the same on every size, and App Store Connect scales it down. 3840×2160
doesn't fit H.264 Level 4.0, so use ProRes 422 HQ for Vision Pro previews.

## Story

- **First 2–3 seconds:** the hook. Show the value or the best feature right away, with no logo intro.
- **Beginning, middle, end:** a problem or goal, the app doing the work, a visible result. Order features by how
  popular they are, or follow how someone progresses through the app.
- **Pacing:** Hold each moment long enough to read. No quick cuts, no fast pans, no sped-up scrolling.
- **Muted first:** Short captions carry the message. If you add music, keep it to a quiet loop.
- **Loop:** The last frame should lead back into the first, for example by returning to the opening screen or using a short crossfade.
- **Poster frame:** It shows before playback and during install. Pick a frame that explains the app on its own,
  not a transition.

## Encoding

H.264 at 30 fps, with a silent stereo track when there is no music:

```sh
ffmpeg -i master.mov -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=48000 \
  -map 0:v -map 1:a -shortest \
  -vf "scale=886:1920:flags=lanczos,fps=30,format=yuv420p" \
  -c:v libx264 -profile:v high -level 4.0 -b:v 11M -maxrate 12M -bufsize 24M \
  -c:a aac -b:a 256k -ar 48000 -ac 2 -movflags +faststart preview-iphone.mp4
```

With music, use `-map 0:v -map 0:a` and drop the `anullsrc` input. Simulator and screen recordings often have a
variable frame rate, and `fps=30` makes it constant. Always check the result with `scripts/check_assets.py`.
