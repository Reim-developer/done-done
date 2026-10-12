# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Initial release of the `done-done` Agent Skill.
- Four-step Definition-of-Done protocol: detect, run, show evidence, close the
  loop or report BLOCKED.
- Two-report contract (`DONE` / `BLOCKED`) with banned "fake done" phrases.
- Per-language verification-detection reference
  (`skills/done-done/references/verification.md`).
- CI workflow and `tests/validate.py` to validate the skill package.
- `tests/test_contract.py`: deterministic regression guard on the skill's
  structural promises (four steps in order, DONE+BLOCKED reports, banned
  phrases, bounded fix loop, reference link). Verified against deliberate
  mutations of the skill.
- `pyrightconfig.json` (strict) and typechecking of the test harness.
- Plugin manifests: `.claude-plugin/` (plugin + marketplace), `.codex-plugin/`
  (official Codex format), `.cursor-plugin/`. `validate.py` checks they parse
  and are self-consistent.
- `evals/`: behavioral eval cases + runnable fixtures (green / red / nocheck),
  documented with an explicit note that no benchmark numbers are shipped.
- `AGENTS.md`, contributing and conduct docs.
