---
name: mise
description: |
  Use whenever an agent needs to run python, uv, java, node, npm, pnpm, yarn,
  ruby, go, cargo, or any other mise-managed tool from the bash tool. Ensures
  commands execute inside the project's mise environment instead of relying on a
  globally installed version.
---

# mise environment runner

This project uses [mise](https://mise.jdx.dev) to manage its runtime tools.
Always route tool invocations through mise so agents pick the versions declared
in `mise.toml`.

## When to apply this skill

Apply before every `bash` command that runs any of the following, unless the
command is already explicitly prefixed with `mise `:

- `python`, `python3`, `pip`, `pip3`, `uv`
- `node`, `npm`, `npx`, `pnpm`, `yarn`, `corepack`
- `java`, `javac`, `mvn`, `gradle`
- `go`, `cargo`, `rustc`, `ruby`, `bundle`, `gem`
- Any task defined in `[tasks]` in `mise.toml`

## How to run a command through mise

Use the `mise x -- <command>` form (short for `mise exec -- <command>`).

Examples:

```bash
mise x -- python --version
mise x -- uv run pytest
mise x -- node -e "console.log(process.version)"
mise x -- npm install
mise x -- java -version
```

For chained commands, wrap the whole chain:

```bash
mise x -- bash -c "python script.py && uv run pytest"
```

For any command that itself shells out to several managed tools, prefer running
it through `mise x --` so the whole subprocess inherits the correct PATH:

```bash
mise x -- ./do-all-the-things.sh
```

## How to run a mise task

If `mise.toml` defines `[tasks]`, run tasks with `mise run`:

```bash
mise run test
mise run lint
```

Do not convert `mise run <task>` into `mise x -- <task>` unless the task truly is
a plain executable.

## What to avoid

- Do not call `python`, `uv`, `node`, etc. directly without the `mise x -- `
  prefix.
- Do not assume the global PATH already contains the correct versions.
- Do not change the working directory with `cd` and then drop the `mise x --`
  prefix; use `mise x -- <command>` from the repo root or pass the target path
  explicitly.
- Do not use `mise activate` or shell hooks; each `bash` invocation is
  independent, so prefix each command instead.

## Diagnostic check

If unsure whether mise sees a tool, run:

```bash
mise list
mise x -- <tool> --version
```
