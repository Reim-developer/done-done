#!/usr/bin/env python3
"""Contract test for the done-done skill.

The product here is prose. So the honest, deterministic test is a CONTRACT
test: assert the SKILL.md still keeps every structural promise the repo makes
about it. This is not a markdown-formatting check -- it guards the actual
behavior the skill claims to enforce.

If a future edit removes the BLOCKED report, drops the banned phrases, breaks
the step ordering, or gashes the reference link, CI goes red. Those are real
regressions in the product.

This mirrors how prose/prompt skills get regression-tested deterministically.
The deeper behavioral eval (does an agent WITH the skill actually run checks vs
WITHOUT it) needs a live model and runs locally before release, not in CI --
see evals/README.md.

Run:  python tests/test_contract.py
Exit 0 = contract intact, non-zero = a promise was broken.
"""
from __future__ import annotations

import sys
from collections.abc import Callable
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent / "skills" / "done-done"
SKILL_MD = SKILL_DIR / "SKILL.md"

# Each rule: (name, predicate(skill_text) -> bool). A failing predicate means
# the skill no longer keeps that promise.
Rule = tuple[str, Callable[[str], bool]]


def _steps_in_order(text: str) -> bool:
    """The four protocol step HEADINGS must appear, and in order 1 -> 2 -> 3 -> 4.

    Match the '### Step N' headings specifically. Body text legitimately
    cross-references later steps ("see Step 4"), so a bare substring search
    would false-positive on prose.
    """
    markers = ["### Step 1", "### Step 2", "### Step 3", "### Step 4"]
    pos = [text.find(m) for m in markers]
    if any(p < 0 for p in pos):
        return False
    return pos == sorted(pos)


def _two_report_blocks(text: str) -> bool:
    """The two-report contract: both DONE and BLOCKED templates exist."""
    return "## DONE" in text and "## BLOCKED" in text


def _banned_phrases(text: str) -> bool:
    """The skill must still document the 'fake done' phrases it forbids."""
    banned = ["should work", "install X", "works on my machine"]
    return all(p in text for p in banned)


def _bounded_loop(text: str) -> bool:
    """Fix loop must be bounded (no infinite thrash) -- '3 attempts'."""
    return "3 attempts" in text or "3 failed attempts" in text


def _reference_link(text: str) -> bool:
    """The per-language table must be linked AND the file must exist."""
    if "references/verification.md" not in text:
        return False
    return (SKILL_DIR / "references" / "verification.md").is_file()


def _no_verification_path(text: str) -> bool:
    """Skill must handle the 'nothing to run' case explicitly."""
    return "no verification exists" in text.lower()


RULES: list[Rule] = [
    ("skill is at the Agent-Skills-standard path", lambda t: SKILL_MD.is_file()),
    ("frontmatter description has trigger conditions ('Use when')",
     lambda t: "Use when" in _frontmatter_description(t)),
    ("four protocol steps present, in order", _steps_in_order),
    ("two-report contract (DONE + BLOCKED) intact", _two_report_blocks),
    ("banned 'fake done' phrases still documented", _banned_phrases),
    ("fix loop is bounded (3 attempts)", _bounded_loop),
    ("'no verification exists' path present", _no_verification_path),
    ("per-language reference linked and file exists", _reference_link),
]


def _frontmatter_description(text: str) -> str:
    """Pull the frontmatter `description` value out of the SKILL.md."""
    if not text.startswith("---"):
        return ""
    parts = text.split("---", 2)
    if len(parts) < 3:
        return ""
    lines = parts[1].splitlines()
    out: list[str] = []
    grab = False
    for line in lines:
        if line.startswith("description:"):
            grab = True
            out.append(line.split(":", 1)[1])
            continue
        if grab:
            if line[:1] in (" ", "\t") or not line.strip():
                out.append(line)
            else:
                break
    return " ".join(out)


def main() -> int:
    text = SKILL_MD.read_text(encoding="utf-8") if SKILL_MD.is_file() else ""
    failures = [name for name, pred in RULES if not pred(text)]

    if failures:
        print("Contract test FAILED -- the skill broke a promise:\n")
        for name in failures:
            print(f"  - {name}")
        print(
            "\nThe skill no longer enforces what the README claims. "
            "Restore the promise or update the README + this test together."
        )
        return 1

    print(f"Contract test passed: all {len(RULES)} promises intact.")
    for name, _ in RULES:
        print(f"  ok  {name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
