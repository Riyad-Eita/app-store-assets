---
name: app-store-assets
description: Plan, make, check and ship App Store assets the way Apple asks for them — app icon, screenshots, app previews, product page header and search results art (iOS 27 creative assets), In-App Event media, custom product pages and product page tests. Holds Apple's exact specs and rejection rules and a validator for sizes, alpha, video length, frame rate and audio. Use whenever creating, reviewing, exporting or uploading any App Store image or video, or planning store listing work.
---

# App Store assets

Apple's asset guidance, condensed into a checklist. The full specs are in `reference/` and the validator is in `scripts/`.
Last checked against Apple's pages on 2026-11-15. Sizes change when new devices ship, so re-read the source page
when something doesn't add up.

## Workflow

1. **Plan the story before making anything.** Start with one idea for someone who has never heard of the app, then the
   three features that matter most, then the rest. Screenshots, previews and the header tell this story in the same
   order, in one visual style (palette, type, iconography, tone).
2. **Capture real UI.** Use the current design and fictional demo data, never a real person's data (Guideline 2.3.9).
   Previews may contain only screen captures of the app itself (2.3.4).
3. **Compose one master per asset type, review it, then batch.** Render a single screenshot or frame, check it against
   the rules below, and only then produce every size and language.
4. **Validate:** `python3 scripts/check_assets.py <folder>` must report no failures.
5. **Review by eye** what a script can't see: the rules below, the safe area, the poster frame, the loop point, and the
   video watched muted.
6. **Upload** with a new version, in the Asset Library, or through the App Store Connect API. Then open App Store
   Connect's **product page preview** and check the header, the screenshots and the search result together.

## What gets assets rejected

Every image and video (screenshots, previews, header, search, event media) — Review Guidelines 2.3.3–2.3.14 and
[Focus on your core experience](https://developer.apple.com/app-store/asset-best-practices/#core-experience):

- [ ] No prices, discounts, "free", website URLs or © symbols.
- [ ] No claims that can't be verified: "#1", "best", awards or press the app didn't get.
- [ ] No Apple recognitions: Editor's Choice, App of the Day, Game of the Day, Apple Design Award.
- [ ] No names, icons or imagery of other mobile platforms or app marketplaces (2.3.10).
- [ ] Shows the app in use. A screenshot that is only title art, a login page or a splash screen gets rejected (2.3.3).
- [ ] Previews contain only screen captures of the app. Captions, narration and touch indicators are allowed (2.3.4).
- [ ] Suitable for 4+ even when the app is rated higher: no gore, weapons pointed at someone, profanity, drugs, sexual
      content, hate, self-harm or stereotypes (2.3.8).
- [ ] You hold the rights to everything shown, and every account, name and number is fictional (2.3.9).
- [ ] Paid content is marked as such where shown (2.3.2).
- [ ] Localized for every language the listing supports, images and videos included.

## What Apple rewards (and features)

Images ([#image](https://developer.apple.com/app-store/asset-best-practices/#image)):
- One clear focal point and strong composition, in the app's own aesthetic and the latest UI.
- Text is a short phrase that adds to the picture rather than describes it. Overlays can show input (a touch point,
  typing, Pencil).
- Key elements, text most of all, sit centered inside the safe area, because assets get cropped differently on each device.

Videos ([#videos](https://developer.apple.com/app-store/asset-best-practices/#videos)):
- **Poster frame**: the still people see first. It has to work on its own.
- **Start strong**: lead with the value or the best feature. Pace the cuts so people can follow, with no quick cuts and
  no fast motion.
- **Loop seamlessly**: videos autoplay and repeat, so the last frame must flow into the first.
- **Silent first**: audio is muted by default, so captions carry the message. Sound is brand texture, like a short
  music loop with no sudden loud parts, that loops cleanly.

## Asset map

| Asset | Where it shows | Count | Key size | Details |
|---|---|---|---|---|
| App icon | Everywhere | 1 | Icon Composer `.icon` | below |
| Screenshots | Product page; first 3 in search | 1–10 per device size and language | iPhone 1320×2868 · iPad 2064×2752 · Mac 2880×1800 | [reference/screenshots.md](reference/screenshots.md) |
| App previews | Before the screenshots; up to 3 in search | 0–3 per device size and language | iPhone 886×1920 · iPad 1200×1600 · Mac 1920×1080; 15–30 s | [reference/app-previews.md](reference/app-previews.md) |
| Product page header | Top of the product page (iOS 27+) | 1 | 3840×1646 (21:9) | [reference/creative-assets.md](reference/creative-assets.md) |
| Search results art | Search tab (iOS 27+) | 1 | 3:2, 1920×1280 – 3840×2560 | [reference/creative-assets.md](reference/creative-assets.md) |
| Universal creative asset | Header, search and hero spots | 1 | 5244×2950 PNG (16:9) | [reference/creative-assets.md](reference/creative-assets.md) |
| In-App Event media | Event card / details page | 1 each | 16:9 and 9:16 | [reference/creative-assets.md](reference/creative-assets.md#in-app-events) |

No image may have an alpha channel. Upload the largest size and App Store Connect scales it down for smaller devices.

## App icon

- Build a layered **Liquid Glass** icon in [Icon Composer](https://developer.apple.com/icon-composer/). One design covers
  iPhone, iPad, Mac and Apple Watch.
- Check the default, dark, clear and tinted appearances. It must stay recognizable at every size, from the App Store
  down to Spotlight.
- Keep the icon consistent with the alternate icons and the in-app purchase icons (2.3.8).
- Read the [HIG: App icons](https://developer.apple.com/design/human-interface-guidelines/app-icons) page and watch WWDC25
  [Say hello to the new look of app icons](https://developer.apple.com/videos/play/wwdc2025/220/).

## Validator

```sh
python3 scripts/check_assets.py path/to/assets            # every image and video under the folder
python3 scripts/check_assets.py shot.png preview.mp4 --json
python3 scripts/check_assets.py assets --strict           # warnings fail too
```

Standard library only. Videos need `ffprobe` (from FFmpeg). For each file it finds every App Store slot that size can
go into and checks the format, alpha channel, length, frame rate, codec, H.264 level, file size and audio. Per folder,
it flags more than 10 screenshots or more than 3 previews for one slot. Exit code 1 on any failure.

## Growing the listing

- **Custom product pages** — up to 70 extra versions of the product page, each with its own screenshots, previews,
  promotional text and URL, for one audience or campaign. ([guide](https://developer.apple.com/app-store/custom-product-pages/))
- **Product page optimization** — test up to three treatments (icon, screenshots, previews, header art) against the
  original for up to 90 days, one test at a time. Alternate icons have to ship in the binary.
  ([guide](https://developer.apple.com/app-store/product-page-optimization/))
- **In-App Events** — a timely moment (Major Update, Premiere, Live Event…) gets its own card in search, on the product
  page and in editorial.

## Sources

- [App Store asset best practices and resources](https://developer.apple.com/app-store/asset-best-practices/)
- [App Review Guidelines 2.3 — Accurate Metadata](https://developer.apple.com/app-store/review/guidelines/#metadata)
- [Screenshot specifications](https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications)
- [App preview specifications](https://developer.apple.com/help/app-store-connect/reference/app-information/app-preview-specifications)
- [Creative assets specifications](https://developer.apple.com/help/app-store-connect/reference/app-information/creative-assets-specifications)
- [In-App Event media and audio specifications](https://developer.apple.com/help/app-store-connect/reference/in-app-events/in-app-event-media-and-audio-specifications)
