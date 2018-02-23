#!/usr/bin/env python3

from prody import *

# Load the dimer + ligand structure.
ksi = parsePDB('1qjg.pdb')

# Only keep chains A+B.
ksi = ksi.select('chain A or chain B')

# Get rid of waters, ions, and the chain B ligand.
ksi = ksi.select('protein or (resname EQU and chain A)')

# Forget about any deleted atoms.
ksi = ksi.copy()

# Sequentially renumber the residues.
resis = ksi.getResindices() + 1
ksi.setResnums(resis)

# Put the ligand in chain X.
equ = ksi.select('resname EQU')
equ.setChids(['X'] * len(equ))

# Save the cleaned PDB.
writePDB('1qjg_clean.pdb', ksi)


