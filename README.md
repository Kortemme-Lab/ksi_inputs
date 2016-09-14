KSI Inputs
==========
This repository contains input files describing ketosteroid isomerase (KSI) for 
use in my project to rescue the D38E mutation via backbone remodeling.

Contents
--------
The top level of the repository contains symlinks to minpacked PDB files and a 
few assorted processing scripts.  I think it would be good to reorganize this 
such that all the PDB files are in their own directory and all the scripts are 
in the same directories as the files they operate on.

* ``fasta/`` Protein sequence files for the PDB files contained in this 
  repository.

* ``ligand/`` Parameters for the non-hydrolyzable ligand analog present in some 
  of the crystal structures of KSI.

* ``loops/`` Loop definitions.  These files indicate which residues will be 
  allowed to move in loop modeling simulations.

* ``minpack/`` PDB files that have been minimized and repacked in the rosetta 
  score function.  I'm not sure which version of the score function though 
  (i.e. score12 or talaris2013), so this probably needs to be repeated with 
  scripts that are more reproducible.

* ``sessions/`` Pymol sessions of KSI for quick viewing.  Not meant to be part 
  of the Pull into Place pipeline.

* ``symmetry/`` Parameters for simulating the KSI dimer in symmetry mode.  I 
  never got this to work, and I now prefer to design KSI by focusing only on 
  one active site and not using symmetry, but I'm keeping these files here for 
  future reference.



