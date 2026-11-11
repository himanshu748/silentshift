import { verifyReceipt } from './receipt-verifier.mjs';
const $ = id => document.getElementById(id);
const tabs = [...document.querySelectorAll('[data-step]')];
let data, selected = 'quantity-mismatch', step = 0, epoch = 0;
const names = ['intake', 'authority', 'decision', 'receipt'];
const make = (tag, text, className = '') => { const node = document.createElement(tag); node.textContent = text; if (className) node.className = className; return node; };
const json = value => make('pre', JSON.stringify(value, null, 2), 'tour-json');
async function render({ focus = false } = {}) {
  if (!data) return;
  const ticket = ++epoch, record = data.cases.find(row => row.scenario_id === selected);
  $('recorded-route').textContent = record.routing;
  $('recorded-effect').textContent = 'Recorded simulator deliveries: ' + record.delivery_count;
  $('recorded-id').textContent = record.id; $('recorded-session').textContent = String(record.trace_id);
  $('case-held').setAttribute('aria-pressed',String(selected === 'quantity-mismatch'));
  $('case-amended').setAttribute('aria-pressed',String(selected === 'approved-amendment'));
  tabs.forEach((tab, i) => { tab.setAttribute('aria-selected', String(i === step)); tab.tabIndex = i === step ? 0 : -1; });
  $('step-panel').setAttribute('aria-labelledby', 'step-' + step);
  $('previous').disabled = step === 0; $('next').disabled = step === 3;
  $('next').textContent = step === 3 ? 'End of record' : 'Next: ' + names[step + 1] + ' →';
  $('step-progress').textContent = (step + 1) + ' of 4';
  const body = $('step-body'); body.replaceChildren();
  $('step-kicker').textContent = 'Recorded ' + names[step] + ' / ' + record.scenario_id;
  if (step === 0) {
    $('step-title').textContent = 'An accepted message still needs a meaning check.';
    $('step-explanation').textContent = 'The saved incoming order requests ' + record.message.quantity + ' ' + record.message.unit + '. Its business event clock is ' + record.clock + '; the native investigation was recorded on November 11. These dates serve different purposes.';
    body.append(json(record.message));
  } else if (step === 1) {
    $('step-title').textContent = selected === 'quantity-mismatch' ? 'No approved conversion closes this gap.' : 'The effective amendment changes the authority.';
    $('step-explanation').textContent = 'These are the independent reference snapshots saved with this case, not fields asserted by the sender. Active reference selection comes from the persisted deterministic assessment.';
    for (const reference of record.references) {
      const card = make('section', '', 'tour-reference');
      card.append(make('h3',reference.id));
      card.append(make('p',String(reference.quantity) + ' ' + reference.unit + ' · ' + reference.authority));
      card.append(make('p',record.assessment.active_reference_ids.includes(reference.id) ? 'Selected as active by assessment' : 'Not selected as active by assessment'));
      card.append(make('p','Effective from ' + reference.effective_from));
      const details = make('details','');details.append(make('summary','Read the complete saved reference'),json(reference));card.append(details);body.append(card);
    }
  } else if (step === 2) {
    $('step-title').textContent = record.recommendation.decision === 'ALLOW' && record.routing !== 'DELIVERED'
      ? 'The model said ALLOW. Policy refused.' : 'A proposal passes only with resolved evidence.';
    $('step-explanation').textContent = 'The proposal below is the actual saved model output. Its explanation is not an authoritative fact. The final route and passed/failed checks come from the recorded deterministic policy.';
    const proposal = make('section','','tour-proposal');proposal.append(make('strong','Actual agent proposal: ' + record.recommendation.decision));proposal.append(make('p',record.recommendation.explanation));proposal.append(make('p','Cited records: ' + record.recommendation.evidence_ids.join(', ')));body.append(proposal);
    const tools = make('details','');tools.append(make('summary','Inspect original model metadata and tool reads'),json(record.agent));body.append(tools);
    body.append(make('h3','Recorded policy: ' + record.policy.decision));
    for (const check of record.policy.checks) {
      const row = make('div','','tour-check');row.dataset.passed=String(check.passed);
      row.append(make('span',check.code),make('strong',check.passed ? 'Passed' : 'Failed'));body.append(row);
    }
  } else {
    $('step-title').textContent = 'The receipt preserves the committed outcome.';
    $('step-explanation').textContent = 'Java PEX exported this record in the same historical case. This browser now checks its payload hash and signature. That checks integrity under the embedded key, not business correctness or independent identity.';
    const status = make('p','Checking the recorded signature locally…','tour-signature');status.setAttribute('role','status');body.append(status);
    body.append(json(record.receipt.signed));
    const link = make('a','Try an edited copy in the receipt inspector ↗');link.href='receipts.html?case='+encodeURIComponent(selected);body.append(link);
    try {
      const verified = await verifyReceipt(JSON.stringify(record.receipt));
      if (ticket !== epoch) return;
      status.textContent = verified.integrityValid ? 'Payload hash matches. RSA signature is valid under the embedded key. Independent signing identity is not established here.' : 'Recorded receipt verification failed. Inspect the original source before relying on this selection.';
      if (!verified.integrityValid) status.style.background = '#f9e6df';
    } catch { if (ticket === epoch) status.textContent = 'Local verification is unavailable. Use HTTPS or localhost and inspect the source receipt.'; }
  }
  if (ticket !== epoch) return;
  const url = new URL(location.href);url.searchParams.set('case',selected);url.searchParams.set('step',String(step));history.replaceState(null,'',url);
  if (focus) $('step-panel').focus();
}
function chooseStep(index, focus = false) { step = Math.max(0,Math.min(3,index)); render({ focus }); }
$('case-held').addEventListener('click',()=>{selected='quantity-mismatch';render();});
$('case-amended').addEventListener('click',()=>{selected='approved-amendment';render();});
tabs.forEach((tab,i)=>{
 tab.addEventListener('click',()=>chooseStep(i));
 tab.addEventListener('keydown',event=>{
   const target=event.key==='ArrowRight'?(i+1)%4:event.key==='ArrowLeft'?(i+3)%4:event.key==='Home'?0:event.key==='End'?3:null;
   if(target!==null){event.preventDefault();chooseStep(target);tabs[target].focus();}
 });
});
$('previous').addEventListener('click',()=>chooseStep(step-1,true));$('next').addEventListener('click',()=>chooseStep(step+1,true));
try {
 const response = await fetch('assets/recorded-cases.json');if(!response.ok)throw Error('Recorded case data is unavailable.');data=await response.json();
 if(data.schema!=='silentshift-recorded-tour/1'||data.synthetic!==true||data.cases.length!==2)throw Error('Unsupported recorded selection.');
 const query = new URL(location.href).searchParams;
 if(data.cases.some(row=>row.scenario_id===query.get('case')))selected=query.get('case');
 if(/^[0-3]$/.test(query.get('step')||''))step=Number(query.get('step'));
 await render();
} catch(error){$('tour-error').hidden=false;$('tour-error').textContent=error.message+' The original native evidence remains linked below.';}
