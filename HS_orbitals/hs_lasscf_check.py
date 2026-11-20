import pyscf
from pyscf import gto, scf, lib, mcscf,tools
from mrh.my_pyscf.mcscf.lasscf_o0 import LASSCF
from mrh.exploratory.unitary_cc import lasuccsd
from mrh.exploratory.unitary_cc.uccsd_sym0 import get_uccsd_op
from mrh.exploratory.citools import grad, lasci_ominus1
import numpy as np
import sys
from pyscf import gto, scf, tools,lib, mcscf
from pyscf.mcscf import avas,project_init_guess
from pyscf import mcscf
from mrh.my_pyscf.tools import molden
from mrh.my_pyscf.mcscf import lasscf_async as asyn
from mrh.util.chemistry import yamaguchi

mol_name='Al_Fe_Fe.xyz' # Al-Fe-Fe MOF node
basis={'C': 'cc-pvdz','H': 'cc-pvdz','O': 'cc-pvtz','Al': 'cc-pvtz','Fe': 'cc-pvtz'}
output='hs_lasscf_check.log'
lib.logger.TIMER_LEVEL = lib.logger.INFO
mol=gto.M(atom=mol_name,verbose=4,spin=9,charge=0,basis=basis,max_memory=10000,output=output) #spin = 2S
mol.use_gpu = False

mf=scf.RHF(mol)
mf=mf.density_fit()
mf.max_cycle=1
mf.mo_coeff=np.load('hf.npy')
mf.kernel()
#ncas,nelecas,guess_mo_coeff=avas.kernel(mf,['Fe 3d'],minao=mol.basis,openshell_option=3)
#tools.molden.from_mo(mol,'alfefe_10_11avas.molden',guess_mo_coeff)
#np.save('alfefe_10_11_avas', guess_mo_coeff)
#guess_mo_coeff = np.load('alfefe_10_11_avas.npy')
#final_list = [111,112,113,114,115, 116,117,118,119,120]

#mo_guess=np.load('final_las_10_11.npy')

las=asyn.LASSCF(mf,(5,5),((5,1),(5,0)),spin_sub=(5,6),verbose=4) # spin is 2S+1
mo = np.load('hs_lasscf_10_11.npy')
#guess_mo_sorted=las.sort_mo(final_list, guess_mo_coeff)
#mo_localized=las.set_fragments_(([17],[19]),guess_mo_sorted)
las.set_fragments_(([17],[19]),mo)
las.max_cycle_macro = 200
#las.set_fragments_(([17],[19]),mo)
#las.mo_coeff = mo
las.kernel(mo)
print('las energy', las.e_tot)
#np.save('converged_10_11',las.mo_coeff)
#from mrh.my_pyscf.tools import molden
#molden.from_lasscf(las,'alfefe_las_10_11.molden')
#np.save('converged_10_11',las.mo_coeff)
mc = mcscf.CASCI(mf,10, (10,1))
mc.kernel(las.mo_coeff)
print('casci',mc.e_tot)
exit()
