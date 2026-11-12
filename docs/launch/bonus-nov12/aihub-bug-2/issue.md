# %AI.Tool returns character-stream metadata instead of the advertised string contents (154U)

## Environment

- InterSystems IRIS Community AI Hub `2026.3.0AI.154.0`, ARM64, Linux container.
- Exact `$ZVERSION`: `IRIS for UNIX (Ubuntu Server LTS for ARM64 Containers) 2026.3.0AI (Build 154U) Thu Sep 24 2026 10:05:18 EDT`.
- Image ID: `sha256:8fa0ae85777d11ef113ec25a7ac2d1548edfa321a31bcbfa3e0a01ea7dbd8713`.
- Reproduced in three independent, fresh containers with `--network none`, no published ports, source mounts, model, API key or SilentShift classes.

## Summary

A `%AI.Tool` method declared `As %Stream.GlobalCharacter` is advertised by `%Discover()` as returning a JSON string. A normal direct ObjectScript call returns a readable stream with the expected text. Calling the same method through `%AI.ToolMgr.ExecuteTool()` instead returns a JSON object containing stream bookkeeping properties, with the text missing.

The inbound side has a related mismatch: a `%Stream.GlobalCharacter` parameter is advertised as a JSON string, but passing that string through `ExecuteTool()` reaches the method as a scalar, so a normal `data.Read()` fails with `<INVALID OREF>`.

This report is about the built-in stream codec, with the outbound content loss as the primary reproduction. No custom `%Encode`/`%Decode`, policy, Embedded Python, MCP transport or application wrapper is involved.

## Minimal standalone class

Save as `/tmp/StreamTools.cls` inside a disposable IRIS development container:

```objectscript
Class BugProbe.StreamTools Extends %AI.Tool
{
/// Control: the same payload, returned as a string.
Method ReturnText() As %String
{
    Return "Approved amendment: 1 CASE = 12 EA."
}
/// Return the complete evidence text as a character stream.
Method ReturnStream() As %Stream.GlobalCharacter
{
    Set stream = ##class(%Stream.GlobalCharacter).%New()
    Do stream.Write(..ReturnText())
    Do stream.Rewind()
    Return stream
}
/// Read an evidence stream, received from the tool caller.
Method ReadStream(data As %Stream.GlobalCharacter) As %String
{
    Return data.Read()
}
}
```

In namespace USER:

```objectscript
set sc=$system.OBJ.Load("/tmp/StreamTools.cls","ck")
write "COMPILE_OK=",$system.Status.IsOK(sc),!
set tools=##class(BugProbe.StreamTools).%New()
write tools.%Discover().%ToJSON(),!
set direct=tools.ReturnStream()
write "DIRECT_STREAM_TEXT=",direct.Read(),!
set manager=##class(%AI.ToolMgr).%New()
set sc=manager.AddTool(tools)
write "REGISTER_OK=",$system.Status.IsOK(sc),!
write manager.ExecuteTool("ReturnText",{}).%ToJSON(),!
write manager.ExecuteTool("ReturnStream",{}).%ToJSON(),!
```

## Expected

The [documented type mapping](https://github.com/intersystems-community/ai-hub-eap/blob/cf50da7d3074f09e58d6b2b9858aef22cfbd68b6/ObjectScript_SDK_Guide.md#primitive-types) explicitly lists `%Stream.GlobalCharacter` as `{"type":"string"}`; the same section says the mapping applies to both parameters and return types. The framework itself advertises `ReturnStream.returns.type = "string"` on this build.

Accordingly, the stream-returning tool should deliver the character contents as a JSON string, just like the `ReturnText` control, or report a documented unsupported-type error rather than a successful unrelated metadata object. A string supplied according to the advertised input schema should be decoded into a readable character stream before `ReadStream` runs.

The current guide at commit `4199018eb2ec360c7a0ad8e1925fa2a5fef39335` contains the same mapping. The reproduction relies on the installed build's own discovery output as well as the guide, not on an assumption that a newer feature exists in 154U.

## Actual

Direct method control:

```text
DIRECT_STREAM_TEXT=Approved amendment: 1 CASE = 12 EA.
```

Tool-manager string control (variable timing omitted here; exact output retained):

```json
{"value":"Approved amendment: 1 CASE = 12 EA."}
```

Tool-manager stream result, on every fresh run:

```json
{"value":{"%Location":"^CacheStream","AtEnd":false,"Id":"","LineTerminator":"\r\n","RemoveOnClose":false}}
```

The `value` type is `object`, and the original text is absent. The inbound case reports:

```text
READ_STREAM_ERROR=ERROR <%AICore>ToolExecutionFailed: Tool execution failed: IRIS error [INVALID OREF]: <INVALID OREF>ReadStream+1^BugProbe.StreamTools.1
```

A subsequent string control succeeds, so this does not require corrupt or stale manager state.

## Agent-path confirmation

Separately, an ordinary `%AI.Agent.Chat()` used the same standalone tool with a loopback-only fake OpenAI-compatible provider. The provider requested `ReturnStream`; the next request received this tool message:

```json
{
  "content": "{\"%Location\":\"^CacheStream\",\"AtEnd\":false,\"Id\":\"\",\"LineTerminator\":\"\\r\\n\",\"RemoveOnClose\":false}",
  "role": "tool",
  "tool_call_id": "call-stream"
}
```

The evidence text never reached the provider. This used two local HTTP requests and no model inference; it is a transport/control test, not a claim about a model's answer quality. The minimal tool-manager reproduction above needs no provider at all.

## Impact and workaround

A tool returning evidence through the documented character-stream type silently supplies bookkeeping data instead of the evidence. As a bounded workaround, explicitly read small text into a `%String` return value, as in the control method, or implement a deliberate stream codec. The workaround does not establish support for unbounded strings or large payloads.

## Reproduction evidence and duplicate check

Local bundle: `StreamTools.cls`, `repro.in`, `run_repro.py`, `outputs/fresh-1.txt` through `fresh-3.txt`, and `outputs/fresh-reproduction.json`. The runner verifies that the class is absent before loading it into each fresh container and retains exact output plus SHA-256 hashes. `outputs/agent-mock-requests.jsonl` records the separate agent-path observation.

Checked both open and closed reports in `intersystems-community/ai-hub-eap-bugreports`, plus the original `intersystems-community/ai-hub-eap` tracker and available issue comments, on November 12, 2026. No matching stream-codec report was found; snapshots and searches are retained under `reference/`.

- AI Hub #17 (SilentShift's existing report): quoted underscore method-call generation. This repro uses ordinary CamelCase names.
- AI Hub #20: missing/wrong input-schema validation. Here a valid no-argument call returns data incompatible with its own declared return schema.
- AI Hub #22: repeated nested-class schema fields. This repro has no nested argument classes or repeated property types.
- Original tracker #18: MCP calculator execution/JSON framing on build 162U. This repro is in-process on 154U, has no MCP transport, and successfully returns the wrong object.
- Original tracker #45: streaming completion callback visibility. That is provider token streaming, not an ObjectScript character-stream tool value.

No claim about newer builds or organizer bonus eligibility is made. This is an unfiled draft.
