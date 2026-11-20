import pyscf
from pyscf import gto, scf, lib, mcscf
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
output='lasscf_ls.log'
lib.logger.TIMER_LEVEL = lib.logger.INFO
mol=gto.M(atom=mol_name,verbose=4,spin=9,charge=0,basis=basis,max_memory=10000,output=output) #spin = 2S
mol.use_gpu = False

mf=scf.RHF(mol)
mf=mf.density_fit()
mf.max_cycle=1
mf.mo_coeff=np.load('hf.npy')
mf.kernel()

mo_guess=np.load('las_1011_ud.npy')

def lasuscc(spin_sub,frag0,frag1):
    las=asyn.LASSCF(mf,(5,5),(frag0,frag1),spin_sub=spin_sub,verbose=4) # spin is 2S+1
    las.set_fragments_(([17],[19]),mo_guess)
    las.mo_coeff=mo_guess
    las.kernel()
    #if spin_sub==(5,6):
    #    las.lasci()
    #elif spin_sub==(1,2):
    #    las.max_cycle_macro=1000
    #    np.save('lasscf_10_11_lowspin', las.mo_coeff)
    #    las.kernel()
        
    all_g, g_sel, a_idxs_selected, i_idxs_selected = grad.get_grad_exact(las, epsilon=0.00001)
    print ("All gradients = ", all_g)
    print ("Selected gradients = ", g_sel)

    excitations = []
    for a, i in zip(a_idxs_selected, i_idxs_selected):
        excitations.append((tuple(i), tuple(a[::-1])))

    print ("Selected excitations = ", excitations)

    epsilon=0.00001
    mc_uscc = mcscf.CASCI(mf,10,(5,6))
    mc_uscc.mo_coeff = las.mo_coeff
    lasci_ominus1.GLOBAL_MAX_CYCLE = 15000
    mc_uscc.fcisolver = lasuccsd.FCISolver_USCC(mol, a_idxs_selected, i_idxs_selected)
    #mc_uscc.fcisolver.nroots = 2
    mc_uscc.fcisolver.norb_f = [5,5]
    mc_uscc.kernel()
    print("Epsilon: {:.9f} | Number of parameters: {:.0f} | LASUSCCSD energy: {:.9f}".format(epsilon, len(a_idxs_selected), mc_uscc.e_tot))
    
    #return spin_sub
    return mc_uscc.fcisolver.energy, spin_sub
#keep below after storing LS lasscf guess except the lasuscc calls

spin_sub_LS = (5,6)
frag0 = (5,1)
frag1 =(0,5)
#spin_HS = lasuscc(spin_sub_HS,alpha_HS,beta_HS)
E_ls, spin_LS = lasuscc(spin_sub_LS,frag0,frag1)

#E_HS, spin_HS = lasuscc(spin_sub_HS,alpha_HS,beta_HS)
'''
E_LS, spin_LS = lasuscc(spin_sub_LS,alpha_LS,beta_LS)


S_HS = (spin_HS[0]-1)/2
S_LS = (spin_LS[0]-1)/2
S2_HS = S_HS*(S_HS+1)
S2_LS = S_LS*(S_LS+1)

E_roots = [E_LS, E_HS]
S2_roots = [S2_LS, S2_HS]
#J = yamaguchi(E_roots, S2_roots)
J = (E_LS - E_HS)/(S2_HS - S2_LS) 
print("Energies (LS, HS):", E_roots)
print("S^2 (LS, HS):", S2_roots)
print("J(LAS-USCC; 2 states) = {:.2f} cm^-1".format(J))
'''
#keep above
'''
#print(dir(mc_uscc.fcisolver))

# Get energy directly from the solver
E_roots = [mc_uscc.fcisolver.energy]

# Active space info
norb = mc_uscc.ncas
nelec = mc_uscc.nelecas

# Compute <S^2> for each root
S2_roots = [mc_uscc.fcisolver.spin_square(0, norb, nelec)[0]]

print("Energies from LASUSCC:", E_roots)
print("<S^2> values:", S2_roots)

# Only compute J if you have 2 energies
if len(E_roots) == 2:
    J = yamaguchi(E_roots, S2_roots)
    print("J(LASUSCC; {} states) = {:.2f} cm^-1".format(len(E_roots), J))
else:
    print("Cannot compute J: need 2 spin states (HS + LS), currently have", len(E_roots))



# After mc_uscc.kernel()
#mc_uscc.analyze()

# Extract energies manually
#E_roots = [root.e for root in mc_uscc.fcisolver.root_list]  # list of energies for all roots
if hasattr(mc_uscc.fcisolver, "e"):
    E_roots = np.atleast_1d(mc_uscc.fcisolver.e)
elif hasattr(mc_uscc.fcisolver, "e_tot"):
    E_roots = np.atleast_1d(mc_uscc.fcisolver.e_tot)
else:
    raise AttributeError("Could not find energy attribute in FCISolver_USCC")

print("Energies from LASUSCC:", E_roots)
# Extract <S^2> for each root
S2_roots = [mc_uscc.fcisolver.spin_square(i)[0] for i in range(mc_uscc.fcisolver.nroots)]

# Compute J using Yamaguchi formula
J = yamaguchi(E_roots, S2_roots)

print("J(LASUSCC; {} states) = {:.2f} cm^-1".format(len(E_roots), J))
'''
print("done")
