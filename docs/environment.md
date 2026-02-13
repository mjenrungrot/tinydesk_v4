# Project Environment (Local macOS + Remote SLURM)

This file is the environment contract for `tinydesk_v4`. It defines how to reproduce the same runtime for:

- Local development on this macOS machine.
- Remote compute on a SLURM cluster node.

The canonical sources for environment state are:

- `environment.yml` (base package set and Python version).
- `requirements-pip.txt` (additional pip-only pinned requirements).
- `scripts/bootstrap_venv.sh` (bootstrap helper).

## 1) Shared Environment Baseline

All locations use the same Python stack:

- Python: `3.13`
- Torch stack:
  - `torch==2.9.1`
  - `torchvision==0.24.1`
  - `torchaudio==2.9.1`
- Additional project/runtime tooling from `environment.yml` and `requirements-pip.txt`.

Acceptance smoke check (all locations):

```bash
./venv/bin/python -c "import torch, torchvision, torchaudio, numpy, matplotlib, lightning; print('tinydesk_v4 env ready')"
```

## 2) Local Environment (macOS)

### Scope

- Development machine: local macOS workstation.
- Default repo path:
  - `/Users/tjenrung/Workspaces/tinydesk_v4` (this machine, from this `pwd`).
- Default virtual environment path:
  - `<repo>/venv` (project-local, path-based conda env).

### Tooling

- macOS shell with git.
- Conda/Miniconda installed and available on `PATH`.
- Optional: `git`, `rsync` (for syncing to remote).

### Bootstrap

From repo root, run:

```bash
./scripts/bootstrap_venv.sh
```

Manual equivalent:

```bash
conda env create -p ./venv -f environment.yml
./venv/bin/pip install --no-deps -r requirements-pip.txt
```

If the env already exists:

```bash
conda env update -p ./venv -f environment.yml
./venv/bin/pip install --no-deps -r requirements-pip.txt
```

### Notes

- Prefer `./venv/bin/python` and `./venv/bin/pip` when running project jobs to avoid shell activation ambiguity.
- Use absolute paths in scripts only when they must run non-interactively.

## 3) Remote Environment (SLURM Node)

### Scope

- Execution happens on a SLURM-managed node.
- Repo checkout is separate from local macOS path.
- Environment must be independently provisioned on the remote filesystem.

### Recommended node layout

- Clone/Sync the repository to one of the project-approved remote paths:
  - `/gscratch/realitylab/tjenrung/tinydesk_v4`
  - `/mmfs1/gscratch/realitylab/tjenrung/tinydesk_v4`
- Keep virtual environment local to the repo for reproducibility:
  - `/home/<USER>/work/tinydesk_v4/venv`
  - or `/scratch/<USER>/tinydesk_v4/venv`

### Remote SLURM prerequisites

- Ensure the remote environment exposes `squeue` and `sinfo` commands from the same node/session where jobs are launched.
- Verify access after login:

```bash
squeue -V
sinfo -V
```

### SLURM job setup (template)

```bash
#!/usr/bin/env bash
#SBATCH --job-name=tinydesk_v4
#SBATCH --output=logs/%x-%j.out
#SBATCH --error=logs/%x-%j.err
#SBATCH --time=02:00:00
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G

set -euo pipefail

REPO_DIR="/path/to/tinydesk_v4"
cd "$REPO_DIR"

# Load conda on the cluster (adjust to your site init path/module names).
source "$HOME/miniconda3/etc/profile.d/conda.sh"
conda activate "$REPO_DIR/venv"

# Optional: keep heavy model/cache writes on node-local disk when available.
export HF_HOME="${SLURM_TMPDIR:-$REPO_DIR}/.cache/huggingface"
export TORCH_HOME="${SLURM_TMPDIR:-$REPO_DIR}/.cache/torch"

./venv/bin/python -c "import torch; print(torch.__version__)"
```

Replace `/path/to/tinydesk_v4` with the actual remote repo path.

### Environment updates on remote

From the remote checkout root:

```bash
conda env update -p ./venv -f environment.yml
./venv/bin/pip install --no-deps -r requirements-pip.txt
```

This keeps local and remote environments aligned with the same manifest.

## 4) Update policy

- Any dependency change must go through `environment.yml` and/or `requirements-pip.txt`.
- Run `./scripts/bootstrap_venv.sh` after dependency changes.
- Re-run the smoke check after every environment update.

## 5) Environment drift checks

- Prefer deterministic imports:

```bash
./venv/bin/python - <<'PY'
import torch, torchvision, torchaudio, numpy, matplotlib, lightning
print("torch", torch.__version__)
print("torchvision", torchvision.__version__)
print("torchaudio", torchaudio.__version__)
PY
```

- Validate local/remote manifest sync by checking:
  - no undocumented package additions in one location only,
  - both commands above succeed with the same active environment path.
