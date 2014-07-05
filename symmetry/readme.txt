We just want to generate a symmetry file that can be used with <wt.pdb> and 
<wt-lig.pdb>.  So we won't actually be using any of the PDB files in this 
directory.

1. Download 1qjg from the PDB.  This file contains KSI with both its ligands 
   and its symmetry mates.

2. Open <1qjg.pdb> and <../wt-lig.pdb> in pymol.  Superimpose them using the 
   super command, then remove the `wt-lig' model and save the resulting pdb:

   > super 1qjg, wt-lig
   > remove wt-lig
   > save 1qjg.pdb

3. Run <symmetrize.sh> to generate the symmetry file.  This script will also 
   generate a number of accessory files.  You can check to make sure that 
   <1qjg_INPUT.pdb> has one chain only and that it overlays well with 
   <../wt-lig.pdb>.  You can also check to make sure that <1qjg_symm.pdb> has 
   two KSI monomers that are oriented correctly with respect to each other.  
   But we won't use these files for any other purpose.

