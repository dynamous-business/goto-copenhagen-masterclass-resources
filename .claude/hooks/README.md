# Hooks — the deterministic layer of the AI Layer

Hooks are the fifth primitive. Rules, subagents, tools, and skills are all things the agent *reaches for*.
A hook is the one the agent never chooses: it fires automatically on a lifecycle event.

> **A rule asks the agent to behave. A hook guarantees it.**
>
> Reach for a rule when "usually" is fine. Reach for a hook when it **must** happen every single time.

## What ships here

| File | Event | What it does | Can it block? |
|---|---|---|---|
| `pre_tool_use.py` | **PreToolUse** | Blocks reading/writing/searching a real env file (committed `.env.example` templates are allowed) and blocks `rm -rf`. Prints the reason to stderr and `exit(2)` → the tool is stopped and the agent is told why, so it adapts. | **Yes** — this is the guarantee |
| `post_tool_use.py` | **PostToolUse** | Appends every tool call to `logs/post_tool_use.json` — a full audit trail of what the agent did. | No — the tool already ran; observe only |

That split *is* the mental model: **pre = gate, post = log.**

## Also here, and deliberately NOT switched on

Three **automation** hooks. They do a different job from the two above: those are always-on safety, these drive a workflow. A hook only exists once it is wired into `.claude/settings.json`, so as files on disk these are **inert**.

| File | Event | Shape | What it does |
|---|---|---|---|
| `format-touched.sh` | PostToolUse `Edit\|Write` | **REACT** | Formats the file that was just touched |
| `stop-gate.sh` | Stop | **GATE** | Refuses to let the session finish until the checks are green. Skips a clean worktree; converts a checker's exit 1 into the **exit 2** that actually blocks |
| `baton.sh` | Stop (`async`) | **BATON** | Issue artifact present and fix output absent, so it launches the fix skill in a fresh `claude -p`. Keeps an in-flight marker on disk |

`automation-hooks.settings.json` is the stanza that wires them up. Merge its `hooks` block into your own `.claude/settings.json` when you want the behaviour.

> ⚠️ **Think before you merge it.** Hooks fire on *every* session in the repo they are configured in, not just the one you had in mind. `stop-gate.sh` will stop you ending a session while checks are red, and `baton.sh` spawns a fresh `claude -p` on every Stop. That is exactly what they are for, and it is also why they ship switched off.

They are worth reading even switched off, because the three shapes are the whole vocabulary: **react** to something that happened, **gate** something from finishing, and **hand the baton** to the next agent. With `pre = gate, post = log` above, that is every hook you are likely to write.

### Exit codes — the one thing to get right

**Only `exit 2` blocks.** Not exit 1, which is what every linter, type checker and test runner returns on failure. Converting one into the other is most of what a gate hook does.

| Exit | Meaning |
|---|---|
| `0` | success. stdout goes to the debug log (except on `UserPromptSubmit` / `SessionStart`, where it becomes context) |
| **`2`** | **blocking error.** stderr is handed to the agent as the reason |
| anything else | non-blocking error: noise, no effect |

What `exit 2` blocks depends on the event, and these hooks sit on events with different answers:

| Event | Does `exit 2` block? |
|---|---|
| `PreToolUse` | **yes** — the tool call is stopped (`pre_tool_use.py` relies on this) |
| `Stop` | **yes** — the session is prevented from finishing (`stop-gate.sh` relies on this) |
| `PostToolUse` | **no** — the tool already ran; stderr is merely shown, so `format-touched.sh` always exits 0 |

`baton.sh` is `async`, which is fire-and-forget: its exit code is never read, so it exits 0 throughout.

⚠️ Both scripts assume your project's real check commands. They ship wired for the feature-flag exercise (`pnpm` build, lint and test in `server/` and `client/`, and `eslint --fix` on touched TypeScript). Open them before wiring them up in your own project: `stop-gate.sh` in particular runs a checker that must exit non-zero on failure, and `format-touched.sh` formats with a specific tool. See `automations/README.md` for the same configure-before-you-run point applied to the two workflow templates.

## Turning them on

Hooks are the one primitive that does something the moment it exists, so the pack ships the wiring as a
**template** rather than a live file (same idea as `.claude/CLAUDE.md.template`). Copy it in your project:

```bash
cp .claude/settings.json.example .claude/settings.json
```

Nothing is switched on until you create `.claude/settings.json`, so the hooks don't fire while you're reading
the material. **In your own project, commit it** — that's how the whole team inherits the same guarantees.
If you already have a `settings.json`, merge the `hooks` block in rather than overwriting it.

## Try it

```
ask the agent to read your env file          -> blocked (exit 2, reason handed back)
ask it to read server/.env.example           -> allowed
ask it to run `rm -rf ...`                   -> blocked
any normal command                           -> allowed, and logged to logs/post_tool_use.json
```

