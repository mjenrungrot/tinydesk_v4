#!/usr/bin/env bash
#SBATCH --job-name=tinydesk_v4
#SBATCH --output=logs/%x-%j.out
#SBATCH --error=logs/%x-%j.err
#SBATCH --time=02:00:00
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G

set -euo pipefail

echo "TODO: implement SLURM run command"
