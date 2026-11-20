#!/bin/bash
# Rebuild the software stack outside Midway3 (adjust compilers/BLAS for your machine).
# Usage: bash env/install_from_source.sh <install_dir>
set -e
D=${1:-$PWD/soft}; mkdir -p $D; cd $D
python3 -m venv my_env && . my_env/bin/activate
pip install "numpy==1.24.3" "scipy==1.10.1" "h5py==3.1.0" cmake
git clone https://github.com/pyscf/pyscf.git       && git -C pyscf checkout 52f57374ce073b75e9ca7a9dcabddfe9f7a9e920
git clone https://github.com/pyscf/pyscf-forge.git && git -C pyscf-forge checkout 2ba0e504d56e6f9aa098bb3ef877c743f8c8f0b2
git clone -b gpudev https://github.com/cjknight/mrh.git && git -C mrh checkout 603e94440d44c689e0ccaf2e7d7afa02d3710f93
(cd pyscf/pyscf/lib && mkdir -p build && cd build && cmake .. && make -j8)
(cd pyscf-forge/pyscf/lib && mkdir -p build && cd build && cmake .. && make -j8)
(cd mrh/lib && mkdir -p build && cd build && cmake .. && make -j8)
cat <<MSG
Done. Before running, do:
  . $D/my_env/bin/activate
  export PYTHONPATH=$D/pyscf:$D/pyscf-forge:$D/mrh/gpu:$D:\$PYTHONPATH
MSG
