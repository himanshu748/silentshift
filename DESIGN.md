# Signal / Substance

## Product direction

SilentShift is an evidence workbench for integration engineers. The main view prioritizes the contradiction and the records that prove it. Calm typography, aligned data and visible provenance do the work; decorative charts and invented activity do not.

## Foundations

- Canvas `#0B1116`, surface `#121C23`, elevated `#19262F`, border `#2B3D47`.
- Text `#EBF3F5`, secondary `#A2B4BC`. Use `#97ABB5` for small metadata rather than the brief's lower-contrast muted token.
- Semantic mint `#44D6B4` allow, amber `#FFC27B` review, coral `#FF7C78` quarantine, lavender `#BCA9FF` investigation, blue `#7DBEFF` information. Always pair color with text/icon.
- Manrope variable for interface; IBM Plex Mono for identifiers, values and code. Self-host installed font packages with license notices; no remote font dependency.
- Display 40/48, H1 30/38, H2 24/32, H3 18/26, body 14/22, data 13/20, metadata 12/18. Tabular numeric values.
- Four-pixel rhythm, 24px desktop gutters, 16px compact gutters. Radii 6/10/14/18px. Thin borders and restrained elevation.

## Composition

Desktop uses a 220px navigation rail and a full-height work area. Header communicates selected environment and the actual connection state. Investigations use queue → evidence → provenance. Evidence comparison is a ruled table with partner value, reference value and source; the decision appears beside its concrete consequence. At 1100px provenance moves below the evidence; at 760px navigation becomes a horizontal scrollable rail and the queue becomes a full-width list preceding detail. No fixed element may obscure content or keyboard focus.

Overview shows backend-derived counts and recent cases. When there are no records, show zero only after a successful API response. While disconnected, counts are unavailable. Scenario Lab presents five numbered experiments, the exact injected payload, independent reference context and expected ground truth separately from the observed result. The run button triggers the native API and shows pending, timeout/failure or returned case. Never play a staged progress animation as if it were a native trace.

Messages expose copyable raw JSON and a semantic comparison. Evaluations display measured run denominators, version and missing metrics explicitly. Policies show actual versioned checks. Health distinguishes configured credentials from a provider invocation that actually succeeded.

## Interaction and accessibility

Use semantic buttons, links, headings, tables and labeled inputs. Visible mint focus ring; skip-to-content; native selects and disclosure controls. Search and decision filters operate on returned records with a clearly labeled server limit. Errors contain a recovery action. Reviewer dialogs explain effect, require a reason, trap/restore focus and support Escape. Server permissions remain authoritative.

Motion personality is Corporate: 100ms hover, 160ms feedback and 220ms panel entrance using `cubic-bezier(.2,0,0,1)`. Use only small transform/opacity transitions that explain selection or a returned state. No continuous ambient motion. Reduced motion disables spatial transitions and spinner loops; text still conveys pending work. Accessibility and repeated-task speed take precedence over motion recipes.

## Verification

Check desktop 1440×960 and mobile 390×844, keyboard tab/focus, modal Escape, reduced motion, semantic names, overflow and contrast. Verify connected states against actual native records when runtime is available. Disconnected and empty-state browser tests are useful but do not prove the native journey.
