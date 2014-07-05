#!/usr/bin/env sh

rosetta="$HOME/rosetta/ksi"
rosetta_bin="$rosetta/source/bin"

# Relax the structure using the rosetta score function.
$rosetta_bin/fixbb                              \
    -in:file:fullatom                           \
    -in:file:s "wt-lig.pdb"                     \
    -use_input_sc false                         \
    -packing:repack_only                        \
    -extra_res_fa "../ligand/EQU.fa.params"     \
    -symmetry_definition "1qjg.symm"            \
    -ex1 -ex2 -extrachi_cutoff 0                \
    -overwrite                                  \
    -nstruct 1

    #-min_pack                                   \
