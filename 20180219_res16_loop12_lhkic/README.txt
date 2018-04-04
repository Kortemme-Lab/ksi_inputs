`flags`
   In previous iterations of this protocol, we had to provide rosetta with 
   ligand parameters via the `-extra_res_fa` flag.  However, this no longer 
   seems necessary.  On top of that, there seemed to be a problem with the 
   params files that would cause the ligand atoms to be in the wrong place in 
   the PDB produced at the end of a rosetta run.  I tried regenerating the 
   ligand parameters, but that didn't help.

`foldtree`
   This fold tree was handwritten to to accomplish the following things:

   - Connect the two chains at their closest point, to reduce lever arm effects 
     if I ever do move the monomers relative to each other.

   - Anchor the ligand in place.

   - Prevent movements in either loop from propagating to the rest of the 
     protein.

   I chose residue 100 as the root of the fold tree because it's directly 
   across from itself (residue 225 in the opposite monomer) in the dimer 
   interface.  The symmetry of it being near itself appealed to me, but to be 
   honest it's not really important.  You just needs two residues that are 
   close together in the dimer interface to reduce the lever arm effect.

   I connected the ligand directly to residue 100 to ensure that it won't move 
   in response to anything else in the protein.  This is important, because my 
   constraints file is based on the original coordinates of the ligand, so I 
   really don't want it to move.

   I put the chainbreaks near the middle of the each loop, because I remember 
   hearing from Amelie that torsion minimization works better when a similar 
   number of residues are being moved on either side of the chainbreak.  I 
   haven't tested this myself, but it sounds reasonable.

`loops`
   I chose residues 26 and 51 as the endpoints for the active site loop because 
   they're each about a half-turn into the α-helices flanking the designed 
   region.  This anchors the loop in a relatively rigid part of the enzyme, but 
   still allows the takeoff and landing points of the loop to move slightly.
   
   Similarly, I chose residues 198 and 203 as the endpoints for the turn on the 
   opposite monomer.  These endpoints anchor the turn in the β-sheet flanking 
   the turn.  I didn't want to make this loop very big, since it's not the main 
   focus of the design.  I made it 6 residues because I wanted to allow the 
   take-off and landing points to move slightly, and I wanted there to be more 
   than one non-pivot torsion, so 4 residues would've been too small.

   I put the cutpoints in the same places as the chainbreaks in the foldtree, 
   and for the same reasons.  The foldtree and loops files are never actually 
   used together, but the loop modeling protocol automatically generates a 
   foldtree from the loops file, with chainbreaks at the cutpoints.  I want the 
   chainbreaks to be in the same place for both foldtrees.

   The `extend` flag (i.e. the last number on each line) is 0 for these loops, 
   because they're too big to rebuild from scratch.

`build_models/loops`
   Only move designable residues in the model building stage, because lhKIC 
   designs every residue it moves.  These loops are also small enough to 
   rebuild from scratch, which should help produce a broader diversity of 
   backbone models (relative to starting every simulation from the same 
   wildtype loop conformation).

`restraints`
   These coordinates come from D38 in `wt.pdb`, which is derived from 8CHO.  
   This PDB has the wildtype Asp at position 38, but it doesn't have the 
   ligand.  The actual input structure was created by superimposing a structure 
   of the KSI dimer with the ligand on `wt.pdb`, 

   I don't know why I decided to make the restraint on CG weaker than the 
   others.  Probably I was thinking that it was less important, but 

`input.pdb`
   Not sure how the input was prepared...

`design_only.resfile`
   This resfile simply encompasses the whole active site loop, the beta strand 
   leading up to it, and the turn on the opposite monomer.  Compared to our 
   previous resfile, this one allows two more positions to design on each side 
   of the active site loop, which we hope will lead to design models that 
   better satisfy the constraints:

   Positions 35+37: Previously we excluded these positions because they're 
   pointing into solvent and clearly not affecting the active site loop.  
   Despite that, we now think that the more important thing is to create a more 
   diverse set of backbones in the initial model building step.  Allowing 
   loophash to design the whole loop should help accomplish that.  We'll use 
   LayerDesign in the next step to make sure we still end up with greasy 
   residues on the inside and polar one on the outside.

   Positions 45+46: Design the active site loop up to G47.  We don't think it 
   would be wise to include G47 in the design, since it seems to be responsible 
   for breaking the α-helix at position 48.  Previously we stopped at position 
   44 in hopes of keeping its salt-bridge with E53, but Rosetta usually got rid 
   of that interaction anyways.

   We'll be using LayerDesign and ConsensusLoopDesign to restrict which 
   residues can go where, so the only thing we need to specify here is `NOTAA 
   CH`.  We never want cysteine because it can mess up the global fold by 
   forming unexpected disulfides, and we never want histidine because it's 
   behavior can be pH dependent.

`compare_to_representative.sho`
   Run PyMOL to show how to Rosetta score function differently scores two 
   design models.

`compare_to_wildtype.sho`
   Run PyMOL to show the differences between a design model and wildtype KSI.

`build_models.xml`
   Use lhKIC to build models.  Prevent position 38 from designing, since we 
   know we want a Glu there (and because mutating it would break the  
   restraints).

`design_models.xml`
   Use FastDesign to design design the loops.  Setup the foldtree and the 
   movemap to prevent the backbone from moving outside of the loop region.

   For the turn, use ConsensusLoopDesign to ensure that we get a sequence that 
   is known to be capable of forming turns.  Typically this means having either 
   Gly or Asn somewhere in the turn, depending on it's precise geometry.

`shared_defs.xml`
   The "ex" and "chi" task operations are included on the recommendation of 
   this page:

      https://www.rosettacommons.org/docs/latest/scripting_documentation/RosettaScripts/TaskOperations/Recommended_Design_TaskOperations
   
`validate_designs.xml`
   Use fKIC to validate designs.  It's nice that this is a different method 
   than e used to build the loops in the first place.

