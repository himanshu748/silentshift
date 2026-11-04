#!/usr/bin/env python3
"""Run frozen scenario A and print its real native session / Visual Trace URL.

Default requires operator-configured recorded playback and performs no inference.
--live explicitly permits one real local Ollama investigation instead. Replay
records are never accepted as live verification or as model-quality evidence.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import time
from urllib.parse import urlparse
import uuid
from bootstrap import read_env
from verify_native import Client
from verify_native_trace import native

ROOT=Path(__file__).resolve().parents[1]


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--api',default=os.environ.get('SILENTSHIFT_API_URL','http://127.0.0.1:52773/silentshift/api'))
    p.add_argument('--env-file',type=Path,default=ROOT/'.env')
    p.add_argument('--context',default='colima-silentshift')
    p.add_argument('--container',default='silentshift-clean-iris-1')
    p.add_argument('--live',action='store_true')
    p.add_argument('--output',type=Path,default=ROOT/'evidence/native/idea-trace-example.json')
    args=p.parse_args(); values={**read_env(args.env_file),**os.environ}
    args.runtime_env=values
    expected='live' if args.live else 'recorded-replay'
    result={'created_at':datetime.now(timezone.utc).isoformat(),'execution_mode':expected,'passed':False}
    try:
        actual=native(args,'write "SS_PROVIDER_MODE=",##class(SilentShift.Provider.Lease).ExecutionMode(),!','SS_PROVIDER_MODE=')
        if actual!=expected:raise ValueError('Runtime provider mode is '+actual+'; expected '+expected+'. Configure the container explicitly before running.')
        names=('SILENTSHIFT_IRIS_USERNAME','SILENTSHIFT_IRIS_PASSWORD')
        if any(not values.get(k) for k in names):raise ValueError('Missing reviewer environment credentials; values are never printed')
        client=Client(args.api,*(values[k] for k in names))
        status,record=client.call('/scenarios/quantity-mismatch/run',{'run_id':str(uuid.uuid4())})
        if status!=200 or not isinstance(record,dict):raise ValueError('Scenario request failed with HTTP '+str(status))
        for _ in range(20):
            if record.get('routing')!='PROCESSING':break
            time.sleep(.25);status,record=client.call('/cases/'+record['id'])
            if status!=200:raise ValueError('Persisted case readback failed')
        case=record['id']
        if not re.fullmatch(r'[A-Fa-f0-9-]{36}',case):raise ValueError('Invalid returned case identifier')
        export=json.loads(native(args,'write "SS_PROVIDER_EXPORT=",##class(SilentShift.Test.ProviderChecks).InspectCase("'+case+'"),!','SS_PROVIDER_EXPORT='))
        messages=export['provider_messages'];responses=[m for m in messages if m['event_kind']=='provider_response']
        headers={str(h['id']):h for h in export['native_headers']}
        agent=record.get('agent') or {}; reads=agent.get('tool_reads') or {}
        checks={
            'held_without_delivery':record.get('routing')=='QUARANTINED' and record.get('delivery_count')==0,
            'critical_policy_veto':(record.get('policy') or {}).get('decision')=='QUARANTINE',
            'four_native_tool_reads':all(reads.get(k)==1 for k in ('message','contracts','related','precedents')),
            'provider_pairs_present':len(responses)>0 and len(messages)==len(responses)*2,
            'same_case_session':all(str(m['production_session_id'])==str(record['trace_id']) and m['case_id']==case for m in messages),
            'response_headers_paired':all(str(headers[str(m['message_header_id'])]['corresponding_message_id']) in headers for m in responses),
            'execution_mode_labeled':all(m.get('execution_mode')==expected for m in messages),
            'model_provider_prompt_timing':all(m.get('model') and m.get('provider') and m.get('prompt_version') and m.get('duration_ms',-1)>=0 for m in responses),
            'cost_and_provider_retries_unknown':all(m.get('billing_cost') is None and m.get('provider_retry_count') is None for m in messages),
            'no_transient_payloads':export['transient_call_count']==0,
        }
        if args.live:
            checks['actual_upstream_http']=all(m['upstream_http_status']==200 for m in responses)
            checks['live_mode']=agent.get('mode')=='native-ai-hub' and agent.get('model_invoked') is True
        else:
            checks['five_recorded_responses']=len(responses)==5
            checks['no_upstream_inference']=agent.get('model_invoked') is False and agent.get('mode')=='native-ai-hub-recorded-replay' and all(m['upstream_http_status'] is None and m['response_usage'] is None and m['usage_scope']=='unavailable_for_replay' for m in responses)
        parsed=urlparse(args.api)
        trace_url=parsed.scheme+'://'+parsed.netloc+'/csp/silentshift/EnsPortal.VisualTrace.zen?SESSIONID='+str(record['trace_id'])
        result.update({'case_id':case,'session_id':str(record['trace_id']),'visual_trace_url':trace_url,
            'routing':record['routing'],'delivery_count':record['delivery_count'],'checks':checks,
            'provider_messages':messages,'native_headers':export['native_headers'],'agent_mode':agent.get('mode'),
            'passed':all(checks.values())})
        print('execution_mode='+expected+'; fresh_inference='+str(args.live).lower())
        print('case_id='+case+'; session_id='+str(record['trace_id']))
        print('visual_trace_url='+trace_url)
        print('provider_pairs='+str(len(responses))+'; four_tools=1_each; routing='+record['routing']+'; delivery_count='+str(record['delivery_count']))
        print('checks='+str(sum(checks.values()))+'/'+str(len(checks))+'; passed='+str(result['passed']).lower())
        return 0 if result['passed'] else 1
    except (OSError,ValueError,KeyError,TypeError) as e:
        result['error']=str(e); print('Trace example stopped: '+str(e)); return 1
    finally:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':raise SystemExit(main())
