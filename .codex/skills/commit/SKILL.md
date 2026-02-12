---
name: commit
description: Use to run repo-aware git commit workflows with preflight validation, Conventional Commits checks, staging, optional tests, and optional push.
---

# Commit

Use this skill when the user asks to commit work in a git repository and wants a disciplined flow.

## Mandatory preflight
1. Confirm the request is in a git repository.
   - `git rev-parse --is-inside-work-tree`
2. Capture workspace state.
   - `git status --short`
   - `git diff --stat`
3. Show branch context.
   - `git branch --show-current`
   - `git status --short` (quick check for merge conflicts/staged vs unstaged)
4. If merge conflicts exist, stop and ask for conflict resolution first.
   - `git diff --check`
   - `git status --short` entries starting with `UU`, `AA`, `DD`, `DU`, or `UD`

## Repo-aware checks
1. If `AGENTS.md` exists, read and apply its commit/test requirements before continuing.
2. If `./venv/bin/python` exists, run the repository-standard smoke import:
   - `./venv/bin/python -c "import torch, torchvision, torchaudio, numpy, matplotlib, lightning; print('env ready')"`
3. If test targets are available, run targeted checks before commit:
   - `pytest`-style tests when `tests/`, `eval/`, or script-driven tests are present and likely relevant
   - Prefer `pytest <changed-test-paths>` over a full-suite run

## Commit message policy
1. Require Conventional Commits v1.0.0.
2. Validate message against:
   - `^(build|ci|chore|docs|feat|fix|perf|refactor|style|test|revert)(\([a-z0-9-]+\))?: .+$`
   - Optional body and `BREAKING CHANGE:` footer are allowed.
3. On malformed messages, refuse commit and request a corrected message.

## Commit execution
1. Stage selected files or all changes as requested.
2. Show final staged payload:
   - `git diff --cached`
3. Commit with the validated message.
4. Always print confirmation:
   - `git show --stat -1 --oneline`

## Optional push flow
1. Detect detached HEAD and stop push if detached.
   - `git symbolic-ref -q --short HEAD`
2. Detect upstream branch.
   - `git rev-parse --abbrev-ref --symbolic-full-name @{u}`
3. If upstream exists:
   - `git push`
4. If upstream does not exist:
   - Confirm intent and run `git push -u origin <branch>`

## Exit checks
- If untracked sensitive files are detected (`.env`, `*id_rsa*`, `*pem`, `*key`, `*secret*`), explicitly warn before commit.
- If no files are staged, ask user whether to stage everything or target files.
