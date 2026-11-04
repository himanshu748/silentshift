Include %occStatus

/// Explicit operator playback, restricted to one frozen synthetic held case.
/// It never opens a network connection or generates a new recommendation.
Class SilentShift.Provider.Replay Extends %RegisteredObject
{
Parameter RECORDID = "quantity-mismatch-recorded-1471-v1";

ClassMethod CheckCase(caseId As %String) As %Status
{
    Try {
        Set body = ##class(SilentShift.Store).CaseJSON(caseId)
        If '..MatchesCase(body) Return $$$ERROR($$$GeneralError,"PROVIDER_REPLAY_SYNTHETIC_SCOPE_REQUIRED")
        Return $$$OK
    } Catch error {
        Return $$$ERROR($$$GeneralError,"PROVIDER_REPLAY_SYNTHETIC_SCOPE_REQUIRED")
    }
}

ClassMethod MatchesCase(body As %String) As %Boolean [ Language = python ]
{
    import iris, json
    try:
        data = json.loads(body)
        if (data.get('synthetic') is not True
                or data.get('scenario_id') != 'quantity-mismatch'
                or data.get('routing') != 'PROCESSING'
                or data.get('assessment', {}).get('critical') is not True):
            return False
        from pathlib import Path
        dataset = json.loads(Path(iris.cls('SilentShift.IPM').AssetPath('fixtures/v1/scenarios.json')).read_text())
        original = next(s['message'] for s in dataset['scenarios'] if s['id'] == 'quantity-mismatch')
        message = data.get('message', {})
        fields = set(original) - {'event_id', 'correlation_id'}
        return (data.get('dataset_version') == dataset['dataset_version']
                and set(message) == set(original)
                and all(message.get(k) == original[k] for k in fields)
                and data['assessment'].get('evidence_ids') == ['contract:PO-2048:v1'])
    except (ValueError, KeyError, StopIteration, OSError, TypeError, AttributeError):
        return False
}

/// The recorded assistant text is exact. Tool envelopes are deterministic
/// reconstruction; their zero-argument tools still execute in native AI Hub.
/// Original token usage remains in fixture provenance, never today's usage.
ClassMethod Response(raw As %String, round As %Integer) As %String [ Language = python ]
{
    import hashlib, iris, json
    from pathlib import Path
    path = Path(iris.cls('SilentShift.IPM').AssetPath('fixtures/provider-replay.json'))
    if path.stat().st_size > 16384:
        raise ValueError('Replay fixture exceeds bound')
    fixture = json.loads(path.read_text())
    text = fixture['assistant_content']
    if (fixture['schema'] != 'silentshift-provider-replay/1'
            or fixture['id'] != 'quantity-mismatch-recorded-1471-v1'
            or hashlib.sha256(text.encode()).hexdigest() != fixture['recording']['raw_assistant_sha256']):
        raise ValueError('Replay fixture provenance differs')
    tools = ['GetCurrentMessage', 'GetApprovedContracts', 'GetRelatedRecords', 'find_similar_precedents']
    if fixture['tool_sequence'] != tools or round not in range(1, 6):
        raise ValueError('Replay round differs')
    request = json.loads(raw)
    messages = request.get('messages', [])
    completed = [m for m in messages if m.get('role') == 'tool']
    if len(completed) != round - 1:
        raise ValueError('Replay tool progression differs')
    message = {'role': 'assistant', 'content': text if round == 5 else None}
    if round < 5:
        message['tool_calls'] = [{'id': 'replay_tool_' + str(round), 'type': 'function',
            'function': {'name': tools[round - 1], 'arguments': '{}'}}]
    # No usage field: original recording counts are not current inference.
    return json.dumps({'id': 'recorded-response-' + str(round), 'object': 'chat.completion',
        'created': 0, 'model': fixture['recording']['model'],
        'choices': [{'index': 0, 'message': message,
            'finish_reason': 'stop' if round == 5 else 'tool_calls'}]}, separators=(',', ':'))
}
}
