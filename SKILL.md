---
name: done-done
description: >-
  Use when finishing ANY implementation, bugfix, refactor, or coding task —
  specifically right before declaring the work "done", "complete", "working",
  or "should work". Enforces a hard Definition-of-Done protocol: detect the
  project's real verification commands, actually run them, show the raw
  output, and either reach green or produce an honest BLOCKED report. Prevents
  false "done", silent abandonment, and "you may need to install X" cop-outs.
  Also use when a previous attempt failed and the agent is tempted to stop.
---

# done-done

> The agent says "done." **Is it *done* done?**

## Why this exists

Coding agents fail in one specific, expensive way: they declare a task
complete without ever running the test, the build, or the type checker. Or
they run it, see red, and still write "done — you may need to install X." Or
they bail after the first failure and leave you a half-fixed repo.

You then spend the next hour cleaning up "done" work that never ran.

This skill installs a **hard gate** between "I wrote code" and "I say done."
The word *done* is only allowed to appear after real verification with real
output pasted. If verification can't go green, the correct output is an
honest **BLOCKED** report — never a fake done, never silence.

---

## The protocol

Before writing the word "done", "complete", "works", or "should work", the
agent MUST complete these four steps **in order**. Skipping a step is not
allowed.

### Step 1 — Detect the project's REAL verification

Do not invent commands. Read what the project actually declares and find its
own source of truth. Look, in priority order, for:

- **Task-specific check first.** If the user gave a command ("run `npm test
  -- login`", "check with `cargo clippy`"), THAT is the primary check. Never
  substitute an easier one.
- **The manifest / lockfile** for declared scripts and tooling.
- **CI config** (`.github/workflows/*`) — CI is the project's own definition
  of "passes". Mirror it.
- **`Makefile` / `justfile` / `Taskfile`** — `make test`, `just verify`,
  etc. are the intended entry points.

Use the table in [`references/verification.md`](references/verification.md)
for language-specific detection, but prefer anything the repo itself declares.
If there is genuinely **no** runnable check, say so explicitly (see Step 4,
"no verification exists") — do NOT silently skip to "done".

### Step 2 — Actually run it

Execute the detected commands. Do not predict the result, do not reason about
whether the code "should" pass. **Run it and capture the output.**

Run the full relevant check, not a filtered or weakened version. If the suite
is large, run the subset that covers the changed code — and say that you ran a
subset, with the exact command.

### Step 3 — Show the evidence

Paste the real result, not a summary of your belief. The report must contain
the **exact command(s)** and their **actual exit outcome** (pass/fail + the
salient output lines). Banned phrasings that count as *not done*:

- "should work now" / "should be fixed"
- "this will pass once you install X"
- "the tests pass (trust me)" with no output
- "done, but there may be a type error"
- "works on my machine" with no run shown

If a command failed, that is **not** done. Go to Step 4.

### Step 4 — Close the loop, or report BLOCKED

**If verification is green** → you may say "done", backed by the Step 3
evidence.

**If verification is red** → fix and re-run. Bounded loop:

1. Read the actual error (don't guess the fix).
2. Apply the smallest correct fix.
3. Re-run the check.
4. Repeat, up to **3 attempts** for the same class of error.

**After 3 failed attempts on the same error class**, STOP guessing and emit
the BLOCKED report below. Continuing to thrash wastes tokens and can make the
code worse.

**If no verification exists** → do not claim done. Say plainly: "No test,
lint, typecheck, or build is declared in this project — I could not verify.
Here is exactly what I changed and how to check it manually." Offer to add a
minimal check.

---

## The report

Every task ends with exactly one of two blocks. Use this structure so it is
greppable and honest:

### DONE

```
## DONE
Changed:
  - <file/behaviour changed>
Verification:
  - <exact command>  → PASS (key output: <lines>)
  - <exact command>  → PASS (key output: <lines>)
Notes: <anything the human must still know, e.g. "ran unit subset covering auth/">
```

### BLOCKED

```
## BLOCKED
Changed so far:
  - <what is done and verified, if anything>
What fails:
  - <exact command> → FAIL
Error (verbatim):
  <paste the real error, not a paraphrase>
Why I stopped:
  - <e.g. "3 fix attempts on the same TypeError, root cause not identifiable from here">
Next step I recommend:
  - <the single most useful action for a human>
```

The BLOCKED report is a **success**, not a failure. An honest "I could not
verify this, here's exactly why and where it stands" is infinitely more useful
than a fake "done." Never abandon a task silently; always leave the BLOCKED
handoff.

---

## Anti-patterns this skill forbids

- **The assumption done** — writing code and declaring success without one
  execution of the check.
- **The conditional done** — "done, assuming the env is set up." Verification
  runs in *this* environment; if it can't, that's BLOCKED, not done.
- **The cop-out done** — "done, you may need to install X / set Y." That's a
  setup blocker → say BLOCKED with the exact missing thing, or fix it.
- **The filtered truth** — running the check, seeing red on an "unrelated"
  test, and reporting green anyway. If it's red and you touched related code,
  it counts. If truly unrelated and pre-existing, say so explicitly.
- **The silent quit** — hitting an error and stopping without the BLOCKED
  report.
- **The word salad** — a long "here's what I did" narrative with no command
  and no output. Evidence is a command plus its result, not prose.

---

## Scope

This skill does not make the agent write better code. It makes the agent
**stop lying about whether the code works.** Pair it with your normal
quality skills; this is the gate at the end.

For how to detect the right verification command per language, see
[`references/verification.md`](references/verification.md).
