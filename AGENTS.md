# AGENTS.md

Guidance for AI coding agents working in this repository.

## What this repo is

`done-done` is a single Agent Skill (`skills/done-done/SKILL.md`) that stops
coding agents from declaring work "done" without running the project's real
verification. There is no runtime, no model, and no build step. The product is
prose.

## Ground rules

- **The skill is the product.** It lives at `skills/done-done/SKILL.md`. Do not
  move it; the Agent-Skills-standard path is what makes `npx skills add` work.
- **Keep the tone honest.** This repo's whole pitch is "do not overclaim."
  Never add benchmark numbers, install counts, or performance claims that are
  not measured and disclosed. If you cannot verify it, do not write it.
- **Preserve the two-report contract.** The skill ends every task in exactly
  one of `## DONE` or `## BLOCKED`. Both must stay; the BLOCKED path is the
  point, not an afterthought.
- **No emoji.** The project convention is plain text.

## Verifying a change

Run the same checks CI runs:

```bash
python tests/validate.py
```

It validates the skill is at the standard path, has valid frontmatter
(`name` matching the directory + a `description`), and that any referenced
`references/*.md` files exist. There is no behavioral test suite — see the
"What this is not" section of the README. Do not invent one.

## Editing the skill

When changing `skills/done-done/SKILL.md`:

- Keep the YAML frontmatter `name` equal to `done-done`.
- Keep the `description` accurate; agents read it to decide when to load the
  skill, so it must describe real trigger conditions.
- If you add a reference table, put it under
  `skills/done-done/references/` and link it relatively, then run the
  validator to confirm the link resolves.

## Pull requests

- One logical change per PR.
- Update `CHANGELOG.md` under the "Unreleased" heading.
- Do not touch files under `.github/` unless the change is specifically about CI.
