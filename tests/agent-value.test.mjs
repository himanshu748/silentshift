import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {spawnSync} from 'node:child_process';
const root = new URL('../', import.meta.url);
const read = p => readFile(new URL(p,root),'utf8');
const data = JSON.parse(await read('docs/site/assets/agent-value.json'));
const summary = JSON.parse(await read('evidence/heldout/summary.json'));

test('presentation metrics are unchanged copies of the historical summary, including the worse third trial',()=>{
  for(const key of ['totals','trials','categories']) assert.deepEqual(data[key],summary[key]);
  assert.deepEqual(Object.values(data.trials['agent+policy']).map(x=>x.correct),[33,33,30]);
  assert.deepEqual(Object.values(data.trials['agent+policy']).map(x=>x.wrong_deliveries),[2,3,3]);
  assert.equal(data.totals['rules-only'].reviews,6);
  assert.equal(data.totals['agent+policy'].reviews,31);
});
test('every selected source byte is pinned; case values are copied from actual records',async()=>{
  const sources=[...data.sources,...data.cases.flatMap(c=>c.trials.map(t=>t.source))];
  for(const s of sources) assert.equal(s.sha256,createHash('sha256').update(await read(s.path)).digest('hex'));
  const rules=JSON.parse(await read('evidence/heldout/rules-only.json'));
  const fixtures=JSON.parse(await read('fixtures/v2-heldout/scenarios.json'));
  for(const c of data.cases){
    assert.deepEqual(c.baseline,rules.cases.find(x=>x.scenario_id===c.id));
    assert.deepEqual(c.truth,fixtures.scenarios.find(x=>x.id===c.id).ground_truth);
    for(const t of c.trials){
      const raw=JSON.parse(await read(t.source.path));
      for(const field of ['message','references','recommendation','policy','workflow','delivery_count','review']) assert.deepEqual(t[field],raw.record[field]);
      assert.equal(t.case_id,raw.case_id);assert.equal(t.session_id,raw.trace_id);
    }
  }
});
test('selected agent-only successes retain the shipped exact-routing failure and pending human step',()=>{
  assert.deepEqual(data.cases.map(c=>c.id),['HO-045','HO-030','HO-017']);
  for(const c of data.cases){assert.equal(c.category,'unstructured');assert.equal(c.baseline.decision,'ALLOW');
    for(const t of c.trials){assert.equal(t.recommendation.decision,c.truth.decision);assert.notEqual(t.policy.decision,c.truth.decision);assert.equal(t.policy.decision,'REQUEST_REVIEW');assert.equal(t.delivery_count,0);assert.equal(t.review,null);assert.equal(t.workflow.status,'pending');}
  }
});
test('each front door keeps denominators, review cost and correct-route limits beside the result',async()=>{
  for(const path of ['README.md','docs/site/index.html','docs/site/evidence-tour.html','docs/site/agent-value.html','docs/OPEN_EXCHANGE_COPY.md']){
    const text=await read(path);
    for(const required of ['6/23','2–3/23','12.5%','21.5%','33/48','30/48','counterfactual']) assert.ok(text.includes(required),`${path}: ${required}`);
    assert.ok(!text.includes('Overall correct routes are unchanged'),path);
  }
});
test('static selection rebuilds deterministically without running the evaluation',()=>{
  const r=spawnSync('python3',['scripts/build_agent_value.py','--check'],{cwd:root,encoding:'utf8'});
  assert.equal(r.status,0,r.stdout+r.stderr);assert.match(r.stdout,/no evaluation executed/);
});
