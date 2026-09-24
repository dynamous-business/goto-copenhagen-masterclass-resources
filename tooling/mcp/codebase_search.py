"""Codebase-search MCP server — AST-based structured search for Python AND TypeScript/TSX.

Ported from the Helpline AI Layer and extended for cross-language repos. The
original server covered Python only; this version adds TypeScript/TSX parsing
via tree-sitter so a React frontend is equally searchable.

The article: "the most sophisticated teams built MCP servers exposing structured
search as a tool Claude can call directly."

*Structured* is the operative word. This server parses every module (Python via
`ast`, TypeScript/TSX via `tree-sitter`) and answers questions about code
**structure** — definitions, references, and module shape. It never
substring-matches: grep already does that, and the article is explicit that
moving past text-pattern matching is the whole point.

Tools:
  - where_is(name)        : every definition of `name` across Python and TS/TSX
                            source — function, method, class, constant, arrow
                            function, interface — with kind and source location.
  - find_references(name) : every use of `name` — calls, member access, and
                            name loads — across both language families.
  - outline(module)       : the structured public API of one module — classes,
                            methods, and functions with signatures, in source
                            order.

Language coverage:
  - Python  : standard library `ast` module (unchanged from Helpline)
  - TypeScript (.ts)  : tree-sitter + tree-sitter-typescript
  - TSX (.tsx)        : tree-sitter + tree-sitter-typescript (tsx grammar)
  - JavaScript (.js, .jsx) : treated as TypeScript — tree-sitter-typescript
                              parses modern JS (including JSX via tsx grammar)

Run directly (self-contained — uv installs the inline dependencies below):
  uv run --script tooling/mcp/codebase_search.py
"""

# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "mcp>=1.2,<2",
#     "tree-sitter>=0.23,<0.26",
#     "tree-sitter-typescript>=0.23",
# ]
# ///

from __future__ import annotations

import ast
import os
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from mcp.server.fastmcp import FastMCP

if TYPE_CHECKING:
    pass

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Resolve against the project Claude Code is operating in — so the same server
# works repo-local (via .mcp.json) in any repository.
ROOT = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path.cwd())

# Dependencies, caches, build output, and AI-Layer config are never "the
# codebase" — skip them so the index is repo source only, in any repo.
EXCLUDE_DIRS = frozenset({
    ".git", ".venv", "venv", "env", "node_modules", "__pycache__",
    ".pytest_cache", ".mypy_cache", ".ruff_cache", "build", "dist",
    ".claude", ".tox", "site-packages", "coverage", ".next", ".nuxt",
    ".turbo", "out", ".cache",
})

mcp = FastMCP("codebase-search")


# ---------------------------------------------------------------------------
# Shared data types
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Definition:
    path: str
    line: int
    kind: str   # "function" | "method" | "class" | "constant" | "interface" | "arrow_function"
    qualname: str
    signature: str


@dataclass(frozen=True)
class Reference:
    path: str
    line: int
    kind: str   # "call" | "attribute" | "name" | "member"
    text: str


# ---------------------------------------------------------------------------
# File discovery
# ---------------------------------------------------------------------------

def _files_by_ext(*exts: str) -> list[Path]:
    """All source files with the given extensions, pruning exclude dirs."""
    files: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for filename in filenames:
            if any(filename.endswith(ext) for ext in exts):
                files.append(Path(dirpath) / filename)
    return sorted(files)


def _python_files() -> list[Path]:
    return _files_by_ext(".py")


def _ts_files() -> list[Path]:
    """TypeScript, TSX, JavaScript, JSX source files."""
    return _files_by_ext(".ts", ".tsx", ".js", ".jsx")


def _all_source_files() -> list[Path]:
    return sorted(_python_files() + _ts_files())


def _rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


# ---------------------------------------------------------------------------
# Python helpers (unchanged from Helpline)
# ---------------------------------------------------------------------------

def _parse_py(path: Path) -> ast.Module | None:
    try:
        return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, SyntaxError):
        return None


def _module_name(path: Path) -> str:
    return _rel(path).removesuffix(".py").replace("/", ".")


