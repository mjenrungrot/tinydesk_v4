# Repository & Environment Baseline

This repo uses a local conda environment at `./venv` to match the StageCraft/v3 bootstrap pattern.

## Current policy

- Environment path: `./venv`
- Python: 3.13
- Torch stack:
  - `torch==2.9.1`
  - `torchvision==0.24.1`
  - `torchaudio==2.9.1`
- Environment manifest: `environment.yml`
- Perception Models: `requirements-pip.txt`

## Why these pins

- Keep parity with `tinydesk_v3` so scripts and docs port cleanly.
- Prefer pip-installed PyTorch wheels to avoid mixed conda/pip binaries.
- Keep shared tooling (Ruff, Lightning, WandB, plotting and math stacks) in the shared environment.

## Update process

When dependencies change:

1. Edit `environment.yml`.
2. Run:

```bash
conda env update -p ./venv -f environment.yml
./venv/bin/pip install --no-deps -r requirements-pip.txt
```

3. Re-run smoke checks from `README.md`.

## Acceptance checks

- `./venv/bin/python -c "import torch, torchvision, torchaudio, numpy, matplotlib, lightning; print('StageCraft env ready')"`
- `conda env list | rg 'tinydesk_v4|stagecraft'`

## Notes

- This repo-level contract is intentionally lightweight: it documents reproducibility and bootstrap commands,
  while runtime-heavy model/data assets are intentionally outside source control.
