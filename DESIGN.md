# Product and interaction design

SilentShift serves integration operations teams investigating B2B orders. The central task is to compare what arrived with the independently approved commitment, understand the resulting hold or delivery, and resolve only the actions permitted by the server.

The current interface was rebuilt with Snowflake CoCo from the product and integration brief. The owner asked CoCo to choose its visual direction without a prescribed palette or layout. The earlier Signal / Substance specification described the original interface; it is superseded by the implemented components and [tokens](web/src/tokens.css). Future changes should preserve the accepted interface and task contracts rather than restore that historical layout.

## Public site

The product site has separate HTML documents for Home, How it works, Workbench tour, Safeguards, Evidence record and Run locally. Vite builds each entry, so direct loads and refreshes do not depend on a single-page fallback. Each document has its own title, content and active navigation state. Public components do not mount authenticated API hooks.

The home comparison is interactive and explicitly synthetic. Switching its authority state or playing the walkthrough explains the policy; it does not invoke IRIS or a model. Recorded evidence pages identify historical captures. They do not imply a hosted app or fresh inference. Setup links to the single [installation guide](INSTALL.md), rather than introducing a competing recipe.

Old landing-section links redirect to the corresponding document. Existing workbench and case hashes remain compatible. Opening a separate document ends that tab's in-memory session; reconnecting is deliberate, with no browser credential persistence.

## Native workbench

The application uses a horizontal desktop shell with Workspace and Validation navigation, a connection indicator, quick navigation and session controls. Narrow layouts expose a menu and keep the connection state visible. The queue leads to evidence, provenance and the next permitted action. Values use responsive paired ledgers; they must remain readable without horizontal page overflow.

Case records, counts, workflow tasks, traces and precedent scores come from the actual native API. Empty records, a missing session, insufficient permission and an unavailable backend are distinct states. No connected data is invented to make a screen look populated.

CSV intake preserves the selected sources while navigating, previews without dispatch, requires explicit source consent and importer permission, and reports progress per resolved line. An uncertain result requires reconciliation or a new preview, not an automatic resubmission. Displayed quantities and units must match the native records.

Review controls reflect server permissions and the case's eligibility. A written reason and current version are required. Critical contradictions cannot be approved. A recorded review pending native task completion resumes the existing decision rather than inventing a new approval.

## Accessibility and motion

Manrope and IBM Plex Mono are installed and served locally. Data uses aligned numeric values. Meaning is conveyed by labels and icons as well as colour; contrast and visible focus must survive both OS appearance modes.

Use semantic links, buttons, headings, tables and disclosures. Every public page has a skip link and main landmark. Mobile navigation supports Escape and returns focus to its toggle. The workbench supports keyboard queue navigation and quick switching; dialogs trap focus, close on Escape and restore focus to the initiating control.

Motion explains a user action or returned state. The synthetic walkthrough is bounded and labelled; it must never masquerade as native progress. Reduced motion disables animations and transitions while retaining usable controls and textual status. Small screens must not hide an action, credential/session status or business value to obtain a clean screenshot.

## Verified scope

[The multi-page receipt](docs/evidence/top3-multipage.json) ties the implementation to its source hash and desktop/mobile captures. It records production-build static document checks, keyboard/reduced-motion/browser checks, actual native reads, CSV imports and fresh native scenarios. The [build status](docs/BUILD_STATUS.md) separates these results from clean-install, model-provider and public-package gates.

All supplied cases are synthetic and delivery is simulator-only. The [held-out comparison](docs/EVAL_HELDOUT.md) does not establish an overall AI accuracy advantage, and agent + policy did not improve unstructured routing over rules. These limitations are part of the interface's truth contract, not copy to remove during visual polish.
