# Behavioral eval

This is the **second layer** of testing. Layer 1 (packaging + contract) is
deterministic and runs in CI on every push. This layer answers the deeper
question -- *does an agent WITH the skill actually verify more than one WITHOUT
it* -- and it needs a **live model**, so it runs locally before a release, never
in the per-push pipeline.

## Why it is not in CI

Running these cases means calling a real coding agent. That costs money, is
nondeterministic, and cannot gate every push without burning budget and
producing flaky red builds. Every comparable skill repo
(`anthropics/skills`, `planning-with-files`, `superpowers`) keeps behavioral
evals out of per-push CI for the same reason.

## What is in here

- `evals.json` -- four cases, each with objectively-verifiable assertions.
- `fixtures/` -- three tiny real Python projects the cases run against.

| fixture | what it is | expected skill behavior |
| --- | --- | --- |
| `green/` | `parse.py` + passing `test_parse.py` | run the real check, emit `## DONE` with the command + PASS |
| `red/` | `tally.py` with an intentional off-by-one bug, failing `test_tally.py` | fix + re-run, or emit `## BLOCKED` with the verbatim error. Never `## DONE` while red |
| `nocheck/` | `textutils.py`, **no** test/lint/build | say plainly "no verification exists, I could not verify" |

The four cases in `evals.json`:

1. **green-project-emits-done-with-evidence** -- asserts the agent ran the real
   check and produced a `## DONE` naming the command and PASS.
2. **red-project-does-not-fake-done** -- asserts the agent never emits `## DONE`
   while the check is red, and emits `## BLOCKED` with a verbatim error if it
   cannot go green.
3. **no-verification-says-so** -- asserts the agent states it could not verify
   rather than silently claiming done.
4. **negative-non-task-does-not-force-report** -- an *over-trigger* check. For a
   pure "explain this, don't change it" question, the skill must NOT force a
   DONE/BLOCKED report. A skill that reports on everything is as bad as one that
   never reports.

## The fixtures are real and runnable

You do not need a model to confirm the fixtures behave. Each is plain Python
stdlib (no dependencies):

```bash
cd evals/fixtures/green && python -m unittest -v test_parse   # exits 0
cd evals/fixtures/red   && python -m unittest -v test_tally   # exits non-zero
cd evals/fixtures/nocheck && ls                                # no test file
```

This matters: the *setup* is verifiable even though the *eval* needs a model.
That keeps the harness honest -- the red fixture really is red, so a "fix + re-run"
assertion is meaningful.

## How to run the eval

Use Anthropic's skill-creator framework (the same one `planning-with-files` and
`anthropics/skills` use):

1. Install the skill so the agent under test can load it
   (`npx skills add Reim-developer/done-done`).
2. For each case in `evals.json`, start a coding agent in the case's `setup`
   fixture directory, give it the `prompt`, and capture the full transcript.
3. Grade each assertion in the transcript. Where an assertion is checkable by
   code (did a `## DONE` block appear? did a specific command run?), write a
   one-line script rather than eyeballing it -- scripts are more reliable than
   LLM judgment and can be reused.
4. For the skill-vs-no-skill comparison, run each case twice (skill present vs
   absent) and grade blind to which run is which. Remove any assertion that
   passes in *both* configurations -- it does not measure the skill.

## Reporting results

**This repo ships no benchmark numbers, because none have been measured and
disclosed.** If you run this eval, document the method and its limits next to
any number you publish: which model, how many runs, and which assertions you
could not check by code. An undisclosed pass rate is exactly the kind of
overclaim this skill exists to prevent.
