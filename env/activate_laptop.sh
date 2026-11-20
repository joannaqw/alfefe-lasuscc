# Usage (from the repo root):  source env/activate_laptop.sh
_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/.." && pwd)"
eval "$(conda shell.bash hook 2>/dev/null || conda shell.zsh hook)"
conda activate alfefe-las
export PYTHONPATH="$_ROOT/soft:${PYTHONPATH:-}"
unset _ROOT
echo "alfefe-las environment active (pyscf + mrh)."
