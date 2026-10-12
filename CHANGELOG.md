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
- Claude Code plugin manifest, `AGENTS.md`, contributing and conduct docs.
