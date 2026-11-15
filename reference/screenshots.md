# Screenshots

Source: [Screenshot specifications](https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications)
and [asset best practices → Screenshots](https://developer.apple.com/app-store/asset-best-practices/#screenshots).

## Rules

- 1–10 screenshots per device size and language. Depending on orientation, up to **3** show in search results, so the
  first three have to work without the rest.
- `.png`, `.jpg` or `.jpeg`. **No alpha channel or transparency**, even if every pixel is opaque.
- Upload the highest required size. App Store Connect scales it down for the smaller devices. Upload a smaller size
  only when the UI really differs on that device.
- Show the app in use. A slide that is only an accolade or a call to action wastes a slot, and a screenshot that is
  only title art, a login page or a splash screen gets rejected (Guideline 2.3.3).
- Lead with the strongest feature and order the set as one story, the way someone would actually use the app.

## Required sets

| Platform | Required | In practice |
|---|---|---|
| iPhone | At least one screenshot for iPhone with Dynamic Island (medium display) | The medium set falls back to scaled Face ID (large), which falls back to Dynamic Island (large). So one 1320×2868 set covers every iPhone |
| iPhone Duo | From **April 2027** for apps built with the iOS 27.1 SDK or later | No fallback. Uploading them adds a "made for iPhone Duo" badge to the product page |
| iPad | At least one 13" screenshot if the app runs on iPad | 2064×2752 covers every iPad |
| Mac | Required for Mac apps | 16:10 only |
| Apple TV, Apple Vision Pro, Apple Watch | Required for that platform | — |

## Sizes

The sizes are in pixels and each one is also accepted rotated. `Display type` is the `screenshotDisplayType` value in the
App Store Connect API.

### iPhone

| Display | Devices (examples) | Sizes | Display type | Falls back to |
|---|---|---|---|---|
| Dynamic Island, large | iPhone 18/17/16 Pro Max, Air, 16/15 Plus | **1320×2868**, 1290×2796, 1260×2736 | `APP_IPHONE_67` | Face ID, large |
| Face ID, large | iPhone 14 Plus, 13/12/11 Pro Max, 11, XS Max, XR | 1284×2778, 1242×2688 | `APP_IPHONE_65` | Dynamic Island, large |
| Dynamic Island, medium | iPhone 18/17/16/15 Pro, 17, 16, 15, 14 Pro | 1206×2622, 1179×2556 | `APP_IPHONE_61` | Face ID, large |
| Face ID, medium | iPhone 17e, 16e, 14, 13, 12, 11 Pro, XS, X | 1170×2532, 1125×2436, 1080×2340 | `APP_IPHONE_58` | Dynamic Island, medium |
| Home Button, large | iPhone 8/7/6S/6 Plus | 1242×2208 | `APP_IPHONE_55` | Face ID, medium |
| Home Button, medium | iPhone SE (2nd, 3rd), 8, 7, 6S, 6 | 750×1334 | `APP_IPHONE_47` | Home Button, large |
| Home Button, 4" | iPhone SE (1st), 5S, 5C, 5 | 640×1136, 640×1096 | `APP_IPHONE_40` | Home Button, medium |
| Home Button, 3.5" | iPhone 4S, 4 | 640×960, 640×920 | `APP_IPHONE_35` | Home Button, 4" |
| iPhone Duo, outer | iPhone Duo | 1398×2034 | see App Store Connect | — |
| iPhone Duo, inner | iPhone Duo | 2007×2853 | see App Store Connect | — |

### iPad

| Display | Devices (examples) | Sizes | Display type | Falls back to |
|---|---|---|---|---|
| 13" | iPad Pro (M5, M4, 3rd–6th gen), iPad Air (M2–M4) | **2064×2752**, 2048×2732 | `APP_IPAD_PRO_3GEN_129` | — |
| 12.9" | iPad Pro (2nd gen) | 2048×2732 | `APP_IPAD_PRO_129` | 13" |
| 11" | iPad Pro 11", iPad Air, iPad (A16, 10th), iPad mini (A17 Pro, A20 Pro, 6th) | 1488×2266, 1512×2316, 1668×2420, 1668×2388, 1640×2360 | `APP_IPAD_PRO_3GEN_11` | 13" |
| 10.5" | iPad Pro 10.5", iPad Air (3rd), iPad (7th–9th) | 1668×2224 | `APP_IPAD_105` | 12.9" |
| 9.7" | older iPads, iPad mini 2–5 | 1536×2048, 1536×2008, 768×1024, 768×1004 | `APP_IPAD_97` | 10.5" |

### Other platforms

| Platform | Sizes | Display type |
|---|---|---|
| Mac | 16:10 — 1280×800, 1440×900, 2560×1600, **2880×1800** (landscape only) | `APP_DESKTOP` |
| Apple TV | 1920×1080, 3840×2160 | `APP_APPLE_TV` |
| Apple Vision Pro | 3840×2160 | `APP_APPLE_VISION_PRO` |
| Apple Watch | 422×514 (Ultra 3/4), 410×502 (Ultra/Ultra 2), 416×496 (Series 10–12), 396×484 (Series 7–9), 368×448 (Series 4–6, SE), 312×390 (Series 1–3). Use the same size in every language | `APP_WATCH_ULTRA`, `APP_WATCH_SERIES_10`, `APP_WATCH_SERIES_7`, `APP_WATCH_SERIES_4`, `APP_WATCH_SERIES_3` |

The display types for the iPhone Duo aren't in the published API reference yet. Look them up in App Store Connect or
in the API's current OpenAPI spec before you script an upload.

## Making them well

- **Frame:** A device frame isn't required. A full-bleed screenshot with a caption band works as well, as long as the UI
  stays large enough to read at the size it's shown in search.
- **Caption:** One short line, two at most, that tells a stranger why the screen matters. Use the same position and
  type size on every screenshot.
- **Scaled check:** Look at the 1320×2868 master at about 30 % size. If the caption or the key UI is hard to read
  there, it will be hard to read in search too.
- **Landscape apps:** Search shows up to three portrait screenshots side by side, but fewer landscape ones. Put the
  single strongest screen first.
