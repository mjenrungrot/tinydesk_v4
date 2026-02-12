# tinydesk_v4 Installation

This guide mirrors the v3 repository environment bootstrap flow.

## 0) Prerequisites

- Conda or Miniconda on PATH (`conda --version` succeeds).
- `git` checked out and you are in this repository root.

## 1) Create and activate the base environment

```bash
conda env create -p ./venv -f environment.yml
conda activate ./venv
```

If this is a re-run and the environment already exists, use:

```bash
conda env update -p ./venv -f environment.yml
```

## 2) Install Perception Models

```bash
./venv/bin/pip install --no-deps -r requirements-pip.txt
```

## 3) Optional: CUDA 12.8 wheel override

For GPU hosts using CUDA 12.8:

```bash
./venv/bin/pip install --index-url https://download.pytorch.org/whl/cu128 \
  --extra-index-url https://pypi.org/simple \
  --upgrade --force-reinstall \
  torch==2.9.1+cu128 torchvision==0.24.1+cu128 torchaudio==2.9.1+cu128
```

If your driver cannot support CUDA 12.8, stay on CPU wheels until compatible.

## 4) Optional local packages

When submodules are added to this repo, install them in editable mode from the repo root.

```bash
# Optional examples once submodules exist
./venv/bin/pip install -e ./sam3
./venv/bin/pip install -e ./sam2
./venv/bin/pip install --no-deps -e ./sam-audio
./venv/bin/pip install -e ./ImageBind
./venv/bin/pip install -e ./CLAP
```

## 5) Smoke checks

```bash
cd /path/to/tinydesk_v4
./venv/bin/python -c "import torch, torchvision, torchaudio, numpy, matplotlib, lightning; print('tinydesk_v4 env ready')"
```

Run additional checks only if those components are available in your checkout.
