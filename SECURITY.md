# Security Policy

## About this project

`done-done` is a prose-only Agent Skill. It ships **no runtime code, no
dependencies, no network calls, and no binary**. The skill instructs a coding
agent to run the verification the *target project* declares — it does not
execute anything itself until an agent acts on it inside your own environment.

## Supported versions

Only the latest version on `main` receives updates.

## Reporting a vulnerability

Please report security issues via
[GitHub Security Advisories](https://github.com/Reim-developer/done-done/security/advisories/new)
rather than a public issue.

The most relevant reports for this project are:

- **Prompt-injection or misuse vectors.** If the skill's wording could be
  abused to make an agent *less* safe (e.g. encouraging it to run unvetted
  commands under the banner of "verification"), that is a real issue.
- **Supply-chain concerns.** This repo has zero dependencies. If a future
  change introduces one, flag it.

## What is out of scope

- The behavior of any coding agent that loads this skill.
- The security of the commands run by *your* project's own test/lint/build
  pipeline — those are yours, not this repo's.

You will receive an acknowledgment when the report is received and an update
when it is triaged.
