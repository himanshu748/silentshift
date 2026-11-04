# Interactive interface review

SilentShift serves an integration operator investigating a technically successful order or payment whose meaning may be wrong. The interface needs to explain authority, then let the operator inspect the actual message, evidence and policy. The visual language remains Signal / Substance: dark surfaces, Manrope, IBM Plex Mono and mint/coral/amber decision colors.

## Product references studied

| Primary reference | Useful pattern | SilentShift application |
| --- | --- | --- |
| [Hookdeck Inspect](https://hookdeck.com/docs/inspect) and [event gateway basics](https://hookdeck.com/docs/hookdeck-basics) | Inspect an event and its delivery context together | Preserve the case queue beside actual evidence and make navigation quick; do not invent delivery status |
| [n8n execution workflow](https://docs.n8n.io/workflows/executions/all-executions/) | A run is understandable as stages with inspectable context | Click Receive, Read evidence, Policy gate or Route in the illustrated landing walkthrough |
| [Langfuse trace walkthrough](https://langfuse.com/docs/observability/overview) | Separate trace context, observations and detailed data | Keep Evidence / Timeline / Payload / Agent tabs; make detail changes legible with short transitions |

These public product pages and documentation informed the interaction patterns. No claim is made to have used a private competitor account; branding, screenshots, customer claims and operational metrics were not copied.

## Delivered interaction

The root URL opens a real landing page with an interactive order/contract comparison. Unsupported change and Approved amendment change the evidence and explain the corresponding decision. Stage selection and the bounded Play walkthrough show how that reasoning proceeds. This is explicitly **Illustrated / synthetic**, performs no API/model call and never claims a delivery. The adjacent workbench and Scenario Lab links lead to the real application.

The workbench adds ⌘K / Ctrl+K navigation, filtered view links and exact case-ID entry. Escape restores focus; Enter opens the first matching view. Existing authenticated case tabs, review permissions and API errors remain functional. No business policy or native runtime classes changed.

Motion follows the preferred motion-design guidance: corporate timing, short entrances and clear press/state feedback. The walkthrough is user-initiated, completes in under three seconds and has Reset. Reduced motion removes spatial animation and makes Play select the final stage immediately. No continuous ambient loop, parallax or fake live data is used.

## Verification

- TypeScript passed during implementation.
- Full landing/disconnected browser suite: **38 passed** at desktop 1440×960 and mobile 390×844, including 320px overflow, keyboard, API isolation, walkthrough and reduced motion.
- Connected native browser suite: **16 passed**, including a final repeat in **1.7 minutes**, against the real API. It covers case evidence, review permissions, keyboard and reduced motion. Two further desktop/mobile review-dialog checks passed in **16.4s**, including that ⌘K / Ctrl+K cannot stack navigation over an active review dialog.
- Final layout subset: **6 passed in 17.7s**. TypeScript and production build passed again; Vite completed in **1.69s** with the existing Lucide directive warnings.

[Desktop landing](assets/ui-final-landing-desktop.jpg) · [Mobile landing](assets/ui-final-landing-mobile.png) · [Real desktop investigation](assets/ui-final-workbench-desktop.png). Additional automated viewport captures are retained privately under evidence/browser. No screenshots or illustration are counted as native execution or a hosted online demo.
