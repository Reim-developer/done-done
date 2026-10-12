# Contributing to done-done

Thanks for considering a contribution. This is a small, focused project, so the
bar is "does it stay honest and does it not bloat."

## The core principle

This project exists because agents overclaim. Contributions that overclaim will
be declined. In particular:

- **No invented numbers.** Do not add benchmark results, pass rates, install
  counts, or performance figures that are not measured and reproducible. If you
  run a real eval, document the method and its limits alongside the number.
- **No scope creep into "another coding framework."** done-done is a gate at
  the end of a task, not a methodology. Broaden it carefully or not at all.

## Getting started

```bash
git clone https://github.com/Reim-developer/done-done.git
cd done-done
python tests/validate.py   # should pass on a clean checkout
```

## Making a change

1. Fork and create a branch from `main`.
2. Make your change.
3. Run the checks:

   ```bash
   python tests/validate.py
   ```

4. Update `CHANGELOG.md` under "Unreleased".
5. Open a pull request describing *what* changed and *why*.

## Editing the skill itself

The skill is `skills/done-done/SKILL.md`. Two invariants:

- The frontmatter `name` stays `done-done` (the validator enforces this).
- Every task still ends in `## DONE` or `## BLOCKED`.

If you add reference material, place it in `skills/done-done/references/` and
link it relatively from the skill so the validator confirms it resolves.

## Style

- Plain text. No emoji.
- Direct, second-person instructions to the agent (this is a skill, so it tells
  the model what to do, not the reader).
- Prefer deleting prose to adding it.

## Reporting bugs

Open an issue. The most useful bug report says: which agent (Claude Code,
Codex, Cursor, ...), what the agent claimed, and what it actually ran (or did
not run).

## License

By contributing you agree your contribution is released under the MIT License.
