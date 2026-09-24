# Claude Agent SDK Python mechanics

Read this only after the workflow topology is approved. This is deliberately not a complete program. Select the smallest isolated pattern the design requires; do not combine these patterns by default or invent a fix loop, review stage, guard, retry, or dependency because it appears here.

Verify every used field against the current official Python reference and the installed `ClaudeAgentOptions` type before building. The notes below describe the behavior verified against `claude-agent-sdk` 0.2.139, not a permanent API contract.

## Configuration choices

- The SDK uses a minimal system prompt unless the design explicitly selects the Claude Code preset: `system_prompt={"type": "preset", "preset": "claude_code"}`.
- Omitting `setting_sources` currently loads user, project, and local filesystem sources. Use `setting_sources=["project"]` for shared repository context without personal/local settings, or `setting_sources=[]` for none.
- `tools` controls which tools exist. `allowed_tools` pre-approves matching tools; it is not an availability whitelist. Unlisted tools fall through to the permission mode or callback.
- Set model, tools, permissions, sources, turns, budget, and effort per stage. Do not reuse one options object when stages have different contracts.
- Python sessions normally write resumable transcripts to disk. When the approved contract requires an in-memory-only call, verify the current Python/CLI support. Version 0.2.139 can forward the installed CLI's `--no-session-persistence` flag with `extra_args={"no-session-persistence": None}`; treat this escape hatch as version-specific.

## Fresh one-shot query

Use `query()` for one independent exchange. Consume the iterator through its `ResultMessage`; merely constructing it does no work.

```python
result: ResultMessage | None = None
async for message in query(prompt=prompt, options=options):
    if isinstance(message, AssistantMessage):
        observe_selected_blocks(message.content)
    elif isinstance(message, ResultMessage):
        result = message

if result is None or result.is_error:
    raise WorkflowError("stage did not complete")
```

Translate only approved events into operator-facing progress. Do not dump raw messages or transcripts.

## Persistent conversation

Use `ClaudeSDKClient` only when later turns need the same conversation state, such as an approved correction loop. Each sent turn must be drained before the next one.

```python
async with ClaudeSDKClient(options=options) as client:
    await client.query(first_prompt)
    async for message in client.receive_response():
        observe(message)

    await client.query(follow_up)
    async for message in client.receive_response():
        observe(message)
```

Do not introduce persistence merely to avoid passing a small explicit value between independent stages.

## Permission callback

Use `can_use_tool` only when the application must decide about a tool call at runtime. Keep tools that require the callback out of `allowed_tools`; pre-approved calls bypass it. Prefer `tools` plus a non-bypassing permission mode when a static availability boundary is sufficient.

## Structured handoff

Use `output_format={"type": "json_schema", "schema": schema}` when a downstream stage genuinely needs a typed in-memory value. Keep the schema shallow and include only fields the recipient consumes. At the boundary, check the result exists and validate workflow-specific invariants that the schema cannot express; do not reimplement a general JSON Schema validator or duplicate the whole contract across schemas, model classes, and rendering types.

Do not add a schema, validation library, or verbose raw JSON artifact when plain text or one directly written artifact is the approved handoff. If type plumbing dominates the program, reduce the handoff rather than adding an abstraction.

Structured-output finalization consumes turn and budget headroom. Keep prompts focused and reserve capacity for the final schema emission.

## Deterministic subprocess

Run objective checks in ordinary code and preserve their exact command, working directory, exit code, and relevant output. A PEP 723 `uv` script should remove its own `VIRTUAL_ENV` from the child environment before invoking the target project's `uv run`, so uv selects the project environment without a mismatch warning.

```python
child_env = os.environ.copy()
child_env.pop("VIRTUAL_ENV", None)
completed = subprocess.run(
    command,
    cwd=checks_dir,
    env=child_env,
    capture_output=True,
    text=True,
    check=False,
)
```

## Bounds and failures

- Treat configured bounds and SDK-reported usage as different fields; report both without rewriting either.
- Catch documented SDK failures at the stage boundary and retain the stage name. Keep one outer executable boundary for unexpected runtime exceptions, because CLI terminal conditions may not always arrive as an SDK-specific exception.
- Do not retry unless the approved design names the retry condition, destination, evidence, and cap.
- On failure, do not write a success-shaped final artifact from partial agent results.
