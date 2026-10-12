# Verification detection by language

The agent should prefer whatever the repo itself declares. This table is the
fallback map: given a manifest, what is the real test / lint / typecheck /
build command. Always confirm against the repo's scripts before running.

Rule of thumb: **CI is the source of truth.** If `.github/workflows/` runs a
command, mirror that command.

---

## JavaScript / TypeScript

Detected by `package.json` (+ lockfile: `package-lock.json`, `pnpm-lock.yaml`,
`yarn.lock`, `bun.lockb`).

Pick the package manager from the lockfile, then read `package.json` →
`scripts`. Only run scripts that exist.

| Check        | Look for in `scripts`                | Fallback |
|--------------|---------------------------------------|----------|
| Test         | `test`, `test:ci`, `check`            | `npm test` only if a real runner exists |
| Lint         | `lint`, `lint:ci`, `eslint`           | — |
| Typecheck    | `typecheck`, `type-check`, `tsc`      | `npx tsc --noEmit` for TS projects |
| Build        | `build`                               | — |

```bash
# choose ONE pm; only run scripts that exist in package.json
npm run test --if-present
npm run lint --if-present
npm run typecheck --if-present
npm run build --if-present
# pnpm / yarn / bun:  pnpm run <script> | yarn <script> | bun run <script>
```

Note: `--if-present` prevents a hard failure when a script is absent, but
**absence is not proof of green** — report which checks were skipped.

## Python

Detected by `pyproject.toml`, `setup.py`, `setup.cfg`, `requirements*.txt`,
or a `tox.ini` / `Makefile`.

| Check        | Look for                              | Command |
|--------------|---------------------------------------|---------|
| Test         | `pytest` in deps / `tests/` dir       | `python -m pytest -q` |
| Lint         | `ruff`, `flake8`, `pylint` in deps    | `ruff check .` / `python -m flake8 .` |
| Format check | `black`, `ruff`                       | `black --check .` / `ruff format --check .` |
| Typecheck    | `mypy`, `pyright` in deps             | `python -m mypy .` |
| Build        | packaging present                     | `python -m build` |

Prefer the tool already pinned in the project. If the project uses `uv`:
`uv run pytest`, `uv run ruff check .`.

## Rust

Detected by `Cargo.toml`.

| Check        | Command |
|--------------|---------|
| Test         | `cargo test` |
| Lint         | `cargo clippy --all-targets -- -D warnings` |
| Format check | `cargo fmt --check` |
| Build        | `cargo build` |

`cargo test` runs unit + integration tests and compiles the crate, so it is a
strong default. For docs-heavy crates add `cargo doc --no-deps`.

## Go

Detected by `go.mod`.

| Check        | Command |
|--------------|---------|
| Test         | `go test ./...` |
| Lint         | `golangci-lint run` (if configured) |
| Vet          | `go vet ./...` |
| Build        | `go build ./...` |

## Ruby

Detected by `Gemfile`, `.ruby-version`.

| Check   | Command              |
|---------|----------------------|
| Test    | `bundle exec rake` / `bundle exec rspec` |
| Lint    | `bundle exec rubocop` |

## Java / Kotlin (Gradle / Maven)

Detected by `build.gradle*`, `pom.xml`.

| Check   | Gradle              | Maven          |
|---------|---------------------|----------------|
| Test    | `./gradlew test`    | `mvn test`     |
| Build   | `./gradlew build`   | `mvn package`  |
| Lint    | `./gradlew ktlintCheck` / `checkstyle` | — |

## .NET

Detected by `*.csproj`, `*.sln`.

| Check   | Command        |
|---------|----------------|
| Test    | `dotnet test`  |
| Build   | `dotnet build` |

---

## Cross-cutting checks worth mirroring from CI

If the repo has any of these wired up, run them — they catch the "done" lies
that tests miss:

- **Formatting** — a green test with a failing `fmt --check` / `--check`
  formatter still fails CI.
- **Lint with `-D warnings` / `--max-warnings 0`** — warnings that "don't
  break the build" usually break CI.
- **Typecheck on TS** — `tsc --noEmit` is the number-one source of "done but
  broken" in JS/TS repos.

## When there is genuinely no verification

If none of the above exists, do NOT invent green. Report:

> No test, lint, typecheck, or build is declared in this project. I could not
> verify. Here is what I changed and how to check it manually.

Then offer to add a minimal check (e.g. one `pytest` test, one `npm test`
script) so the project can be verified next time.
