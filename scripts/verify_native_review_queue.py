#!/usr/bin/env python3
"""Prove native pending tasks and concurrent review through the real API.

Creates two isolated synthetic cases in the live production. Their 11-reference
guard skips LLM inference. One is rejected; concurrent identical approvals decide
one. Existing/evaluation cases are untouched; no LLM call is made. Existing procedural retrieval may use local embeddings.
"""
from __future__ import annotations

import argparse
import json
import sys
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

from bootstrap import read_env
from verify_native import Client, native_build
from verify_native_trace import native
from verify_native_workflow import observed, task_checks

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--env-file', type=Path, default=ROOT / '.env')
    parser.add_argument('--context')
    parser.add_argument('--container')
    parser.add_argument('--allow-new-synthetic-cases', action='store_true')
    parser.add_argument('--output', type=Path, default=ROOT / 'evidence/native/review-queue.json')
    args = parser.parse_args()
    if not args.allow_new_synthetic_cases:
        parser.error('Explicit --allow-new-synthetic-cases is required; no LLM calls are made')
    result: dict = {'created_at': datetime.now(timezone.utc).isoformat(), 'llm_calls': 0,
                    'cases': [], 'checks': {}, 'passed': False}
    try:
        env = read_env(args.env_file)
        args.runtime_env = env
        args.context = args.context or env.get('DOCKER_CONTEXT')
        args.container = args.container or env.get('COMPOSE_PROJECT_NAME', ROOT.name.lower()) + '-iris-1'
        api = env.get('SILENTSHIFT_API_URL', 'http://127.0.0.1:52773/silentshift/api')
        reviewer, password = env['SILENTSHIFT_IRIS_USERNAME'], env['SILENTSHIFT_IRIS_PASSWORD']
        client = Client(api, reviewer, password)
        viewer = Client(api, env['SILENTSHIFT_VIEWER_USERNAME'], env['SILENTSHIFT_VIEWER_PASSWORD'])
        status, health = client.call('/health')
        if status != 200 or not native_build(health.get('build')) or not health.get('production', {}).get('running'):
            raise ValueError('Live build154 production is required')
        script = ('set ok=1\nfor f="TraceChecks","WorkflowChecks" {'
                  'set sc=$SYSTEM.OBJ.Load("/opt/silentshift/tests/iris/"_f_".cls","ck") '
                  'if $SYSTEM.Status.IsError(sc) set ok=0}\nwrite "REVIEW_TESTS=",ok,!')
        if native(args, script, 'REVIEW_TESTS=') != '1':
            raise ValueError('Native review inspection classes failed to compile')
        status, _ = viewer.call('/reviews?limit=50&offset=0')
        result['checks']['viewer_queue_denied'] = status == 403
        status, _ = client.call('/reviews?limit=0&offset=0')
        result['checks']['invalid_pagination_denied'] = status == 422
        for action in ('reject', 'approve'):
            case_id = native(args, 'set sc=##class(SilentShift.Test.TraceChecks).RunBudgetCase(.id)\n'
                             'if $SYSTEM.Status.IsOK(sc) write "REVIEW_CASE=",id,!', 'REVIEW_CASE=')
            before = observed(args, case_id)
            checks = task_checks(before, reviewer)
            checks['no_model_invocation'] = (before.get('agent_summary') or {}).get('model_invoked') is False
            status, queue = client.call('/reviews?limit=100&offset=0')
            entries = queue.get('items', []) if isinstance(queue, dict) else []
            matches = [item for item in entries if item.get('case_id') == case_id]
            checks['actual_native_task_in_review_api'] = status == 200 and queue.get('engine') == 'native-iris-workflow' and len(matches) == 1 and matches[0]['task_id'] == str(before['native_task']['task_id']) and matches[0]['case_version'] == before['version']
            request = {'action': action.upper(), 'reason': 'Synthetic native worklist verification: ' + action,
                       'expected_version': before['version'], 'idempotency_key': str(uuid.uuid4())}
            item = {'case_id': case_id, 'action': action, 'before': before, 'request': request, 'checks': checks}
            result['cases'].append(item)
            if not all(checks.values()):
                raise ValueError('Native worklist preflight failed; no decision attempted')
            for label, altered, expected in (
                ('blank_reason_denied', dict(request, reason='  '), 422),
                ('stale_version_denied', dict(request, expected_version=before['version'] - 1), 409),
            ):
                status, _ = client.call(f'/cases/{case_id}/review', altered)
                checks[label] = status == expected
            status, _ = viewer.call(f'/cases/{case_id}/review', request)
            checks['viewer_action_denied'] = status == 403
            if not all(checks.values()):
                raise ValueError('Review boundary failed before decision')
            if action == 'approve':
                barrier = threading.Barrier(2)
                def submit(_: int, barrier=barrier, request=request, case_id=case_id):
                    separate_client = Client(api, reviewer, password)
                    barrier.wait(timeout=10)
                    return separate_client.call(f'/cases/{case_id}/review', request)[0]
                with ThreadPoolExecutor(max_workers=2) as pool:
                    statuses = list(pool.map(submit, (0, 1)))
                item['concurrent_http_statuses'] = statuses
                checks['both_concurrent_requests_completed'] = statuses == [200, 200]
            else:
                status, _ = client.call(f'/cases/{case_id}/review', request)
                checks['rejection_http200'] = status == 200
            after = observed(args, case_id, complete=True)
            item['after'] = after
            checks.update(task_checks(after, reviewer, action))
            expected_count = int(action == 'approve')
            checks['expected_terminal_route'] = after['routing'] == ('DELIVERED' if action == 'approve' else 'REJECTED')
            checks['exactly_one_review_receipt'] = after['review_receipt_count'] == 1
            checks['exactly_one_native_completion_response'] = after['native_completion_response_count'] == 1
            checks['exact_delivery_receipts'] = after['delivery_count'] == after['delivery_receipt_count'] == expected_count
            status, replay = client.call(f'/cases/{case_id}/review', request)
            checks['same_request_replay_stable'] = status == 200 and replay['version'] == after['version'] and replay['delivery_count'] == expected_count
            status, queue = client.call('/reviews?limit=100&offset=0')
            checks['completed_task_leaves_pending_queue'] = status == 200 and not any(t['case_id'] == case_id for t in queue.get('items', []))
            changed = dict(request, reason='Changed review must not reuse the committed key')
            status, _ = client.call(f'/cases/{case_id}/review', changed)
            checks['changed_key_content_denied'] = status == 409
            item['passed'] = all(checks.values())
            print(f'{action}: case={case_id} task={after["native_task"]["task_id"]} trace={after["trace_id"]} checks={sum(checks.values())}/{len(checks)}', flush=True)
            if not item['passed']:
                raise ValueError('Native review final-state check failed')
        result['passed'] = all(result['checks'].values()) and all(c['passed'] for c in result['cases'])
        return 0 if result['passed'] else 1
    except Exception as error:
        result['error'] = str(error) if isinstance(error, ValueError) else type(error).__name__
        print('FAILED: ' + result['error'], file=sys.stderr)
        return 1
    finally:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
        print(f'Native review evidence: {args.output}', flush=True)


if __name__ == '__main__':
    raise SystemExit(main())
