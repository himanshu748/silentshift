# SilentShift logo assets

Created locally on November 10, 2026 with the built-in image generation tool. These are transparent PNG assets, not SVG/vector masters. The two offset forms create an S with a channel between them, echoing the comparison between a message and its governing record.

| File | Use | Dimensions | Alpha |
| --- | --- | --- | --- |
| [silentshift-logo-v1.png](silentshift-logo-v1.png) | Horizontal mark and wordmark, best on light surfaces | 2172 × 724 | Yes |
| [silentshift-icon-v1.png](silentshift-icon-v1.png) | Square standalone mark for an avatar or app icon | 1254 × 1254 | Yes |

The colors follow the current `web/src/tokens.css` ink/accent values. Existing application assets and the Open Exchange listing have not been changed. Publishing or uploading remains a separate gated action. Original generated files were preserved; selected copies live here. File sizes and SHA-256 hashes are in [the receipt](logo-v1-receipt.json). The metadata check used `sips -g pixelWidth -g pixelHeight -g hasAlpha` on each file. Both are under the repository's 50 MiB limit. Generation does not establish trademark clearance.

## Primary logo prompt

```text
Use case: logo-brand.
Create a finished, distinctive logo for SilentShift, a B2B order-validation workbench. It catches technically successful messages whose business meaning disagrees with approved contracts, and gives operators evidence before delivery.
Design one elegant horizontal brand lockup: a compact original geometric symbol on the left and the exact word "SilentShift" on the right. The symbol should suggest two offset ledger records being brought into alignment, with a deliberate negative-space pause between them; subtly read as an S. Make it simple enough to recognise at favicon size, with confident consistent geometry and a memorable silhouette.
Typography: meticulously spaced, medium-weight contemporary humanist sans serif, precise and calm, compatible with Manrope; exact capitalization SilentShift.
Follow the existing product's restrained paper-and-ink identity: dark graphite #17191c wordmark and a deep blue #1f3fbf symbol. Flat two-color design, crisp vector-like contours, generous balanced clear space, large artwork occupying most of the canvas.
Background: genuinely transparent alpha. This is the actual logo asset, not a presentation board or mockup. No additional words, tagline, subtitles, specimen labels, diagrams, shadows, gradients, 3D effects, glossy effects, sparkle/AI stars, robot heads, shields, ticks, stock arrows, badges, or watermarks. Create an original mark, not a recreation of another company's branding.
```

## Standalone icon prompt

The horizontal logo was supplied as the edit target; transparent background remained enabled.

```text
Use case: logo-brand. Create a square standalone app-icon companion from the supplied SilentShift logo. Edit target: the attached logo. Preserve the exact blue two-part S symbol's silhouette, diagonal angle, rounded corners, negative-space channel, proportions and deep blue color. Remove the entire SilentShift wordmark. Put only that existing symbol, large and optically centered, on a genuinely transparent square canvas with balanced clear space on all sides. Flat crisp vector-like edges; no extra enclosing rounded-square tile, no text, shadow, gradient, added outline, or new graphic. This is an extraction/reframing of the same identity, not a redesign.
```
