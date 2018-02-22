#!/usr/bin/env bash
set -euo pipefail

# Expect $ROSETTA and $ROSETTA_BUILD to be set as environment variables.

BIN=$ROSETTA/source/bin
INPUTS=$(realpath $(dirname $(realpath $0))/..)

function relax_1qjg () {
    mkdir -p 1qjg_clean_relax
    $BIN/rosetta_scripts.$ROSETTA_BUILD                                     \
        -in:file:s $INPUTS/structures/1qjg_clean.pdb                        \
        -in:file:extra_res_fa $INPUTS/ligand/EQU.fa.params                  \
        -parser:protocol $INPUTS/structures/relax_1qjg.xml                  \
        -out:suffix _relax/$1                                               \
        -out:no_nstruct_label                                               \
        -out:overwrite                                                      \
        -relax:constrain_relax_to_start_coords                              \
        -relax:coord_constrain_sidechains                                   \
        -relax:ramp_constraints true                                        \
        -packing:ex1                                                        \
        -packing:ex2                                                        \
        -packing:use_input_sc                                               \
        -packing:flip_HNQ                                                   \
        -packing:no_optH false                                              \
        | tee 1qjg_clean_relax/$1.stdout
}

function score_1qjg_models () {
    $BIN/score.$ROSETTA_BUILD                                               \
        -database $ROSETTA/database                                         \
        -in:file:s                                                          \
            $INPUTS/structures/1qjg_clean.pdb                               \
            $INPUTS/structures/1qjg_clean_relax/*.pdb                       \
        -in:file:native $INPUTS/structures/1qjg_clean.pdb                   \
        -extra_res_fa $INPUTS/ligand/EQU.fa.params                          \
        -out:file:scorefile_format json                                     #

    python2 $ROSETTA/source/tools/scorefile.py score.sc | tee score.tab
}
