## 1. Stylesheet — token block

- [x] 1.1 Add dark-mode `:root` token block to `styles.css`: `--bg`, `--bg-subtle`, `--text`, `--text-heading`, `--text-muted`, `--accent`, `--accent-display`, `--border`, `--font-title`, `--font-body`, `--body-size`, `--content-width`
- [x] 1.2 Add `@media (prefers-color-scheme: light) :root:not([data-theme="dark"])` light-mode override block with confirmed values (`--text: #2A1640`, `--text-heading: #2D1A4A`, `--text-muted: #7B54A0`, etc.)
- [x] 1.3 Add `:root[data-theme="light"]` explicit light override block (same values as 1.2)
- [x] 1.4 Add `:root[data-theme="dark"]` explicit dark override block (same values as 1.1)

## 2. Stylesheet — base styles

- [x] 2.1 Add CSS reset (`box-sizing: border-box`, margin/padding zero)
- [x] 2.2 Add `body` base rule: `background: var(--bg)`, `color: var(--text)`, `font-family: var(--font-body)`, `font-size: var(--body-size)`, `line-height: 1.75`
- [x] 2.3 Add global `a` styles using `var(--accent)`
- [x] 2.4 Add `.site-header` styles: sticky, border-bottom, background, padding
- [x] 2.5 Add `.header-inner` layout: max-width, centred, flex space-between
- [x] 2.6 Add `.site-name` styles: Fraunces, weight 400, `opsz` 14, `letter-spacing: 0.02em`
- [x] 2.7 Add `nav a` styles: uppercase, muted colour, hover uses `var(--accent)`

## 3. Stylesheet — heading conventions

- [x] 3.1 Add `h1` rule: Fraunces, weight 400, `opsz` 36, `letter-spacing: 0.005em`, `color: var(--text-heading)`
- [x] 3.2 Add `.article-title` rule: Fraunces, weight 500, `opsz` 72, `letter-spacing: -0.01em`, `color: var(--text-heading)`
- [x] 3.3 Add `.article-list h2` rule: Fraunces, weight 300, `opsz` 18, `letter-spacing: 0.01em`, `color: var(--text-heading)`

## 4. Stylesheet — layout

- [x] 4.1 Add `main` centred-column rule: `max-width: var(--content-width)`, `margin: 0 auto`, padding

## 5. Base template — fonts

- [x] 5.1 Add `<link rel="preconnect" href="https://fonts.googleapis.com">` to `base.html` `<head>`
- [x] 5.2 Add `<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>` to `base.html` `<head>`
- [x] 5.3 Add Google Fonts stylesheet `<link>` loading Fraunces (variable, opsz + wght axes, italic + upright) and IBM Plex Sans (300, 400, 500; upright and italic)
- [x] 5.4 Add `<link rel="stylesheet" href="/theme/css/styles.css">` to `base.html` `<head>` (if not already present)

## 7. Component styles — article list

- [x] 7.1 Style `main ul` as unstyled list and `main ul li` with padding and border separators
- [x] 7.2 Style `main ul li > a` as article list title (Fraunces, weight 300, text-heading colour, no underline)
- [x] 7.3 Style `main ul li time` as meta (muted, small) and `span.langs` as pill badge

## 8. Component styles — article page

- [x] 8.1 Override `article h1` with article-title sizing (larger, weight 500, opsz 72)
- [x] 8.2 Style `article > time` and `p.available-in` as article meta (muted, small, block)
- [x] 8.3 Style `article > div p` paragraphs (margin-bottom, max-width 65ch)
- [x] 8.4 Style `p.article-tags` section (border-top, muted) and its `a` links (accent colour)

## 6. Verification

- [x] 6.1 Run `pelican content -s pelicanconf.py` and confirm build completes without errors
- [x] 6.2 Open a rendered page in the browser and confirm dark-mode palette applies by default
- [x] 6.3 Add `data-theme="light"` to `<html>` in a built page temporarily and confirm light palette switches correctly, then revert
- [x] 6.4 Confirm headings use Fraunces and body text uses IBM Plex Sans (or readable fallbacks if offline)
- [x] 6.5 Confirm `--text-muted` is not used at font sizes below 14px in any existing template
