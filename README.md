# tinydesk_v4

[![CI](https://github.com/mjenrungrot/tinydesk_v4/actions/workflows/ci.yml/badge.svg)](https://github.com/mjenrungrot/tinydesk_v4/actions/workflows/ci.yml)

## Environment Setup (Miniconda → `./venv`)

1. Create the base environment at `./venv`:

```bash
conda env create -p ./venv -f environment.yml
```

2. Activate the environment:

```bash
conda activate ./venv
```

3. Install Perception Models dependencies:

```bash
./venv/bin/pip install --no-deps -r requirements-pip.txt
```

4. Run the bootstrap smoke check:

```bash
./venv/bin/python -c "import torch, torchvision, torchaudio, numpy, matplotlib, lightning; print('StageCraft env ready')"
```

5. For full setup details, see `INSTALLATION.md`.
