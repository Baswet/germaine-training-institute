# Germaine Training Institute — Safe Performance Optimization Report

Date: 2026-08-12
Scope: image/asset weight only. No structural changes, no ZIP, no reorganization, no backend/database/EarnFastCash logic touched.

---

## BEFORE

- Total site images (`assets/images/`): **278 MB** across 282 files
- Largest single file: `slide/pexels-mikitayo-16566216.jpg` — **7.4 MB** (5304×6630 px — far beyond any on-screen display size)
- 91 of 282 images were over 500 KB; several school/hero photos were 4–7 MB each
- JS/CSS: already using `defer` on all scripts, no duplicate includes, all 357 `<img>` tags already had explicit `loading="lazy"`/`loading="eager"`, Google Fonts already using `display=swap` with preconnect, critical CSS already preloaded (`<link rel="preload" as="style">`)

## AFTER

- Total site images: **176 MB** (down from 278 MB) — **37% reduction**, ~102 MB removed
- Worst individual offenders cut by 75–92%: e.g. 7.4 MB → 1.16 MB, 6.0 MB → 575 KB, 5.9 MB → 569 KB, 5.4 MB → 529 KB, 4.8 MB → 401 KB
- 261 JPEG/PNG files processed; 0 corrupted (verified with Pillow's image-integrity check after every batch); 0 left larger than their original
- JS/CSS/fonts: audited, found already optimized — no changes needed (details below)

## OPTIMIZATIONS PERFORMED

**Images (the only real bottleneck found):**
Every JPEG/PNG in `assets/images/` was inspected. Two safe, additive operations were applied, both fully reversible:
1. **Downscale oversized originals.** Many images were raw stock-photo/camera resolutions (up to 6720×4480 px) despite never being displayed anywhere near that size — even a full-bleed hero on a large retina monitor doesn't need more than ~2400px on the longest edge. Anything larger was resized down to a 2400px cap, preserving aspect ratio.
2. **Re-compress JPEGs at quality 85, progressive, optimized.** This is a visually-transparent setting (not a "low quality" export) that still cuts file size substantially versus an unoptimized camera/stock-photo export.

Same filenames, same paths, same formats — **zero HTML, CSS, or JS changes were needed**, so there is no risk of a broken reference anywhere on the site.

Every original file was backed up before being touched (kept outside the live project folder, not shipped anywhere). A small number of files were skipped or reverted automatically by a safety check I built into the process: if re-compressing a file would have made it larger or produced no meaningful saving, the original was restored instead — this affected a handful of already-well-compressed images (e.g. one campus photo actually grew by a few KB on re-encode, so it was reverted to its original).

**JS/CSS/fonts — audited, no changes made:**
- All 59 HTML pages already load scripts with `defer`; grepped for duplicate `<script src>`/`<link rel="stylesheet">` includes site-wide — found zero real duplicates (an initial regex hit on `style.css` appearing "twice" per page turned out to be the correct `<link rel="preload">` + `<link rel="stylesheet">` pairing, which is the *recommended* pattern, not a bug).
- All 357 `<img>` tags already have an explicit `loading` attribute (295 lazy, 62 eager) — full lazy-loading coverage already in place from earlier work on this project.
- Google Fonts already loaded with `display=swap` and `preconnect`; the font-weight sets requested match what's actually used in the CSS (`font-weight: 400/500/600/700/800`), so no unused weight was being downloaded.
- EarnCash's third-party scripts (Lucide icons, Chart.js) are already placed at the end of `<body>`, so they don't block initial rendering.

## SKIPPED — RISKY OPTIMIZATION (per your explicit rule)

- **Adding explicit `width`/`height` to the 350 `<img>` tags that lack them.** In principle this helps prevent layout shift (CLS). But spot-checking several of these (nav logo, school-card icons, etc.) showed their containers already have fixed dimensions in CSS (e.g. `.brand-logo-img { height:40px }`, `.school-top-img { width:64px; height:64px }`), so space is already reserved and no shift actually occurs. Retro-fitting correct width/height onto 350 tags across 59 pages — each needing the right true aspect ratio — is a large, error-prone edit for a problem that doesn't appear to exist in practice here. Skipped.
- **Converting images to WebP/AVIF.** Would give a further ~25–35% size cut on top of what's already done, but doing it safely requires either renaming files (breaks every existing reference across 59+ HTML/CSS/JS files) or adding `<picture>`/`srcset` markup around every image (a large, page-by-page edit). Given the "stability > performance" priority, this is left as a follow-up you can request separately if wanted — it's a bigger, more invasive change than the rest of this pass.
- **Pinning the EarnCash `unpkg.com/lucide@latest` script to a fixed version.** Would improve browser caching, but changing "@latest" to a pinned version could theoretically change which icon set renders if the library has moved on since this was wired up — a rendering-behavior risk, not just a performance tweak. Skipped; flagging it for you to decide on deliberately rather than changing it as a side effect of a performance pass.

## VERIFICATION

- **Backend regression:** full `pytest` suite re-run after all image changes (images live entirely in `build10/`, backend code was never touched) — **190 passed, 0 failed, 0 skipped**, same as before.
- **Live browser check:** loaded the homepage, About, and Student Life (`campus.html`) pages in the real browser after optimization, scrolled to trigger all lazy-loaded images, and verified via `fetch(..., {method:'HEAD'})` against every `<img>` on each page — **0 broken images, 0 HTTP failures, 0 console errors** on any of them.
- **Integrity check:** every optimized JPEG/PNG was re-opened and verified with Pillow's image-integrity check after processing — 0 corrupted files.
- Image quality was kept at a visually-transparent setting (quality 85, 2400px cap) — nothing was "compressed to look bad."

## REMAINING WARNINGS

- Backups of every original (unmodified) image are kept at `image_backup_original` in my working sandbox for this session only — they are **not** part of your project folder and won't persist after this session unless you ask me to copy them somewhere permanent. If you want a permanent local backup of the pre-optimization images, let me know and I'll copy it into your project folder (outside `assets/`, so it's never served to visitors).
- The remaining ~176 MB of images is still image-heavy for a website (a handful of hero/slideshow photos are still 1–3.6 MB each, by design, to stay sharp at full-bleed hero size) — WebP conversion (skipped above) is the next lever if you want to go further, but it's a separate, bigger task.
