1. Open `1qjg.pdb' in pymol, delete everything but EQU in chain A, and save the 
   resulting model to `equ.pdb'.
2. Open `equ.pdb' in gvim and pymol.  In pymol, use `label not hydro, ID' to 
   show the atom numbers.  In gvim, manually rewrite all the CONECT records.
3. Use `babel equ.pdb equ.mol -h' to add hydrogens and to convert the ligand to 
   the molfile format.
4. Open `equ.mol' in gvim and manually identify the aromatic bonds.  
   Practically, this means setting the bond type (the third number in the 
   connect section) to 4 for all bonds between atoms 2-12.
5. Create a parameter file using:
   $ src/python/apps/public/molfile_to_params.py equ.mol -n EQU --clobber --centroid
6. Open `EQU_0001.pdb' in pymol to make sure it looks reasonable.
