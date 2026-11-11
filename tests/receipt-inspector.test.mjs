import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { canonical, strictJSON, verifyReceipt } from '../docs/site/receipt-verifier.mjs';
const original = await readFile(new URL('../docs/site/assets/pex-sample.json', import.meta.url), 'utf8');
const sample = JSON.parse(original);
const result = await verifyReceipt(original);

test('real Java-produced sample verifies; no pin implies no identity claim', async () => {
  assert.equal(original, await readFile(new URL('../docs/evidence/bonus-claims-nov11/java-pex-receipt.json', import.meta.url), 'utf8'));
  assert.equal(result.integrityValid, true);
  assert.equal(result.payloadHash, sample.signed.sha256);
  assert.equal(result.keyMatches, null);
  assert.equal(result.verifiedWithPinnedKey, false);
});
test('a separately retained expected key fingerprint is checked', async () => {
  assert.equal((await verifyReceipt(original, result.fingerprint)).verifiedWithPinnedKey, true);
  assert.equal((await verifyReceipt(original, '0'.repeat(64))).verifiedWithPinnedKey, false);
});
for (const field of ['decision', 'case_id', 'execution_mode', 'synthetic']) {
  test(`tampered ${field} fails hash and signature`, async () => {
    const changed = structuredClone(sample);
    changed.signed.payload[field] = {decision:'REVIEW', case_id:'another-case', execution_mode:'recorded-replay', synthetic:false}[field];
    const r = await verifyReceipt(JSON.stringify(changed));
    assert.equal(r.hashValid, false); assert.equal(r.signatureValid, false);
  });
}
test('changing timestamp breaks signature even with original valid payload hash', async () => {
  const changed = structuredClone(sample); changed.signed.created_at = '2026-01-01T00:00:00Z';
  const r = await verifyReceipt(JSON.stringify(changed));
  assert.equal(r.hashValid, true); assert.equal(r.signatureValid, false);
});
test('a new self-signed key cannot satisfy an independently pinned key', async () => {
  const key = await crypto.subtle.generateKey({name:'RSASSA-PKCS1-v1_5',modulusLength:2048,publicExponent:new Uint8Array([1,0,1]),hash:'SHA-256'},true,['sign','verify']);
  const changed = structuredClone(sample);
  changed.public_key_spki = Buffer.from(await crypto.subtle.exportKey('spki',key.publicKey)).toString('base64');
  changed.signature = Buffer.from(await crypto.subtle.sign('RSASSA-PKCS1-v1_5',key.privateKey,new TextEncoder().encode(canonical(changed.signed)))).toString('base64');
  const r=await verifyReceipt(JSON.stringify(changed),result.fingerprint);
  assert.equal(r.integrityValid,true); assert.equal(r.keyMatches,false); assert.equal(r.verifiedWithPinnedKey,false);
});
test('duplicate fields, escaped duplicate names, trailing data and oversized/deep input are rejected', () => {
  for (const input of ['{"a":1,"a":2}','{"a":1,"\\u0061":2}','{} {}','\u00a0{}',' '.repeat(65537), '['.repeat(12)+'0'+']'.repeat(12)])
    assert.throws(()=>strictJSON(input));
});
test('unsupported algorithms, bad metadata, malformed encodings and unsorted evidence fail closed', async () => {
  const variants=[s=>s.signature_algorithm='none',s=>s.signed.payload.synthetic='true',s=>s.signature='@!',s=>s.signed.payload.evidence_hashes.reverse(),s=>s.signed.payload.evidence_hashes.push(s.signed.payload.evidence_hashes[0]),s=>s.signed.extra='ignored'];
  for(const edit of variants){const s=structuredClone(sample);edit(s);await assert.rejects(verifyReceipt(JSON.stringify(s)));}
});
