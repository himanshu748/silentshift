import { strictJSON, verifyReceipt, MAX_RECEIPT_BYTES } from './receipt-verifier.mjs';
const element = id => document.getElementById(id);
const editor = element('receipt-text'), expected = element('expected-key'), verdict = element('verification');
// Independently retained from the committed, real demo export's SPKI bytes.
const DEMO_KEY_SHA256 = '60efeb41e1d261192159cf510a7e2a57bbdf6ca231670d3b739c7182e76230a8';
let epoch = 0;
function invalidate() {
  epoch++; verdict.dataset.state = 'unchecked'; verdict.textContent = 'Edited or newly loaded. Verify these bytes to see the result.';
  for (const id of ['hash-check', 'signature-check', 'identity-check']) element(id).textContent = 'Not checked';
  element('receipt-details').hidden = true;
}
function showError(error) {
  verdict.dataset.state = 'invalid'; verdict.textContent = error instanceof Error ? error.message : 'Verification could not finish.';
  for (const id of ['hash-check', 'signature-check', 'identity-check']) element(id).textContent = 'Not verified';
  element('receipt-details').hidden = true;
}
async function verify(showResult = false) {
  const ticket = ++epoch; verdict.dataset.state = 'unchecked'; verdict.textContent = 'Checking the payload and signature locally…';
  try {
    const result = await verifyReceipt(editor.value, expected.value);
    if (ticket !== epoch) return;
    element('hash-check').textContent = result.hashValid ? 'Matches' : 'Does not match';
    element('signature-check').textContent = result.signatureValid ? 'Valid' : 'Invalid';
    element('identity-check').textContent = result.keyMatches === null ? 'No pin supplied' : result.keyMatches ? 'Matches pin' : 'Different key';
    const valid = result.verifiedWithPinnedKey;
    verdict.dataset.state = valid ? 'valid' : result.integrityValid && result.keyMatches === null ? 'untrusted' : 'invalid';
    verdict.textContent = valid
      ? 'Payload and signature verified against the supplied key fingerprint. This does not certify business correctness.'
      : !result.integrityValid ? 'Integrity check failed. These bytes do not match the signed export.'
      : result.keyMatches === false ? 'Signature is valid, but the signing key differs from the expected fingerprint.'
      : 'Signature and payload match the embedded key. Signing identity is unverified without an independent fingerprint.';
    element('case-id').textContent = result.payload.case_id;
    element('case-decision').textContent = result.payload.decision;
    element('case-mode').textContent = result.payload.execution_mode + (result.payload.synthetic ? ' · synthetic' : ' · not marked synthetic');
    element('key-fingerprint').textContent = result.fingerprint;
    element('receipt-details').hidden = false;
    if (showResult) verdict.focus();
  } catch (error) { if (ticket === epoch) { showError(error); if (showResult) verdict.focus(); } }
}
async function loadSample() {
  invalidate(); const ticket = epoch;
  try {
    const requested = new URL(location.href).searchParams.get('case');
    const selectedCase = ['quantity-mismatch','approved-amendment'].includes(requested) ? requested : null;
    const response = await fetch(selectedCase ? 'assets/recorded-cases.json' : 'assets/pex-sample.json');
    if (!response.ok) throw new Error('Recorded sample is unavailable. Open a local synthetic export instead.');
    let text = await response.text();
    if (ticket !== epoch) return;
    if (selectedCase) {
      const selection = JSON.parse(text).cases.find(row => row.scenario_id === selectedCase);
      if (!selection?.receipt) throw new Error('Selected recorded receipt is unavailable.');
      text = JSON.stringify(selection.receipt, null, 2);
      const sourceLink = document.createElement('a'); sourceLink.href = 'https://github.com/himanshu748/silentshift/blob/main/docs/evidence/bonus-claims-nov11/java-pex-frozen-cases.json'; sourceLink.textContent = 'the native receipt records';
      element('sample-source').replaceChildren('Selected historical synthetic export from ', sourceLink, '. Viewing it runs no investigation.');
    }
    if (ticket !== epoch) return;
    editor.value = text; expected.value = DEMO_KEY_SHA256; await verify();
  } catch (error) { if (ticket === epoch) showError(error); }
}
editor.addEventListener('input', invalidate); expected.addEventListener('input', invalidate);
element('verify').addEventListener('click', () => verify(true));
element('load-sample').addEventListener('click', loadSample);
element('tamper').addEventListener('click', async () => {
  invalidate();
  try {
    const copy = strictJSON(editor.value);
    if (!copy?.signed?.payload) throw new Error('Load a receipt before trying an edited copy.');
    copy.signed.payload.decision = copy.signed.payload.decision === 'DELIVERED' ? 'REVIEW' : 'DELIVERED';
    editor.value = JSON.stringify(copy, null, 2); await verify(true);
  } catch (error) { showError(error); }
});
element('receipt-file').addEventListener('change', async event => {
  invalidate(); const ticket = epoch; const file = event.target.files?.[0];
  if (!file) return;
  if (file.size > MAX_RECEIPT_BYTES) { showError(new Error('Use a receipt no larger than 64 KiB.')); return; }
  try {
    const text = await file.text(); if (ticket !== epoch) return;
    editor.value = text; expected.value = ''; await verify();
  } catch (error) { if (ticket === epoch) showError(error); }
});
loadSample();
