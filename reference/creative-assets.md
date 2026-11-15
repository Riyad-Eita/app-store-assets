# Creative assets and In-App Events

Source: [Creative assets specifications](https://developer.apple.com/help/app-store-connect/reference/app-information/creative-assets-specifications),
[In-App Event media and audio specifications](https://developer.apple.com/help/app-store-connect/reference/in-app-events/in-app-event-media-and-audio-specifications)
and the asset guide's sections on the [header](https://developer.apple.com/app-store/asset-best-practices/#header),
[search results](https://developer.apple.com/app-store/asset-best-practices/#search-results) and
[In-App Events](https://developer.apple.com/app-store/asset-best-practices/#in-app-events).

Creative assets appear on iOS 27 and iPadOS 27 and later: in the product page header, in search results, and when the
app is featured. Unlike screenshots, they can show the brand, seasonal content or new content. They still have to be
about the app, appropriate for all ages, and free of pricing, unverifiable claims and misleading references to other
apps (Guideline 2.3.14).

## Product page header

- **One clear idea.** Dense or busy art weakens the message.
- **Design for a first-time visitor:** what would convince someone who has never heard of the app?
- Test alternative headers with product page optimization.

## Search results

- **Make the purpose obvious at a glance.** People come to search looking for something specific.
- **Show the first-hand experience:** the interface, the content or the gameplay.
- Without search art, In-App Events, previews and screenshots show instead.

## Image specs

No alpha channel or transparency.

| Placement | Ratio | Size (px) | Art safe area (w×h at x, y) | Format |
|---|---|---|---|---|
| Product page header | 21:9 | 3840×1646 | 1646×661 at 1097, 493 | `.jpg`, `.jpeg`, `.png` |
| Search results | 3:2 | 1920×1280 – 3840×2560 | max 2168×1030 at 836, 765 | `.jpg`, `.jpeg`, `.png` |
| Universal (header + search) | 16:9 | 5244×2950 | 1402×962 at 1921, 660 | **`.png` only** |

- **Art Safe Area:** the main subject and every critical element. This area stays visible on every device and orientation.
- **Auxiliary Art Area:** atmosphere and background that fill the rest of the canvas and get cropped as needed.
- The **universal asset** serves both placements with one file. Apple requires PNG for it so that it can appear in
  high-visibility spots like the hero treatments on the App Store and Games tabs.
- The search results safe area values are for the largest canvas (3840×2560). On a smaller canvas, scale them by the
  same factor.

## Video specs

| Placement | Ratio | Size (px) | Frame rate | Length | Format |
|---|---|---|---|---|---|
| Product page header | 21:9 | 3840×1646 | 30 or 60 fps | 5–30 s | `.mov`, `.m4v`, `.mp4` |
| Search results | 3:2 | 1920×1280 – 3840×2560 | 30 or 60 fps | 5–30 s | `.mov`, `.m4v`, `.mp4` |

Videos are muted in search and can't be unmuted there. On the product page they start muted but people can unmute
them. They loop in both places. Make the motion slow and seamless, and keep it inside the safe area.

## Templates

Apple's templates contain the safe areas as layers:

| Tool | Header | Search results | Universal |
|---|---|---|---|
| Figma | — | — | [templates](https://developer.apple.com/go/?id=figma-creative-assets-templates) |
| Photoshop | [header](https://developer.apple.com/go/?id=photoshop-product-page-header-template) | [search](https://developer.apple.com/go/?id=photoshop-search-results-template) | [universal](https://developer.apple.com/go/?id=photoshop-universal-asset-template) |
| Pixelmator | [header](https://developer.apple.com/go/?id=pixelmator-product-page-header-template) | [search](https://developer.apple.com/go/?id=pixelmator-search-results-template) | [universal](https://developer.apple.com/go/?id=pixelmator-universal-asset-template) |
| Sketch | — | — | [templates](https://developer.apple.com/go/?id=sketch-creative-assets-templates) |

## In-App Events

Timely, limited moments in the app: a competition, a premiere, a live experience, a season or a major update. They show
up in search, on the product page and in editorial. Every event needs media in two shapes.

- **Badge:** Challenge, Competition, Live Event, Major Update, New Season, Premiere or Special Event. The media should
  add to the badge, not repeat it.
- **Two shapes, one look:** The landscape card and the portrait details page use the same colors and style.
- Metadata must describe the event, not the app in general. The event has to happen at the dates set, and the deep
  link must open the right place in the app (Guideline 2.3.13).

| Media | Ratio | Size (px) | Video | Max size | Format |
|---|---|---|---|---|---|
| Event card | 16:9 landscape | 1920×1080 – 3840×2160 | 30 or 60 fps, 5–30 s | 500 MB | image `.jpg`/`.jpeg`/`.png`, video `.mov`/`.m4v`/`.mp4` |
| Event details page | 9:16 portrait | 1080×1920 – 2160×3840 | 30 or 60 fps, 5–30 s | 500 MB | same |

Audio is optional ("tracks without audio are supported"). If you add it, use stereo AAC at 256 kbps, 44.1 or 48 kHz.
The details page video also takes 16, 24 or 32-bit PCM.

More: [In-App Events](https://developer.apple.com/app-store/in-app-events/).
