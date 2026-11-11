# Inspect a Java receipt locally

The public [receipt inspector](https://himanshu748.github.io/silentshift/receipts.html) checks the real synthetic export already retained in `docs/evidence/bonus-claims-nov11/java-pex-receipt.json`. It recomputes the payload SHA-256 and verifies the RSA-2048 signature using Web Crypto. It does not contact IRIS, call a model, authorize a route or modify a saved receipt.

```sh
python3 -m http.server 5198 --bind 127.0.0.1 --directory docs/site
```

Open `http://127.0.0.1:5198/receipts.html`. The recorded sample loads automatically. Choose **Test an edited copy** to change only the editor's outcome and see hash/signature verification fail; **Load recorded sample** restores the unchanged exported bytes. Files selected locally are never uploaded. Use synthetic exports only.

A receipt includes its own public key, so a matching signature alone does not prove signing identity. Supply an expected SPKI SHA-256 fingerprint obtained independently from the operator. Without a pin, the page explicitly reports identity as unverified; a different key fails the identity check even if its own signature is valid. The bundled sample pin identifies only the retained demo key, not an externally certified party. Signatures do not establish business correctness, authoritative evidence or a tamper-proof host.

The verifier rejects duplicate JSON fields (including escaped duplicate names), trailing data, oversized/deep input, unsupported schema/algorithm, invalid metadata and unsorted/duplicate evidence hashes. Its canonical representation matches the owned Java exporter for this restricted schema, not a general-purpose JSON-signature standard.

Checks:

```sh
node --test tests/receipt-inspector.test.mjs
npm --prefix web ci
npx --prefix web playwright install chromium
node scripts/check_receipt_inspector.cjs
```

For an already installed local Chrome, set `SILENTSHIFT_CHROME_CHANNEL=chrome` for the browser check. CI uses the runner’s installed Chrome through the same supported channel. The browser gate covers mobile/desktop, key trust, tampering, local-file bounds, keyboard/result focus, reduced-motion conditions, no-script content and absence of writes or third-party requests. [Browser receipt and captures](evidence/voting-nov11-receipts/browser.json) · [cryptographic regression output](evidence/voting-nov11-receipts/node-tests.txt). These are local static checks, not native or public-host execution.

The existing inspector was deployed from main 7ae03be on November 11. No inspector algorithm changed in this presentation branch. Any further Pages deployment remains separately gated. A static verification utility is not a hosted native app or an awarded online-demo bonus. The native package and routing semantics are unchanged.
