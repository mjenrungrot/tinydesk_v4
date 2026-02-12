#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_PATH="${REPO_ROOT}/venv"
ENV_FILE="${REPO_ROOT}/environment.yml"
REQ_FILE="${REPO_ROOT}/requirements-pip.txt"

printf "\n[bootstrap] Repository: %s\n" "$REPO_ROOT"
printf "[bootstrap] Checking conda...\n"
if ! command -v conda >/dev/null 2>&1; then
  echo "[bootstrap] ERROR: conda not found. Install Conda/Miniconda first." >&2
  exit 1
fi
conda --version

echo "[bootstrap] Installing / updating environment: ${ENV_PATH}"
if [[ -f "${ENV_PATH}/conda-meta/history" ]]; then
  conda env update -p "${ENV_PATH}" -f "${ENV_FILE}"
else
  conda env create -p "${ENV_PATH}" -f "${ENV_FILE}"
fi

echo "[bootstrap] Installing pinned pip requirements"
"${ENV_PATH}/bin/pip" install --no-deps -r "${REQ_FILE}"

echo "[bootstrap] Bootstrap complete."
echo "[bootstrap] Next checks:"
echo "${ENV_PATH}/bin/python -c \"import torch, torchvision, torchaudio, numpy, matplotlib, lightning; print('tinydesk_v4 env ready')\""
