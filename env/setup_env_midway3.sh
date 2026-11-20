module unload python
module load python/anaconda-2021.05
module load cmake/3.26
module load mpich
module load gcc
module load cuda

. /project/lgagliardi/knight/LASSCF_gpudev/soft/my_env/bin/activate

export PYTHONPATH=/project/lgagliardi/knight/LASSCF_gpudev/soft/pyscf:$PYTHONPATH
export PYTHONPATH=/project/lgagliardi/knight/LASSCF_gpudev/soft/pyscf-forge:$PYTHONPATH
export PYTHONPATH=/project/lgagliardi/knight/LASSCF_gpudev/soft/mrh/gpu:$PYTHONPATH
export PYTHONPATH=/project/lgagliardi/knight/LASSCF_gpudev/soft:$PYTHONPATH
#export PYTHONPATH=/project/lgagliardi/valayagarawal/Apps/pyscf:$PYTHONPATH
#export PYTHONPATH=/project/lgagliardi/valayagarawal/Apps/pyscf-forge:$PYTHONPATH
#export PYTHONPATH=/project/lgagliardi/valayagarawal/Apps/mrh-cpu/mrh/gpu:$PYTHONPATH
#export PYTHONPATH=/project/lgagliardi/valayagarawal/Apps/mrh-cpu:$PYTHONPATH


# -- should probably replace this with job-specific tmp
#export PYSCF_TMPDIR=/project/lgagliardi/knight/LASSCF_gpudev/tmp

# -- resolve issue with static linkage
#INTEL MKL ERROR: /software/python-anaconda-2021.05-el8-x86_64/lib/libmkl_avx512.so.1: undefined symbol: mkl_sparse_optimize_bsr_trsm_i8.
#Intel MKL FATAL ERROR: Cannot load libmkl_avx512.so.1 or libmkl_def.so.1.
#MKL=/software/python-anaconda-2021.05-el7-x86_64/lib
MKL=/software/python-anaconda-2021.05-el8-x86_64/lib
#MKL=${CONDA_PREFIX}/lib
#export LD_PRELOAD=${MKL}/libmkl_def.so.2:${MKL}/libmkl_avx2.so.2:${MKL}/libmkl_core.so:${MKL}/libmkl_intel_lp64.so:${MKL}/libmkl_intel_thread.so:${MKL}/libiomp5.so
export LD_PRELOAD=${MKL}/libmkl_def.so.1:${MKL}/libmkl_avx2.so.1:${MKL}/libmkl_core.so:${MKL}/libmkl_intel_lp64.so:${MKL}/libmkl_intel_thread.so:${MKL}/libiomp5.so

# -- pyscf cmake command
# scripts/build_pyscf.sh 

# -- mrh cmake command
# scripts build_mrh.sh 

# run examples (in conda)