def _signature(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    args = ast.unparse(node.args)
    returns = f" -> {ast.unparse(node.returns)}" if node.returns is not None else ""
    prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
    return f"{prefix} {node.name}({args}){returns}"


class _PyDefCollector(ast.NodeVisitor):
    """Collects every definition in one Python module."""

    def __init__(self, module: str, relpath: str) -> None:
        self.module = module
        self.relpath = relpath
        self.stack: list[tuple[str, str]] = []  # (name, "class" | "func")
        self.defs: list[Definition] = []

    def _qual(self, name: str) -> str:
        return ".".join([self.module, *(n for n, _ in self.stack), name])

    def _enclosing_is_class(self) -> bool:
        return bool(self.stack) and self.stack[-1][1] == "class"

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.defs.append(Definition(
            self.relpath, node.lineno, "class",
            self._qual(node.name), f"class {node.name}",
        ))
        self.stack.append((node.name, "class"))
        self.generic_visit(node)
        self.stack.pop()

    def _record_func(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        kind = "method" if self._enclosing_is_class() else "function"
        self.defs.append(Definition(
            self.relpath, node.lineno, kind,
            self._qual(node.name), _signature(node),
        ))
        self.stack.append((node.name, "func"))
        self.generic_visit(node)
        self.stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._record_func(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._record_func(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        if not self.stack:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.defs.append(Definition(
                        self.relpath, node.lineno, "constant",
                        self._qual(target.id), target.id,
                    ))
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if not self.stack and isinstance(node.target, ast.Name):
            self.defs.append(Definition(
                self.relpath, node.lineno, "constant",
                self._qual(node.target.id), node.target.id,
            ))
        self.generic_visit(node)


class _PyRefCollector(ast.NodeVisitor):
    """Collects every reference to one name in a Python module."""

    def __init__(self, relpath: str, name: str) -> None:
        self.relpath = relpath
        self.name = name
        self.refs: list[Reference] = []

    def visit_Call(self, node: ast.Call) -> None:
        func = node.func
        called = (
            func.id if isinstance(func, ast.Name)
            else func.attr if isinstance(func, ast.Attribute)
            else None
        )
        if called == self.name:
            self.refs.append(Reference(self.relpath, node.lineno, "call", f"{self.name}(...)"))
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if node.attr == self.name:
            self.refs.append(Reference(self.relpath, node.lineno, "attribute", f".{self.name}"))
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        if node.id == self.name and isinstance(node.ctx, ast.Load):
            self.refs.append(Reference(self.relpath, node.lineno, "name", self.name))
        self.generic_visit(node)


# ---------------------------------------------------------------------------
# TypeScript/TSX helpers (tree-sitter based)
# ---------------------------------------------------------------------------

def _ts_parsers() -> tuple | None:
    """Return (ts_parser, tsx_parser) or None if tree-sitter is unavailable."""
    try:
        import tree_sitter_typescript as ts_ts
        from tree_sitter import Language, Parser
        ts_parser = Parser(Language(ts_ts.language_typescript()))
        tsx_parser = Parser(Language(ts_ts.language_tsx()))
        return ts_parser, tsx_parser
    except Exception:
        return None


# Cache parsers at module level so they are created once.
_TS_PARSERS = _ts_parsers()


def _get_ts_parser(path: Path):  # type: ignore[return]
    """Return the right parser for .ts vs .tsx/.jsx files."""
    if _TS_PARSERS is None:
        return None
    ts_parser, tsx_parser = _TS_PARSERS
    if path.suffix in (".tsx", ".jsx"):
        return tsx_parser
    return ts_parser


def _parse_ts(path: Path):
    """Parse a TS/TSX/JS/JSX file, return the tree-sitter Tree or None."""
    parser = _get_ts_parser(path)
    if parser is None:
        return None
    try:
        source = path.read_bytes()
        return parser.parse(source), source
    except OSError:
        return None


def _ts_node_text(node, source: bytes) -> str:
    """Extract the source text of a tree-sitter node."""
    return source[node.start_byte:node.end_byte].decode("utf-8", errors="replace")


def _ts_collect_defs(path: Path, relpath: str) -> list[Definition]:
    """Walk a TS/TSX AST and collect every definition.

    Handles:
    - function_declaration          → "function"
    - method_definition             → "method" (inside class_body)
    - class_declaration             → "class"
    - lexical_declaration const x = arrow_function → "arrow_function"
    - lexical_declaration const X = non-function   → "constant"
    - export_statement wrapping any of the above
    - interface_declaration         → "interface"
    """
    result = _parse_ts(path)
    if result is None:
        return []
    tree, source = result
    defs: list[Definition] = []
    _walk_ts_defs(tree.root_node, source, relpath, defs, class_stack=[])
    return defs


def _walk_ts_defs(
    node,
    source: bytes,
    relpath: str,
    defs: list[Definition],
    class_stack: list[str],
) -> None:
    """Recursive TS AST walker for definition extraction."""
    node_type = node.type

    # Unwrap export_statement — the interesting child is the declaration inside.
    if node_type == "export_statement":
        for child in node.children:
            if child.type not in ("export", "default", "declare", ";", "type"):
                _walk_ts_defs(child, source, relpath, defs, class_stack)
        return

    if node_type == "function_declaration":
        name_node = node.child_by_field_name("name")
        if name_node:
            name = _ts_node_text(name_node, source)
            kind = "method" if class_stack else "function"
            sig = _ts_func_sig(node, source, name)
            qualname = ".".join(class_stack + [name]) if class_stack else name
            defs.append(Definition(relpath, node.start_point[0] + 1, kind, qualname, sig))
        # Recurse into function body for nested defs.
        for child in node.children:
            if child.type == "statement_block":
                _walk_ts_defs(child, source, relpath, defs, class_stack)
        return

    if node_type == "class_declaration":
        name_node = node.child_by_field_name("name")
        if name_node:
            name = _ts_node_text(name_node, source)
            qualname = ".".join(class_stack + [name]) if class_stack else name
            defs.append(Definition(relpath, node.start_point[0] + 1, "class", qualname, f"class {name}"))
            body = node.child_by_field_name("body")
            if body:
                for child in body.children:
                    _walk_ts_defs(child, source, relpath, defs, class_stack + [name])
        return

    if node_type == "interface_declaration":
        name_node = node.child_by_field_name("name")
        if name_node:
            name = _ts_node_text(name_node, source)
            qualname = ".".join(class_stack + [name]) if class_stack else name
            defs.append(Definition(
                relpath, node.start_point[0] + 1, "interface", qualname, f"interface {name}",
            ))
        return

    if node_type == "method_definition":
        name_node = node.child_by_field_name("name")
        if name_node:
            name = _ts_node_text(name_node, source)
            qualname = ".".join(class_stack + [name]) if class_stack else name
            sig = _ts_method_sig(node, source, name)
            defs.append(Definition(relpath, node.start_point[0] + 1, "method", qualname, sig))
        return

    if node_type == "lexical_declaration":
        # const X = ... or const X = () => ...
        for child in node.children:
            if child.type == "variable_declarator":
                id_node = child.child_by_field_name("name")
                val_node = child.child_by_field_name("value")
                if id_node:
                    name = _ts_node_text(id_node, source)
                    qualname = ".".join(class_stack + [name]) if class_stack else name
                    if val_node and val_node.type == "arrow_function":
                        sig = _ts_arrow_sig(val_node, source, name)
                        defs.append(Definition(
                            relpath, child.start_point[0] + 1, "arrow_function", qualname, sig,
                        ))
                    else:
                        defs.append(Definition(
                            relpath, child.start_point[0] + 1, "constant", qualname, name,
                        ))
        return

    if node_type == "statement_block":
        # Recurse into block bodies (function/method bodies, etc.)
        for child in node.children:
            _walk_ts_defs(child, source, relpath, defs, class_stack)
        return

    # Top-level: recurse for export_statement and top-level declarations.
    if node_type == "program":
        for child in node.children:
            _walk_ts_defs(child, source, relpath, defs, class_stack)
        return


def _ts_func_sig(node, source: bytes, name: str) -> str:
    params_node = node.child_by_field_name("parameters")
    ret_node = node.child_by_field_name("return_type")
    params = _ts_node_text(params_node, source) if params_node else "()"
    ret = _ts_node_text(ret_node, source) if ret_node else ""
    async_prefix = "async " if any(c.type == "async" for c in node.children) else ""
    return f"{async_prefix}function {name}{params}{ret}"


def _ts_method_sig(node, source: bytes, name: str) -> str:
    params_node = node.child_by_field_name("parameters")
    ret_node = node.child_by_field_name("return_type")
    params = _ts_node_text(params_node, source) if params_node else "()"
    ret = _ts_node_text(ret_node, source) if ret_node else ""
    async_prefix = "async " if any(c.type == "async" for c in node.children) else ""
    return f"{async_prefix}{name}{params}{ret}"


def _ts_arrow_sig(node, source: bytes, name: str) -> str:
    params_node = node.child_by_field_name("parameters") or node.child_by_field_name("identifier")
    ret_node = node.child_by_field_name("return_type")
    params = _ts_node_text(params_node, source) if params_node else "()"
    ret = _ts_node_text(ret_node, source) if ret_node else ""
    async_prefix = "async " if any(c.type == "async" for c in node.children) else ""
    return f"const {name} = {async_prefix}({params}){ret} => ..."


def _ts_collect_refs(path: Path, relpath: str, name: str) -> list[Reference]:
    """Walk a TS/TSX AST and collect every reference to `name`."""
    result = _parse_ts(path)
    if result is None:
        return []
    tree, source = result
    refs: list[Reference] = []
    _walk_ts_refs(tree.root_node, source, relpath, name, refs)
    return refs


def _walk_ts_refs(node, source: bytes, relpath: str, name: str, refs: list[Reference]) -> None:
    """Recursive walker for TS reference extraction."""
    nt = node.type

    if nt == "call_expression":
        fn = node.child_by_field_name("function")
        if fn:
            if fn.type == "identifier" and _ts_node_text(fn, source) == name:
                refs.append(Reference(relpath, node.start_point[0] + 1, "call", f"{name}(...)"))
            elif fn.type == "member_expression":
                prop = fn.child_by_field_name("property")
                if prop and _ts_node_text(prop, source) == name:
                    obj_text = _ts_node_text(fn.child_by_field_name("object") or fn, source)
                    refs.append(Reference(relpath, node.start_point[0] + 1, "call", f"{obj_text}.{name}(...)"))

    elif nt == "member_expression":
        prop = node.child_by_field_name("property")
        if prop and _ts_node_text(prop, source) == name:
            # Don't double-report if parent is a call (already covered above).
            if node.parent is None or node.parent.type != "call_expression":
                refs.append(Reference(relpath, node.start_point[0] + 1, "member", f".{name}"))

    elif nt == "identifier":
        if _ts_node_text(node, source) == name:
            # Skip: property names in member_expression (not a reference to the symbol)
            # Skip: the definition itself (handled by def collector)
            parent_nt = node.parent.type if node.parent else ""
            if parent_nt not in (
                "function_declaration", "method_definition", "class_declaration",
                "interface_declaration", "variable_declarator", "pair",
                "shorthand_property_identifier_pattern",
            ):
                # Also skip if this identifier is the property side of a member_expression
                if not (parent_nt == "member_expression" and node.parent.child_by_field_name("property") == node):
                    refs.append(Reference(relpath, node.start_point[0] + 1, "name", name))

    for child in node.children:
        _walk_ts_refs(child, source, relpath, name, refs)


# ---------------------------------------------------------------------------
# Cross-language index helpers
# ---------------------------------------------------------------------------

def _all_definitions() -> list[Definition]:
    defs: list[Definition] = []

    # Python
    for path in _python_files():
        tree = _parse_py(path)
        if tree is None:
            continue
        collector = _PyDefCollector(_module_name(path), _rel(path))
        collector.visit(tree)
        defs.extend(collector.defs)

    # TypeScript/TSX/JS/JSX
    if _TS_PARSERS is not None:
        for path in _ts_files():
            defs.extend(_ts_collect_defs(path, _rel(path)))

    return defs


def _all_references(name: str) -> list[Reference]:
    """All references to `name` across both language families, deduplicated per line."""
    priority = {"call": 0, "attribute": 1, "member": 1, "name": 2}
    found: dict[tuple[str, int], Reference] = {}

    def _merge(ref: Reference) -> None:
        key = (ref.path, ref.line)
        existing = found.get(key)
        if existing is None or priority.get(ref.kind, 9) < priority.get(existing.kind, 9):
            found[key] = ref

    # Python
    for path in _python_files():
        tree = _parse_py(path)
        if tree is None:
            continue
        collector = _PyRefCollector(_rel(path), name)
        collector.visit(tree)
        for ref in collector.refs:
            _merge(ref)

    # TypeScript/TSX
    if _TS_PARSERS is not None:
        for path in _ts_files():
            for ref in _ts_collect_refs(path, _rel(path), name):
                _merge(ref)

    return sorted(found.values(), key=lambda r: (r.path, r.line))


def _resolve_module(query: str) -> tuple[Path, str] | None:
    """Return (path, lang) for a module query, checking both Python and TS."""
    norm = query.strip().replace("\\", "/")

    # Python: remove .py suffix if present, try dotted or path match
    py_norm = norm.removesuffix(".py")
    py_dotted = py_norm.replace("/", ".")
    for path in _python_files():
        module = _module_name(path)
        rel = _rel(path).removesuffix(".py")
        if module == py_dotted or rel == py_norm:
            return path, "python"
        if module.endswith("." + py_dotted) or rel.endswith("/" + py_norm):
            return path, "python"

    # TypeScript: match by path or bare name
    for path in _ts_files():
        rel = _rel(path)
        bare = rel  # e.g. "app/frontend/src/components/ChatArea.tsx"
        # Strip any TS extension for comparison
        for ext in (".ts", ".tsx", ".js", ".jsx"):
            bare_stripped = rel.removesuffix(ext)
            query_stripped = norm.removesuffix(ext)
            if bare_stripped == query_stripped or bare == norm:
                return path, "typescript"
            # Also match on file stem alone
            stem = Path(rel).stem
            if stem == query_stripped or stem == norm:
                return path, "typescript"

    return None


# ---------------------------------------------------------------------------
# MCP tools
# ---------------------------------------------------------------------------

@mcp.tool()
def where_is(name: str) -> str:
    """Find every definition of `name` across the project's Python AND TypeScript/TSX source.

    Covers: Python functions/methods/classes/constants (via ast) and TypeScript
    function declarations, arrow functions, classes, methods, interfaces, and
    exported constants (via tree-sitter).

    Unlike a text search, this matches only real definition nodes: no hits from
    comments, docstrings, string literals, or import statements.
    """
    hits = [d for d in _all_definitions() if d.qualname.rsplit(".", 1)[-1] == name]
    if not hits:
        return (
            f"no definition of {name!r} found in the project's Python or TypeScript source.\n"
            f"Tip: use find_references() if you expect the name to be imported, or check the "
            f"exact casing (TypeScript is case-sensitive)."
        )
    lines = [f"{len(hits)} definition(s) of {name!r}:"]
    for d in sorted(hits, key=lambda d: (d.path, d.line)):
        lines.append(f"  {d.path}:{d.line}  [{d.kind}] {d.qualname}")
        if d.kind in ("function", "method", "arrow_function"):
            lines.append(f"      {d.signature}")
    return "\n".join(lines)


@mcp.tool()
def find_references(name: str) -> str:
    """Find every place `name` is used across the project's Python AND TypeScript/TSX source.

    Python: function calls, attribute access, name loads (via ast).
    TypeScript: call expressions, member access, identifier references (via tree-sitter).

    Returns only genuine structural references — not every textual mention.
    """
    refs = _all_references(name)
    if not refs:
        return f"no references to {name!r} found in the project's Python or TypeScript source"
    lines = [f"{len(refs)} reference(s) to {name!r}:"]
    for r in refs:
        lines.append(f"  {r.path}:{r.line}  [{r.kind}] {r.text}")
    return "\n".join(lines)


@mcp.tool()
def outline(module: str) -> str:
    """Show the structured API of one module — classes, methods, functions, and
    constants with signatures, in source order.

    Accepts a path (`app/backend/rag/retriever_hybrid.py`,
    `app/frontend/src/components/ChatArea.tsx`) or a bare name (`retriever_hybrid`,
    `ChatArea`). Works for both Python and TypeScript/TSX modules.
    """
    result = _resolve_module(module)
    if result is None:
        return (
            f"no module matching {module!r} in the project source.\n"
            f"Tip: use the relative path from the repo root, or just the file stem "
            f"(e.g. 'retriever_hybrid' or 'ChatArea')."
        )
    path, lang = result

    if lang == "python":
        tree = _parse_py(path)
        if tree is None:
            return f"could not parse {_rel(path)}"
        collector = _PyDefCollector(_module_name(path), _rel(path))
        collector.visit(tree)
        if not collector.defs:
            return f"{_rel(path)} has no top-level definitions"
        lines = [f"outline of {_rel(path)} (Python):"]
        for d in collector.defs:
            indent = "    " if d.kind == "method" else "  "
            lines.append(f"{indent}{d.line}: [{d.kind}] {d.signature}")
        return "\n".join(lines)

    else:  # TypeScript/TSX
        if _TS_PARSERS is None:
            return f"tree-sitter is not available; cannot outline TypeScript module {_rel(path)}"
        defs = _ts_collect_defs(path, _rel(path))
        if not defs:
            return f"{_rel(path)} has no extractable definitions"
        lines = [f"outline of {_rel(path)} (TypeScript):"]
        for d in defs:
            indent = "    " if d.kind == "method" else "  "
            lines.append(f"{indent}{d.line}: [{d.kind}] {d.signature}")
        return "\n".join(lines)


if __name__ == "__main__":
    mcp.run()
