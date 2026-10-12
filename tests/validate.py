#!/usr/bin/env python3
"""Validate the done-done skill package.

A skill that tells agents to "verify before claiming done" should not ship
unverified. This runs the same checks locally and in CI:

  1. skills/done-done/SKILL.md exists at the Agent-Skills-standard path.
  2. It starts with YAML frontmatter.
  3. Frontmatter declares a non-empty `name` and `description`.
  4. `name` matches the skill directory name.
  5. Referenced local files (references/*.md) actually exist.

Run:  python tests/validate.py
Exit 0 = valid, non-zero = invalid.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

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

    print(_report(errors))
    return 1 if errors else 0


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
