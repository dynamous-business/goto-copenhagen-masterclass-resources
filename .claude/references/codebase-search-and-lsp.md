# Codebase Search and LSP — Context Curation at Scale

On-demand reference for context curation at scale and MCP servers + Tool
Search. Covers when grep stops scaling, how the codebase-search MCP
server works, LSP setup for Python and TypeScript, and the "navigate by symbol,
not grep" rule that makes all of it actually pay off.

---

## When Grep Stops Scaling

Grep matches text. Code navigators need structure. The difference becomes
material around 10K–50K LOC:

| Query | Grep result | Structured result |
|-------|-------------|-------------------|
| Where is `embed_text` defined? | 17 lines across 5 files (imports, the definition, every call site, docstring mentions) | `rag/embeddings.py:43 [function]` — one answer |
| Where is `ChatArea` used? | Every import, the file itself, test fixtures, any string containing the word | Only real JSX call sites and instantiations |
| What does `retriever_hybrid.py` export? | Nothing useful — you'd have to read the whole file | A structured outline of every function signature |

The Anthropic "Building Effective AI Coding Agents" article is explicit: "the
most sophisticated teams built MCP servers exposing **structured** search as a
tool Claude can call directly." Structured means parsing — AST-level, not
substring.

---

## The Codebase-Search MCP Server

Installed at `tooling/mcp/codebase_search.py` in repos that carry this AI Layer.
Wired via `.mcp.json` at the repo root. Claude Code picks it up automatically.

### Three tools

**`where_is(name)`** — find every definition of `name` by parsing AST:
- Python: `def`, `class`, module-level assignments
- TypeScript: `function` declarations, `const x = () =>` arrow functions, `class`, `interface`, `const X = value`
- Returns kind (`function | method | class | constant | arrow_function | interface`), qualified name, and signature
- Zero false hits from comments, imports, or docstrings

**`find_references(name)`** — find every structural use of `name`:
- Python: call expressions (`name(...)`), attribute access (`.name`), name loads
- TypeScript: call expressions, member access, identifier references
- Deduplicates per line, keeping the most specific kind (call beats name load)

**`outline(module)`** — show the public API of one module:
- Accepts a path (`app/backend/rag/retriever_hybrid.py`) or a bare name (`retriever_hybrid`, `ChatArea`)
- Returns definitions in source order with line numbers and signatures
- Works for both Python and TypeScript/TSX

### How it works

```
Python source → ast.parse → _PyDefCollector / _PyRefCollector → Definition / Reference
TypeScript/TSX → tree_sitter.parse (tree-sitter-typescript) → _TsDefCollector / _TsRefCollector
```

ROOT is set from `CLAUDE_PROJECT_DIR` (the env var Claude Code sets when it
runs an MCP server), so the same server code works in any repo without
reconfiguring.

EXCLUDE_DIRS prunes `node_modules`, `.venv`, `dist`, `build`, `.git`, and
similar non-source directories before walking the file tree.

### Running it directly

```bash
# From the project root. The script declares its own dependencies inline
# (PEP 723: mcp, tree-sitter, tree-sitter-typescript), so uv installs them on first run.
uv run --script tooling/mcp/codebase_search.py
```

Claude Code auto-starts it from `.mcp.json` — you only run it directly to debug.

### .mcp.json wiring

```json
{
  "mcpServers": {
    "codebase-search": {
      "command": "uv",
      "args": ["run", "--script", "tooling/mcp/codebase_search.py"]
    }
  }
}
```

The only prerequisite is `uv` itself. Nothing goes into your project's own dependencies.

---

## LSP Setup

Language Server Protocol gives Claude Code "go to definition" and "find all
references" at the level the IDE gives you. Two servers cover the two language
halves of a Python + TypeScript repo.

### Python — pyright

**Install:** add `pyright>=1.1.400` to `[project.optional-dependencies].dev` in
`pyproject.toml` and run `uv sync --extra dev`.

**Configure** (`[tool.pyright]` in `pyproject.toml`):

```toml
[tool.pyright]
extraPaths = ["."]         # or [".", ".."] if the package is run from the parent dir
venvPath = "."
venv = ".venv"
typeCheckingMode = "standard"
reportMissingImports = true
pythonVersion = "3.11"
```

`extraPaths` lets pyright resolve your project's internal imports. `venvPath`/`venv`
points it at the uv-managed virtualenv so third-party stubs resolve.

**Verify:**
```bash
uv run pyright .                              # type-check
```

### TypeScript — typescript-language-server

**Install:** add `"typescript-language-server": "^4.3.3"` to `devDependencies`
in `package.json` and run `bun install` (or `npm install`).

```bash
bun install   # installs the binary at node_modules/.bin/typescript-language-server
```

**Verify:**
```bash
ls node_modules/.bin/typescript-language-server   # binary present
bun run tsc --noEmit                              # type-check passes
```

Claude Code auto-discovers the binary from the project's `node_modules/.bin`
once it's installed. No further configuration needed — the existing `tsconfig.json`
covers path resolution.

---

## The Navigation Rule

Installing the servers is step one. The rule is what makes Claude actually use them:

> **Navigate by symbol, not by grep.**
>
> - For Python: use pyright go-to-definition / find-all-references to navigate
>   to function definitions, class declarations, and call sites.
> - For TypeScript: use typescript-language-server go-to-definition the same way.
> - Use the `codebase-search` MCP tools (`where_is`, `find_references`, `outline`)
>   for cross-language structural queries.
> - Use grep only for: literal string searches, scanning comments/config, or
>   finding files that import a module by path.

This rule goes in the root `CLAUDE.md` under a "Navigate by Symbol, not by Grep"
heading.

### Why this matters for agent productivity

An agent using grep to find a symbol's definition reads N files to filter the
false hits. An agent using go-to-definition reads one. At 50K LOC, that N is
50–100. The difference compounds across every task in a session. Context
curation at scale is, at its core, replacing grep-and-scan with
parse-and-navigate.

---

## Adding to a New Repo

1. Copy `tooling/mcp/codebase_search.py` into the target repo.
2. Add `.mcp.json` (or merge into existing) with the `codebase-search` server entry above.
   The script carries its own dependencies inline, so there is nothing else to install besides `uv`.
3. Python half: add `pyright>=1.1.400` to dev extras and the `[tool.pyright]` config.
4. TypeScript half: add `typescript-language-server` to `devDependencies`.
5. Add the "navigate by symbol" rule to the root `CLAUDE.md`.
6. Confirm it's wired: ask the agent to `where_is` a real cross-file symbol, then go-to-definition on it, and
   compare with what grep returns.
