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

## See it in action

*The transcript below is an illustrative example of the behavior the skill
asks for, not a captured benchmark run. See "What this is not" for what has and
has not been measured.*

Same task in the same repo — fix the failing auth test and finish. One run with
the skill, one without.

**Without the skill:**

> Done! I fixed the null check in `login.ts`. The tests should pass now — you
> may need to run `npm install` first since a dependency was missing.

It never ran anything. The test was still red, and there was no missing
dependency. You find out an hour later.

**With `done-done`:**

> Ran `npm test -- login`:
>
> ```
> FAIL  src/auth/login.test.ts
>   ● validates session token
>     TypeError: Cannot read properties of undefined (reading 'expires')
> ```
>
> Read the error: the token object is `undefined`, not the expiry field. Applied
> the smallest fix (optional chaining at the call site). Re-ran:
>
> ```
> PASS  src/auth/login.test.ts
> Tests: 1 passed, 1 total
> ```
>
> ## DONE
> Changed:
>   - src/auth/login.ts — guarded undefined session token before reading expiry
> Verification:
>   - npm test -- login → PASS (1 passed)

The difference is not code quality. It is that the second run **ran the real
check, hit real red, fixed it, and re-ran to green** — and the first run
declared victory over code it never executed.

## Install

`done-done` follows the Agent Skills standard, so the skill lives at
`skills/done-done/SKILL.md` and installs with the standard tooling.

### Any agent (recommended)

```bash
npx skills add Reim-developer/done-done
```

This detects your installed agents (Claude Code, Codex, Cursor, OpenCode,
Gemini CLI, and 30+ more) and links the skill into each one. Add `-g` to make
it global instead of project-scoped.

List what a repo contains without installing:

```bash
npx skills add Reim-developer/done-done --list
```

### Claude Code (plugin marketplace)

If you prefer the plugin route, add this repo as a plugin:

```
/plugin marketplace add Reim-developer/done-done
/plugin install done-done@done-done
```

Or manually copy the skill directory:

```bash
# global
cp -r skills/done-done ~/.claude/skills/
# or project-local
cp -r skills/done-done .claude/skills/
```

### Codex (plugin)

Codex ships a native plugin manifest at `.codex-plugin/plugin.json` (the
official format), and reads this repo's `.claude-plugin/marketplace.json` as a
legacy-compatible marketplace. Install with the Codex CLI:

```bash
codex plugin marketplace add Reim-developer/done-done
codex plugin add done-done@done-done
```

Or skip the plugin route entirely and copy the skill into the repo-scoped dir
(`.agents/skills/`) or your user dir (`~/.agents/skills/`).

### Cursor (plugin)

Cursor ships a manifest at `.cursor-plugin/plugin.json` (the same format it
shares with other harnesses). The simplest reliable path in Cursor is the
universal installer above (`npx skills add`), or a manual copy into Cursor's
skills directory. I have not verified a Cursor-specific plugin command, so I am
not going to invent one here.

### OpenCode

OpenCode reads the Agent Skills standard directly from `skills/` — no plugin
manifest needed. Use `npx skills add` or copy the folder into
`~/.config/opencode/skills/`.

### Manual (any Agent-Skills-compatible agent)

Copy the `skills/done-done/` folder — `SKILL.md` plus its `references/` — into
your agent's skills directory (`~/.claude/skills/`, `~/.codex/skills/`,
`~/.cursor/skills/`, `~/.config/opencode/skills/`, etc.). Point the agent at
it, or let it auto-load on task completion.

## Why this works

- **It is one file of Markdown.** No model, no API, no infrastructure. Load it
  and the behavior changes on the next task.
- **It is instantly felt.** The first time the agent refuses to say "done"
  without a green run, you see the difference.
- **It is cross-platform and language-agnostic.** The protocol is pure
  prose — it tells the agent to run whatever the *project* declares, so it
  works for JS, Python, Rust, Go, and anything else without shipping
  language-specific glue.
- **It does not try to write better code.** It fixes the one thing that wastes
  your time: *lying about whether the code works.* Pair it with your normal
  quality skills; this is the gate at the end.

## What this is not

Being upfront, because this is a skill and skills are easy to oversell:

- **It is not a benchmarked, evaluated skill.** I have not run a blind A/B
  study and I am not going to invent one. If you want proof-of-effect numbers,
  this repo does not have them yet, and you should weight it accordingly.
- **It does not make the model smarter.** It is prose that changes *behavior*,
  not capability. A weak model can still write code that fails; the skill just
  makes it say so instead of claiming victory.
- **It cannot force anything.** Skills are context, not a sandbox. A model
  under strong pressure (or a user who keeps saying "just ship it") can ignore
  it. Think of it as a strong default, not a guarantee.
- **It will not fix a project with no verification to run.** If there is no
  test, lint, typecheck, or build, the skill makes the agent say "I could not
  verify" — not magically produce correctness.

If any of that is a dealbreaker, that is a fair reason to pass.

## How this repo verifies itself

A skill that preaches "verify before claiming done" should not ship unverified.
Testing a *prose* skill honestly takes two different layers, and this repo keeps
them separate on purpose:

**1. Deterministic checks (run in CI on every push).** The product is text, so
the test asserts the text keeps its promises. Two scripts in `tests/`:

```bash
python tests/validate.py       # packaging: standard path, frontmatter, links resolve
python tests/test_contract.py  # contract: 4 steps in order, DONE+BLOCKED, banned phrases, bounded loop
```

`test_contract.py` is a real regression guard, not a format linter. Delete the
BLOCKED report, drop a banned phrase, break the step order, or gash the
reference link, and CI goes red. It was checked against 6 deliberate mutations
of the skill; it catches the ones that break a promise.

**2. Behavioral eval (runs locally before a release, never in CI).** Whether an
agent *with* the skill actually verifies more than one *without* it needs a live
model, costs money, and is nondeterministic — so it does not belong in the
per-push pipeline. The eval cases and assertions live in `evals/`, run with
Anthropic's skill-creator framework, and are documented (including how to grade
them) in [`evals/README.md`](evals/README.md). **This repo ships no benchmark
numbers**, because none have been measured and disclosed. See "What this is not".

## Repo structure

```
done-done/
├── skills/
│   └── done-done/
│       ├── SKILL.md                  <- the skill (the product)
│       └── references/
│           └── verification.md       <- per-language "how to detect checks"
├── .claude-plugin/
│   ├── plugin.json                   <- Claude Code plugin manifest
│   └── marketplace.json              <- makes this repo its own marketplace
├── .codex-plugin/
│   └── plugin.json                   <- Codex plugin manifest (official format)
├── .cursor-plugin/
│   └── plugin.json                   <- Cursor plugin manifest
├── .github/
│   └── workflows/
│       └── ci.yml                    <- contract + packaging + typecheck
├── tests/
│   ├── validate.py                   <- packaging + manifest validation
│   └── test_contract.py              <- regression guard on the skill's promises
├── evals/
│   ├── evals.json                    <- behavioral eval cases + assertions
│   ├── fixtures/                     <- green / red / nocheck (runnable)
│   └── README.md                     <- how to run the eval, honestly
├── pyrightconfig.json                <- strict typecheck for the test harness
├── AGENTS.md
├── CHANGELOG.md
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── SECURITY.md
├── CITATION.cff
├── llms.txt
├── LICENSE
└── README.md
```

## Who it is for

Anyone running a coding agent in anger — Claude Code, Cursor, Codex, OpenCode,
Gemini CLI — who is tired of spending the next hour cleaning up "done" work
that never ran.

## License

MIT. See [LICENSE](LICENSE).
