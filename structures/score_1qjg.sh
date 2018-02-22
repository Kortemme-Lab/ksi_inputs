#!/usr/bin/env bash
set -euo pipefail

BUILD=linuxclangrelease
FASTRELAX=$ROSETTA/source/bin/relax.$BUILD
SCORE=$ROSETTA/source/bin/score_jd2.$BUILD
INPUTS=$(realpath $(dirname $(realpath $0))/..)

$SCORE \
    -database $ROSETTA/database                                             \
    -in:file:s $INPUTS/structures/1qjg_clean*.pdb $INPUTS/structures/old_inputs/wt_lig_dimer.pdb \
    -in:file:native $INPUTS/structures/1qjg_clean.pdb                       \
    -extra_res_fa $INPUTS/ligand/EQU.fa.params                              \
    -out:file:scorefile_format json                                         \

python2 $ROSETTA/source/tools/scorefile.py score.sc | tee score.tab
