#!/usr/bin/env sh

trap "" HUP

if [ $# -eq 1 ]; then
    input=../../$1
    pdb=$(basename ${1%.pdb})
elif [ $# -eq 2 ]; then
    input=../../$1
    pdb=$2
else
    echo "Usage: ./preprocess.sh <pdb>"
    exit
fi

rosetta=~/rosetta/ksi
rosetta_bin="$rosetta/source/bin"

rm -rf scratch/$pdb
mkdir -p scratch/$pdb
cd scratch/$pdb

# Download a clean copy of the structure from the PDB.
if [ -e $input ]; then
    cp $input $pdb.pdb
else
    fetch-pdb $pdb
    head $pdb.pdb
fi

# Relax the structure using the rosetta score function.
$rosetta_bin/fixbb                                          \
    -in:file:fullatom                                       \
    -in:file:s $pdb.pdb                                     \
    -min_pack                                               \
    -use_input_sc false                                     \
    -packing:repack_only                                    \
    -extra_res_fa "../../ligand/EQU.fa.params"              \
    -ex1 -ex2 -extrachi_cutoff 0                            \
    -overwrite                                              \
    -nstruct 1

    #-symmetry_definition "../../dimer.symm"                 \

# Copy useful files into permanent locations.
cd ../..
cp scratch/$pdb/$pdb.pdb download/$pdb.pdb
cp scratch/$pdb/${pdb}_0001.pdb minpack/$pdb.pdb
cp scratch/$pdb/score.sc minpack/$pdb.score
gzip -c minpack/$pdb.pdb > minpack/$pdb.pdb.gz
ln -sf minpack/$pdb.pdb
ln -sf minpack/$pdb.pdb.gz
