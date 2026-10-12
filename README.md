# done-done

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-compatible-brightgreen.svg)](https://github.com/anthropics/skills)
[![Claude Code](https://img.shields.io/badge/works%20with-Claude%20Code-orange.svg)](#install)
[![Codex · Cursor · OpenCode](https://img.shields.io/badge/also-Codex%20%C2%B7%20Cursor%20%C2%B7%20OpenCode-lightgrey.svg)](#install)

> The agent says "done." Is it *done* done?

A single-file **Agent Skill** that puts a hard gate between "I wrote code" and
"I say done." It stops coding agents from declaring work complete before they
have actually run the test, the build, or the type checker — and it makes them
leave an honest handoff instead of going silent when something breaks.

Works with **Claude Code, Codex, Cursor, OpenCode, Gemini CLI**, and any agent
that reads the Agent Skills standard (`SKILL.md`).

---

## The problem

Coding agents fail in one specific, expensive way: they say a task is finished
without ever executing the verification. You have seen all of these:

- "Done! You may just need to `pip install X`." *(never ran it)*
- "The tests pass." *(there were no tests, or they were red and ignored)*
- "Fixed. Should work now." *(should ≠ does)*
- It hits one error, goes quiet, and leaves a half-fixed repo for you to clean
  up at 11pm.

The cost is not the failed test. The cost is **your hour** spent discovering
the "done" work never ran.

## What it does

`done-done` enforces a four-step protocol before the word *done* is allowed:

1. **Detect** the project's real verification — from `package.json` scripts,
   `pyproject.toml`, `Cargo.toml`, `go.mod`, a `Makefile`, or by mirroring CI.
   Never invents an easier command.
2. **Run it** — actually executes. No predicting, no "should pass."
3. **Show the evidence** — pastes the exact command and its real output. A set
   of banned phrases ("should work", "you may need to install X") no longer
   count as done.
4. **Close the loop** — on red, it fixes and re-runs (bounded, 3 attempts per
   error class). If it can't go green, it emits an honest **BLOCKED** report
   with the verbatim error and a recommended next step. It never abandons a
   task silently.

The result is one of two greppable blocks, so you always know where you stand:

```
## DONE
Changed:
  - auth/login.ts — validated email before submit
Verification:
  - npm run test:ci  → PASS (42 passed)
  - npm run typecheck → PASS
```

```
## BLOCKED
Changed so far:
  - schema updated, migration written
What fails:
  - npm run typecheck → FAIL
Error (verbatim):
  TS2345: Argument of type 'string' is not assignable to parameter of type 'UserId'
Why I stopped:
  - 3 fix attempts on the same TypeError; root cause not identifiable here
Next step I recommend:
  - widen the UserId type or cast at the call site
```

A **BLOCKED** report is a success, not a failure. An honest "I could not
verify this, here is exactly why" beats a fake "done" every time.

## Install

### Claude Code

```bash
# from a clone of this repo
mkdir -p ~/.claude/skills/done-done
cp -r SKILL.md references ~/.claude/skills/done-done/
```

Or add it to a project for one repo only:

```bash
mkdir -p .claude/skills/done-done
cp -r SKILL.md references .claude/skills/done-done/
```

### Any agent via the skills CLI

```bash
npx skills add <your-github-username>/done-done
```

### Manual (any Agent-Skills-compatible agent)

Copy `SKILL.md` (and optionally `references/`, `scripts/`) into your agent's
skills directory. Point the agent at it, or let it auto-load on task
completion. Codex / OpenCode / Gemini CLI / Cursor all read a `SKILL.md` from
their configured skills path.

## Why this works

- **It is one file of Markdown.** No model, no API, no infrastructure. Load it
  and the behavior changes on the next task.
- **It is instantly felt.** The first time the agent refuses to say "done"
  without a green run, you see the difference.
- **It is cross-platform.** The protocol is shell-agnostic; the helper ships
  for both bash and PowerShell.
- **It does not try to write better code.** It fixes the one thing that wastes
  your time: *lying about whether the code works.* Pair it with your normal
  quality skills; this is the gate at the end.

## Who it is for

Anyone running a coding agent in anger — Claude Code, Cursor, Codex, OpenCode,
Gemini CLI — who is tired of spending the next hour cleaning up "done" work
that never ran.

## License

MIT. See [LICENSE](LICENSE).
