#!/usr/bin/env python
"""Run the Al-Fe-Fe calculations on a laptop/workstation (no Slurm, no HPC modules).

Reproduces the inputs in LS_lasuscc/eps_*/alfefe_lasuscc.py and
HS_orbitals/hs_lasscf_check.py with identical settings; only file paths,
thread count, memory, and the optional iteration cap are configurable.

Examples (after `source env/activate_laptop.sh`):
    python run_local.py ls --eps 5e-2            # quickest LS LAS-USCCSD run (~11 params)
    python run_local.py ls --eps 1e-3 -n 8 --mem 12000
    python run_local.py hs                       # check the HS LASSCF orbitals
"""
import argparse
import os
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
INPUTS = os.path.join(ROOT, 'inputs')

# Common settings, copied from the original inputs
GEOM = os.path.join(INPUTS, 'Al_Fe_Fe.xyz')            # Al-Fe-Fe MOF node
HF_MO = os.path.join(INPUTS, 'hf.npy')
LS_GUESS = os.path.join(INPUTS, 'las_1011_ud.npy')
HS_ORBS = os.path.join(ROOT, 'HS_orbitals', 'hs_lasscf_10_11.npy')
BASIS = {'C': 'cc-pvdz', 'H': 'cc-pvdz', 'O': 'cc-pvtz', 'Al': 'cc-pvtz', 'Fe': 'cc-pvtz'}
SPIN = 9      # 2S of the molecule object (as in the original inputs)
CHARGE = 0
FRAG_ATOMS = ([17], [19])  # 0-based atom indices of the two Fe centers


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='calc', required=True)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument('-n', '--threads', type=int, default=os.cpu_count(),
                        help='OpenMP threads (default: all cores)')
    common.add_argument('--mem', type=int, default=10000,
                        help='PySCF max_memory in MB (original runs: 10000)')
    common.add_argument('-o', '--outdir', default=None, help='output directory')
    ls = sub.add_parser('ls', parents=[common], help='LS LASSCF + LAS-USCCSD')
    ls.add_argument('--eps', type=float, required=True,
                    help='gradient threshold for excitation selection (e.g. 0, 1e-3, 5e-2)')
    ls.add_argument('--max-cycle', type=int, default=15000,
                    help='USCC optimizer iteration cap (original runs: 15000)')
    sub.add_parser('hs', parents=[common], help='reload HS LASSCF orbitals, rerun LASSCF + CASCI')
    return p.parse_args()


def setup(args, default_outdir, logname):
    os.environ.setdefault('OMP_NUM_THREADS', str(args.threads))  # must precede numpy/pyscf import
    outdir = os.path.abspath(args.outdir or os.path.join(ROOT, 'local_runs', default_outdir))
    os.makedirs(outdir, exist_ok=True)
    os.chdir(outdir)  # lasscf_async writes per-fragment logs next to the main log
    import numpy as np
    from pyscf import gto, scf, lib
    lib.num_threads(args.threads)
    lib.logger.TIMER_LEVEL = lib.logger.INFO
    mol = gto.M(atom=GEOM, verbose=4, spin=SPIN, charge=CHARGE, basis=BASIS,
                max_memory=args.mem, output=os.path.join(outdir, logname))
    mol.use_gpu = False
    mf = scf.RHF(mol).density_fit()
    mf.max_cycle = 1               # orbitals are loaded, not re-optimized
    mf.mo_coeff = np.load(HF_MO)
    mf.kernel()
    print(f'Output directory: {outdir}\nLog: {mol.output}\nThreads: {args.threads}  max_memory: {args.mem} MB')
    return np, mf, outdir


def run_ls(args):
    np, mf, outdir = setup(args, f'LS_eps_{args.eps:g}', 'lasscf_ls.log')
    from pyscf import mcscf
    from mrh.my_pyscf.mcscf import lasscf_async as asyn
    from mrh.exploratory.unitary_cc import lasuccsd
    from mrh.exploratory.citools import grad, lasci_ominus1

    mo_guess = np.load(LS_GUESS)
    las = asyn.LASSCF(mf, (5, 5), ((5, 1), (0, 5)), spin_sub=(5, 6), verbose=4)
    las.set_fragments_(FRAG_ATOMS, mo_guess)
    las.mo_coeff = mo_guess
    las.kernel()
    print(f'LS LASSCF energy: {las.e_tot:.9f}  (reference: -3971.790909246)')

    all_g, g_sel, a_idxs, i_idxs = grad.get_grad_exact(las, epsilon=args.eps)
    print('Selected excitations =', [(tuple(i), tuple(a[::-1])) for a, i in zip(a_idxs, i_idxs)])

    mc = mcscf.CASCI(mf, 10, (5, 6))
    mc.mo_coeff = las.mo_coeff
    lasci_ominus1.GLOBAL_MAX_CYCLE = args.max_cycle
    mc.fcisolver = lasuccsd.FCISolver_USCC(mf.mol, a_idxs, i_idxs)
    mc.fcisolver.norb_f = [5, 5]
    mc.kernel()
    line = 'Epsilon: {:.9f} | Number of parameters: {:.0f} | LASUSCCSD energy: {:.9f}'.format(
        args.eps, len(a_idxs), mc.e_tot)
    print(line)
    np.save(os.path.join(outdir, 'las_mo_coeff.npy'), las.mo_coeff)
    with open(os.path.join(outdir, 'result.txt'), 'w') as f:
        f.write(line + f'\nCASCI converged: {mc.converged}\n')


def run_hs(args):
    np, mf, outdir = setup(args, 'HS_check', 'hs_lasscf_check.log')
    from pyscf import mcscf
    from mrh.my_pyscf.mcscf import lasscf_async as asyn

    mo = np.load(HS_ORBS)
    las = asyn.LASSCF(mf, (5, 5), ((5, 1), (5, 0)), spin_sub=(5, 6), verbose=4)
    las.set_fragments_(FRAG_ATOMS, mo)
    las.max_cycle_macro = 200
    las.kernel(mo)
    print(f'las energy {las.e_tot:.11f}  (reference: -3971.79166849281)')
    mc = mcscf.CASCI(mf, 10, (10, 1))
    mc.kernel(las.mo_coeff)
    print(f'casci {mc.e_tot:.11f}')


if __name__ == '__main__':
    a = parse_args()
    t0 = time.time()
    run_ls(a) if a.calc == 'ls' else run_hs(a)
    print(f'Done in {(time.time() - t0) / 60:.1f} min')
    sys.stdout.flush()