You can also test a hook directly, without the agent:

```bash
echo '{"tool_name":"Read","tool_input":{"file_path":".env"}}' | uv run .claude/hooks/pre_tool_use.py; echo "exit=$?"
```

`exit=2` means the guard fired.

## Adding your own — you don't have to write Python

Use the **`hooks-create`** skill and describe the guarantee in plain English:

```
/hooks-create "Don't let the agent finish until my tests pass — run my test command when it tries to stop, and if it fails, block the stop and tell it to fix the failures."
```

It picks the right lifecycle event, writes the script, and merges it into `settings.json`.
Common ones worth adding:

- **stop-until-green** (`Stop`) — the agent can't declare done while tests are red.
- **protected paths** (`PreToolUse`) — never edit `migrations/`, prod config, or lockfiles.
- **auto-format** (`PostToolUse`) — format every file the moment it's edited.

## Loading a steering document at session start

A `SessionStart` hook's stdout is added to the conversation as context, so one line makes a steering document
deterministic instead of relying on a skill to go and read it:

```json
{
  "hooks": {
    "SessionStart": [
      { "hooks": [ { "type": "command", "command": "cat .claude/references/direction.md" } ] }
    ]
  }
}
```

Two honest notes. The cheaper default is the pointer the pack already ships: the plan, implement, and review
skills read `engineering.md` and `direction.md` themselves when the file exists, so only the runs that judge
code or scope pay for it. The hook is the deterministic option: it costs those tokens on every session,
including a one-line question, in exchange for never depending on the skill remembering. Pick per document.
Either way the document is just markdown loaded when it is needed.

## Two things to know

- **Hooks run real code, automatically, with your credentials, with no sandbox.** Review a hook the way you'd
  review a CI script. Only run hooks you have read and trust. This is the same caution as MCP servers.
- **Coverage is yours.** The hook is guaranteed to *run*; what it *catches* is only as good as the check you
  wrote. It is the enforcement point, not omniscience.

  Concretely, `pre_tool_use.py` covers three routes to a secret: the **env file**, the **other credential
  files** (ssh keys, `.pem`, `.aws/credentials`, `.netrc`, `credentials.json`), and the **process environment**
  (the env-dumping shell builtins, a bare `env`, echoing a `*_KEY` / `*_TOKEN` variable, or code that reads the
  environment map). That last route matters more than it looks — a guard that blocks the env *file* but not the
  *environment* is mostly theatre, because the same values are sitting right there in the shell.

  **What it deliberately does not cover: the two-step attack.** Nothing stops the agent *writing* a script that
  reads the environment and then running it — the run looks innocent, because the secret-handling lives in a
  file that was just created. Closing that means inspecting the **content** of `Write`/`Edit` calls, not just
  the command, which is a genuinely different check and roughly triples the size of this file. If you are
  guarding something that matters, that is the next thing to add.

## Portability

This is not a Claude Code party trick. Codex and Cursor use the same shape (a script, JSON on stdin,
`exit 2` to block); Gemini CLI does the same job by reading a structured JSON decision instead of the exit
code; Pi and opencode run hooks in-process as plugins. Learn it once, it transfers — the same way `AGENTS.md`
became the shared rules file.

## Two things to know

- **Hooks run real code, automatically, with your credentials, with no sandbox.** Review a hook the way you'd
  review a CI script. Only run hooks you have read and trust. This is the same caution as MCP servers.
- **Coverage is yours.** The hook is guaranteed to *run*; what it *catches* is only as good as the check you
  wrote. It is the enforcement point, not omniscience.

  Concretely, `pre_tool_use.py` covers three routes to a secret: the **env file**, the **other credential
  files** (ssh keys, `.pem`, `.aws/credentials`, `.netrc`, `credentials.json`), and the **process environment**
  (the env-dumping shell builtins, a bare `env`, echoing a `*_KEY` / `*_TOKEN` variable, or code that reads the
  environment map). That last route matters more than it looks — a guard that blocks the env *file* but not the
  *environment* is mostly theatre, because the same values are sitting right there in the shell.

  **What it deliberately does not cover: the two-step attack.** Nothing stops the agent *writing* a script that
  reads the environment and then running it — the run looks innocent, because the secret-handling lives in a
  file that was just created. Closing that means inspecting the **content** of `Write`/`Edit` calls, not just
  the command, which is a genuinely different check and roughly triples the size of this file. If you are
  guarding something that matters, that is the next thing to add.

## Portability

This is not a Claude Code party trick. Codex and Cursor use the same shape (a script, JSON on stdin,
`exit 2` to block); Gemini CLI does the same job by reading a structured JSON decision instead of the exit
code; Pi and opencode run hooks in-process as plugins. Learn it once, it transfers — the same way `AGENTS.md`
became the shared rules file.
