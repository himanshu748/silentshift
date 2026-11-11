import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {verifyReceipt} from '../docs/site/receipt-verifier.mjs';
const root=new URL('../',import.meta.url);
const read=p=>readFile(new URL(p,root),'utf8');
const selection=JSON.parse(await read('docs/site/assets/recorded-cases.json'));
const sourceText=await read(selection.source),source=JSON.parse(sourceText);
const receiptsText=await read(selection.receipts_source),receipts=JSON.parse(receiptsText);
test('selection pins real public source bytes and contains only the two intended synthetic cases',()=>{
 assert.equal(selection.source_sha256,createHash('sha256').update(sourceText).digest('hex'));
 assert.equal(selection.receipts_source_sha256,createHash('sha256').update(receiptsText).digest('hex'));
 assert.deepEqual(selection.cases.map(c=>c.scenario_id),['quantity-mismatch','approved-amendment']);
 for(const c of selection.cases){const original=source.records.find(r=>r.id===c.id);assert.ok(original);assert.equal(c.synthetic,true);
  for(const field of ['message','references','recommendation','policy','assessment','routing','delivery_count','trace_id'])assert.deepEqual(c[field],original[field]);
  for (const [key,value] of Object.entries(c.agent)) assert.deepEqual(value,original.agent[key]);
  assert.deepEqual(c.receipt,receipts.cases.find(r=>r.case_id===c.id).receipt);
 }
});
test('both native exports verify and bind to the displayed case and recorded route',async()=>{
 for(const c of selection.cases){const r=await verifyReceipt(JSON.stringify(c.receipt));assert.equal(r.integrityValid,true);assert.equal(r.keyMatches,null);assert.equal(r.payload.case_id,c.id);assert.equal(r.payload.decision,c.routing);}
});
test('the model error and the legitimate amendment are retained rather than rewritten',()=>{
 const [held,approved]=selection.cases;
 assert.equal(held.recommendation.decision,'ALLOW');assert.equal(held.policy.downstream_permitted,false);assert.equal(held.routing,'QUARANTINED');assert.equal(held.delivery_count,0);
 assert.ok(held.policy.checks.some(c=>c.code==='NO_CRITICAL_CONTRADICTION'&&!c.passed));
 assert.equal(approved.routing,'DELIVERED');assert.equal(approved.delivery_count,1);
 assert.ok(approved.assessment.active_reference_ids.includes('contract:PO-2048:v2'));
});
