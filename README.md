KSI Inputs
==========
This repository contains input files describing ketosteroid isomerase (KSI) for 
use in my project to rescue the D38E mutation via backbone remodeling.

Contents
--------
* ``fasta/`` Protein sequence files for the PDB files contained in this 
  repository.

* ``ligand/`` Parameters for the non-hydrolyzable ligand analog present in some 
  of the crystal structures of KSI.

* ``loops/`` Loop definitions.  These files indicate which residues will be 
  allowed to move in loop modeling simulations.

* ``pymol/`` Pymol sessions of KSI for quick viewing.  Not meant to be part of 
  the Pull into Place pipeline.

* ``resfile/`` Rosetta "resfiles" specifying which positions to repack and 
  design, and a script used to help generate resfiles.

* ``restraints/`` A restraint file specifying the desired coordinates of the 
  Asp/Glu carboxylate group and the parameters for the harmonic restraint.

* ``structures/`` Monomeric, dimeric, apo, and holo structures of KSI that have 
  been minimized and repacked in the rosetta score function.  I'm not sure 
  which version of the score function though (i.e. score12 or talaris2013), so 
  this probably needs to be repeated with scripts that are more reproducible.  
  The dimeric holo structure ``wt_lig_dimer.pdb.gz`` is the one you should use 
  unless you have a specific reason not to.

