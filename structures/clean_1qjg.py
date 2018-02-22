#!/usr/bin/env python3

from prody import *

# Load PDB
ksi = parsePDB('1qjg')

# Only keep chains A+B
ksi = ksi.select('chain A or chain B')

# Get rid of waters, ions, and the chain B ligand.
ksi = ksi.select('protein or (resname EQU and chain A)')

# Forget about any deleted atoms.
ksi_clean = ksi.copy()

# Renumber residues
resis = ksi_clean.getResindices() + 1
ksi_clean.setResnums(resis)

# Save the cleaned PDB.
writePDB('1qjg_clean.pdb', ksi_clean)


