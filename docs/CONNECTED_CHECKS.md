# Prepare the native browser checks

The connected suite reads existing cases. It deliberately does not fabricate a
delivered case, a precedent match or a Workflow task to make a screen pass.
The keyless replay produces a critical hold only; it cannot supply every case
this suite needs.

Follow [INSTALL.md](../INSTALL.md) first. Use the verified build-154 ARM64 image,
the local Qwen alias and local `all-minilm:22m` embeddings. In the private `.env`,
select `SILENTSHIFT_PROVIDER=ollama`, `SILENTSHIFT_PROVIDER_MODE=live`, the documented
local Ollama URLs and the existing local account passwords. Keep external keys
empty. Start the native production and workbench as that guide describes.

## Create real synthetic operator cases

```sh
uv run --env-file .env python scripts/verify_native.py --allow-model-calls
```

This runs the same five Scenario Lab endpoints used by the workbench, through
authenticated REST, the Partner Service, native AI Hub and deterministic policy.
It performs fresh local inference. Expect `native_verified: true` and all five
scenario checks passing in the saved receipt.

The approved-amendment order must be `DELIVERED` with one simulator receipt.
Delivery queues source-bound indexing through the Precedents operation. Later
cases can retrieve that resolved case with local embeddings. The isolated
verification driver also documents its administrator indexing of the installed
synthetic approved-amendment catalog; it does not insert a fabricated case,
delivery, vector or recommendation. If the corpus is unavailable, inspect the
real retrieval failure rather than replacing it with a fixture.

## Read the resulting workbench

With the workbench running, use the npm entry point:

```sh
SILENTSHIFT_NATIVE_E2E=1 \
SILENTSHIFT_WEB_URL=http://127.0.0.1:5173 \
SILENTSHIFT_API_URL=http://127.0.0.1:52773/silentshift/api \
npm --prefix web run test:e2e:native
```

The suite also loads the repository `.env`. Adjust URLs for an isolated instance;
never place credentials in command arguments or evidence. It checks desktop and
mobile records, delivered amendments, real cosine matches and tool reads, native
review permissions, keyboard behavior and reduced motion. It never submits
investigations or review decisions.

The source prompt is `silentshift-investigator/1.4.2`. The test asserts that exact
version; it does not accept an arbitrary version to hide a mismatch with the
running native source. Public-package replay verification remains separately
pinned to its matching release tests.
