#!/usr/bin/env python3
"""Validate the done-done skill package.

A skill that tells agents to "verify before claiming done" should not ship
unverified. This runs the same checks locally and in CI:

  1. skills/done-done/SKILL.md exists at the Agent-Skills-standard path.
  2. It starts with YAML frontmatter.
  3. Frontmatter declares a non-empty `name` and `description`.
  4. `name` matches the skill directory name.
  5. Referenced local files (references/*.md) actually exist.
  6. The per-harness plugin manifests (.claude-plugin, .codex-plugin,
     .cursor-plugin) parse as JSON and are internally consistent.

Run:  python tests/validate.py
Exit 0 = valid, non-zero = invalid.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any, cast

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = REPO_ROOT / "skills" / "done-done"
SKILL_MD = SKILL_DIR / "SKILL.md"


def parse_frontmatter(text: str) -> dict[str, str] | None:
    """Return the frontmatter as a dict, or None if it is missing/malformed."""
    if not text.startswith("---"):
        return None
    # Frontmatter is the block between the first and second '---' lines.
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    fm: dict[str, str] = {}
    key: str | None = None
    for line in parts[1].splitlines():
        if not line.strip():
            continue
        # Continuation of a folded/multiline value ('>-', '|-', indented lines).
        if line[0].isspace() and key is not None:
            fm[key] = (fm[key] + " " + line.strip()).strip()
            continue
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if m is None:
            continue
        # k is a fresh str, so fm[k] is unambiguously typed.
        k: str = m.group(1)
        val: str = m.group(2).strip()
        # Strip YAML folded/literal block indicators like '>-' or '|'.
        val = re.sub(r"[|>][+-]?$", "", val).strip()
        key = k
        fm[k] = val
    return fm


def main() -> int:
    errors: list[str] = []

    # 1. Standard path
    if not SKILL_MD.is_file():
        errors.append(
            f"missing skill file at standard path: "
            f"{SKILL_MD.relative_to(REPO_ROOT)}"
        )
        print(_report(errors))
        return 1

    text = SKILL_MD.read_text(encoding="utf-8")

    # 2 & 3. Frontmatter with name + description
    fm = parse_frontmatter(text)
    if fm is None:
        errors.append("SKILL.md is missing YAML frontmatter (--- ... ---)")
    else:
        name = fm.get("name", "").strip()
        desc = fm.get("description", "").strip()
        if not name:
            errors.append("frontmatter missing required field: name")
        if not desc:
            errors.append("frontmatter missing required field: description")
        # 4. name matches directory
        if name and name != SKILL_DIR.name:
            errors.append(
                f"frontmatter name '{name}' does not match "
                f"skill directory '{SKILL_DIR.name}'"
            )

    # 5. Referenced local files exist
    for ref in re.findall(r"\]\((references/[^)]+)\)", text):
        if not (SKILL_DIR / ref).is_file():
            errors.append(f"SKILL.md references missing file: {ref}")

    # 6. Per-harness plugin manifests parse and are self-consistent
    errors.extend(_validate_manifests())

    print(_report(errors))
    return 1 if errors else 0


def _validate_manifests() -> list[str]:
    """Parse the plugin manifests and check they point at the real skill dir.

    These are what make `/plugin install` and the Codex/Cursor plugin paths
    work. A malformed manifest breaks the advertised install command, so CI
    checks it rather than trusting it.
    """
    errs: list[str] = []

    # Claude Code: .claude-plugin/plugin.json + marketplace.json (source "./")
    claude = _load_json(REPO_ROOT / ".claude-plugin" / "plugin.json", errs)
    if claude is not None:
        _check_name(claude, "done-done", ".claude-plugin/plugin.json", errs)
    marketplace = _load_json(
        REPO_ROOT / ".claude-plugin" / "marketplace.json", errs
    )
    if marketplace is not None:
        # The README advertises `/plugin install done-done@done-done`; the
        # suffix after @ is this marketplace name, so it must match too.
        _check_name(marketplace, "done-done", ".claude-plugin/marketplace.json", errs)
        plugins: Any = marketplace.get("plugins")
        if not isinstance(plugins, list) or not plugins:
            errs.append(
                ".claude-plugin/marketplace.json: 'plugins' must be a "
                "non-empty list"
            )
        else:
            # Cast before indexing so the element is Any, not list[Unknown].
            items = cast("list[Any]", plugins)
            entry: Any = items[0]
            source: Any = None
            if isinstance(entry, dict):
                source = cast("dict[str, Any]", entry).get("source")
            if source != "./":
                errs.append(
                    ".claude-plugin/marketplace.json: plugins[0].source "
                    'must be "./" (repo is its own marketplace)'
                )

    # Codex and Cursor: .<harness>-plugin/plugin.json with "skills": "./skills/"
    for harness in ("codex", "cursor"):
        manifest_path = f".{harness}-plugin/plugin.json"
        data = _load_json(REPO_ROOT / f".{harness}-plugin" / "plugin.json", errs)
        if data is not None:
            _check_name(data, "done-done", manifest_path, errs)
            if data.get("skills") != "./skills/":
                errs.append(f'{manifest_path}: "skills" must be "./skills/"')

    return errs


def _load_json(path: Path, errs: list[str]) -> dict[str, Any] | None:
    """Load a JSON object; append to errs and return None on any problem."""
    rel = path.relative_to(REPO_ROOT)
    if not path.is_file():
        errs.append(f"missing manifest: {rel}")
        return None
    try:
        data: Any = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errs.append(f"{rel}: invalid JSON ({exc.msg})")
        return None
    if not isinstance(data, dict):
        errs.append(f"{rel}: top level must be a JSON object")
        return None
    return cast(dict[str, Any], data)


def _check_name(
    data: dict[str, Any], expected: str, rel: str, errs: list[str]
) -> None:
    """Assert the manifest's name field matches the plugin name."""
    if data.get("name") != expected:
        errs.append(f'{rel}: "name" must be "{expected}"')


def _report(errors: list[str]) -> str:
    if errors:
        lines = ["SKILL validation FAILED:"]
        lines += [f"  - {e}" for e in errors]
        return "\n".join(lines)
    return (
        "SKILL validation passed: "
        f"{SKILL_MD.relative_to(REPO_ROOT)} has valid frontmatter "
        "and all referenced files exist."
    )


if __name__ == "__main__":
    sys.exit(main())
