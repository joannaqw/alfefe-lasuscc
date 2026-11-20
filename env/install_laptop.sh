#!/usr/bin/env bash
# One-time setup on a laptop/workstation. No HPC modules or Slurm needed.
#   Requirements: conda (Miniforge recommended: https://github.com/conda-forge/miniforge), internet.
#   Usage (from the repo root):  bash env/install_laptop.sh
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_NAME=alfefe-las
MRH_COMMIT=603e94440d44c689e0ccaf2e7d7afa02d3710f93   # cjknight/mrh, branch gpudev

CONDA=$(command -v mamba || command -v conda) || { echo "conda not found; install Miniforge first"; exit 1; }
if conda env list | awk '{print $1}' | grep -qx "$ENV_NAME"; then
  echo "conda env $ENV_NAME already exists, reusing it"
else
  "$CONDA" env create -f "$ROOT/env/environment.yml"
fi
eval "$(conda shell.bash hook)"
conda activate "$ENV_NAME"

mkdir -p "$ROOT/soft"
if [ ! -d "$ROOT/soft/mrh" ]; then
  git clone -b gpudev https://github.com/cjknight/mrh.git "$ROOT/soft/mrh"
fi
git -C "$ROOT/soft/mrh" checkout -q "$MRH_COMMIT"

# Build mrh's C library (CPU only) against the pip-installed pyscf
cmake -S "$ROOT/soft/mrh/lib" -B "$ROOT/soft/mrh/lib/build" \
      -DCMAKE_BUILD_TYPE=Release -DCMAKE_PREFIX_PATH="$CONDA_PREFIX" \
      -DPython_EXECUTABLE="$(command -v python)"
cmake --build "$ROOT/soft/mrh/lib/build" -j "$(getconf _NPROCESSORS_ONLN 2>/dev/null || echo 4)"

# Smoke test
PYTHONPATH="$ROOT/soft:${PYTHONPATH:-}" python - <<'PY'
import pyscf
from mrh.my_pyscf.mcscf import lasscf_async
from mrh.exploratory.unitary_cc import lasuccsd
from mrh.exploratory.citools import grad
print("OK: pyscf", pyscf.__version__, "+ mrh imported")
PY
echo
echo "Setup done. To use:  source env/activate_laptop.sh  then  python run_local.py --help"
