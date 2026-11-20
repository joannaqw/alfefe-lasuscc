# Al–Fe–Fe MOF node: LS LAS-USCCSD calculations + HS LASSCF orbitals

LASSCF(10,11) / LAS-USCCSD calculations on an Al–Fe–Fe MOF node
(two Fe 3d fragments, 5 orbitals each; `mol.spin = 9`, charge 0).
Basis: cc-pVTZ on Fe, Al, O; cc-pVDZ on C, H; density fitting; RHF reference loaded from `inputs/hf.npy`.

## Layout

```
inputs/            shared inputs (identical across all LS runs)
  Al_Fe_Fe.xyz       geometry
  hf.npy             RHF MO coefficients (loaded, 1 SCF cycle)
  las_1011_ud.npy    LS LASSCF starting orbitals
HS_orbitals/       high-spin LASSCF(10,11) orbitals
  hs_lasscf_10_11.npy        converged HS LASSCF MO coefficients
  alfefe_las_10_11.molden    Molden file of the same orbitals
  hs_lasscf_check.py         script that reloads them and reruns LASSCF + CASCI
  hs_lasscf_check.log/.out   output of that check
LS_lasuscc/        low-spin LAS-USCCSD runs, one folder per gradient threshold epsilon
  eps_<value>/
    alfefe_lasuscc.py   input (only epsilon differs between folders)
    run.slurm           Midway3 submission script
    lasuscc.out         stdout (summary line: "Epsilon | Number of parameters | LASUSCCSD energy")
    lasscf_ls.log*      PySCF/mrh logs (LASSCF + USCC CASCI iterations)
    lasuscc_alfefe.err  stderr (only warnings)
    *.npy, *.xyz, setup_env_midway3.sh -> symlinks into ../../inputs and ../../env
env/
  setup_env_midway3.sh     environment used for the runs (UChicago Midway3)
  software_versions.txt    pyscf / pyscf-forge / mrh commits, numpy/scipy versions
  install_from_source.sh   rebuild the stack on another machine
  pip_freeze_my_env.txt    full pip freeze of the venv
```

## HS orbitals

`HS_orbitals/hs_lasscf_10_11.npy` is the converged HS LASSCF solution:
fragments `((5,1),(5,0))`, `spin_sub=(5,6)`, `set_fragments_(([17],[19]), mo)`.
Restarting LASSCF from these orbitals converges in **1 macro cycle** to

    E(HS LASSCF) = -3971.79166849281 Ha   (CASCI(10,(10,1)) on same orbitals: -3971.79166849282)

(see `HS_orbitals/hs_lasscf_check.out`).

## LS LAS-USCCSD results

All LS runs: `LASSCF(mf, (5,5), ((5,1),(0,5)), spin_sub=(5,6))` from `las_1011_ud.npy`, then
`grad.get_grad_exact(las, epsilon)` to select excitations and
`CASCI(mf, 10, (5,6))` with `lasuccsd.FCISolver_USCC` (`norb_f=[5,5]`, `GLOBAL_MAX_CYCLE = 15000`).
LS LASSCF energy (identical in every run): **-3971.790909246 Ha**.

| folder | epsilon | # params | E(LAS-USCCSD) / Ha | CASCI converged | ⟨S²⟩ |
|---|---|---|---|---|---|
| eps_0    | 0     | 6200 | -3971.792171814 | no  | 0.940 |
| eps_1e-7 | 1e-7  | 1922 | -3971.792113791 | no  | 2.991 |
| eps_1e-6 | 1e-6  | 1825 | -3971.792119206 | no  | 2.748 |
| eps_1e-5 | 1e-5  | 1527 | -3971.792110609 | no  | 3.090 |
| eps_1e-4 | 1e-4  |  824 | -3971.792127290 | no  | 2.579 |
| eps_1e-3 | 1e-3  |  613 | -3971.792079609 | yes | 4.715 |
| eps_5e-3 | 5e-3  |  411 | -3971.792079139 | no  | 4.739 |
| eps_1e-2 | 1e-2  |  257 | -3971.792078806 | no  | 4.741 |
| eps_2e-2 | 2e-2  |   78 | -3971.791686389 | yes | 4.745 |
| eps_3e-2 | 3e-2  |   34 | -3971.791513324 | no  | 4.746 |
| eps_4e-2 | 4e-2  |   20 | -3971.791527661 | yes | 4.745 |
| eps_5e-2 | 5e-2  |   11 | -3971.791517637 | yes | 4.745 |

"CASCI converged" and ⟨S²⟩ are taken from the last `CASCI E = ...` line in `lasscf_ls.log`;
"not converged" means the USCC optimizer stopped at the iteration cap.

## How to run

On Midway3 (with access to `/project/lgagliardi`):

```bash
cd LS_lasuscc/eps_1e-3
sbatch run.slurm          # sources setup_env_midway3.sh, writes lasuscc.out and lasscf_ls.log
```

Elsewhere: build the stack with `bash env/install_from_source.sh <dir>`, activate it and set
`PYTHONPATH` as printed at the end. In `env/setup_env_midway3.sh`, replace the paths
and the `module` and `LD_PRELOAD` lines with your own, then run `python alfefe_lasuscc.py`
inside a run folder. To check the HS orbitals: `cd HS_orbitals && ln -s ../inputs/hf.npy ../inputs/Al_Fe_Fe.xyz . && python hs_lasscf_check.py`.

Resources used: 1 node, 8 CPUs, 10 GB/CPU.

## Caveats

- The pyscf/pyscf-forge/mrh checkouts listed in `env/software_versions.txt` were recorded after the
  runs; they were updated in Oct 2026, so they may differ from the exact code that produced these outputs.
- `inputs/hf.npy` is the RHF guess that every script loads, with `mf.max_cycle = 1` (the log says "SCF not converged"; this is expected).
