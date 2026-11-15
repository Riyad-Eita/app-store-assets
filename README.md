# App Store Assets

An agent skill for App Store images and videos. It covers the app icon, screenshots, app previews, product page
header and search results art, and In-App Event media. Apple's asset guidance is condensed into one checklist with
every spec in one place, plus a validator that finds wrong sizes, alpha channels, bad video lengths, frame rates and
audio before App Store Connect does.

- **Rules that get assets rejected:** App Review Guideline 2.3 and Apple's asset best practices, written as a checklist.
- **Exact specs:** every screenshot size, app preview resolution, safe area and length, with the matching App Store
  Connect API display types.
- **The iOS 27 additions:** product page header, search results art and the universal creative asset, plus the iPhone
  Duo screenshots that become mandatory in April 2027.
- **`check_assets.py`:** a validator that uses only the Python standard library (plus `ffprobe` for videos).
- **Sources:** every statement links to Apple's page. Last checked 2026-11-15.

## Install

As a [Claude Code](https://code.claude.com/docs/en/skills) skill, for every project:

```sh
git clone https://github.com/Riyad-Eita/app-store-assets ~/.claude/skills/app-store-assets
```

For a single project, clone it into `.claude/skills/app-store-assets` inside that project instead. Any other agent
that reads `SKILL.md` skills can use the folder as is.

Then just ask, for example:

> Plan the screenshots for our App Store listing.
> Check everything in `./store` before I upload it.
> Turn this screen recording into an iPhone app preview.

The skill also loads on its own whenever a task involves App Store images or videos.

## Validator

The validator also works without any agent:

```sh
python3 scripts/check_assets.py store/                 # every image and video under the folder
python3 scripts/check_assets.py hero.png --json        # machine-readable
python3 scripts/check_assets.py store/ --strict        # warnings fail too (for CI)
```

```text
FAIL  store/header.jpg  5244×2950  [Universal creative asset 16:9]
        x the universal creative asset must be PNG
ok    store/en/01-agent.png  1320×2868  [iPhone Dynamic Island, large (APP_IPHONE_67)]
FAIL  store/en/02-terminal.png  1320×2868  [iPhone Dynamic Island, large (APP_IPHONE_67)]
        x has an alpha channel (App Store images can't have transparency; flatten to RGB)
ok    store/en/preview.mp4  886×1920, 20.0 s, 30 fps  [iPhone app preview (Face ID, Dynamic Island, Duo)]

4 file(s), 2 failed
```

What it checks:

| | Checks |
|---|---|
| Images | Size matches a real App Store slot · PNG/JPEG only · no alpha channel or `tRNS` transparency · no CMYK · universal asset is PNG · extension matches the content |
| App previews | Accepted resolution · 15–30 s · ≤ 30 fps · H.264 up to High Profile Level 4.0 or ProRes 422 HQ · progressive · ≤ 500 MB · stereo AAC/PCM at 44.1 or 48 kHz |
| Creative and event videos | Size or aspect ratio range · 5–30 s · 30 or 60 fps · ≤ 500 MB (events) · stereo audio if present |
| Folders | No more than 10 screenshots or 3 previews for one slot |

A file can fit more than one slot. For example, 1920×1080 fits a Mac preview, an Apple TV screenshot and an In-App
Event card. The validator checks it against each of them and passes the file if it meets the rules of at least one.
Content (prices, URLs, other platforms' logos, readability) still needs a person, and the checklist in
[`SKILL.md`](SKILL.md#what-gets-assets-rejected) covers it.

Videos need FFmpeg (`brew install ffmpeg`, `apt install ffmpeg`).

## Contents

```text
SKILL.md                         workflow, rejection rules, craft, asset map, app icon
reference/screenshots.md         every size, required sets, fallbacks, API display types
reference/app-previews.md        encoding, resolutions, story, a working ffmpeg recipe
reference/creative-assets.md     header, search results, universal asset, In-App Events, templates
scripts/check_assets.py          the validator
tests/                           python3 -m unittest discover -s tests
```

## Keeping it current

Apple changes these specs whenever new devices ship. Every reference file names its source page. If a spec here
disagrees with Apple's page, Apple's page is right, so please open an issue or a pull request with the link.

## License

[MIT](LICENSE). This project isn't affiliated with or endorsed by Apple. App Store, iPhone, iPad, Mac, Apple Watch,
Apple Vision Pro and Liquid Glass are trademarks of Apple Inc.
