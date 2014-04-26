#!/usr/bin/env sh

if [ $# -ne 1 ]; then
    echo "Usage: ./preprocess.sh <pdb>"
    exit
else
    pdb=$(basename ${1%.pdb})
    input=../../$1
fi

rosetta="../../../../../../../../.."
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
$rosetta_bin/fixbb                              \
    -in:file:fullatom                           \
    -in:file:s $pdb.pdb                         \
    -min_pack                                   \
    -use_input_sc false                         \
    -packing:repack_only                        \
    -extra_res_fa ../../ligand/EQU.fa.params    \
    -ex1 -ex2 -extrachi_cutoff 0                \
    -overwrite                                  \
    -nstruct 1

# Copy useful files into permanent locations.
cd ../..
cp scratch/$pdb/$pdb.pdb download/$pdb.pdb
cp scratch/$pdb/${pdb}_0001.pdb minpack/$pdb.pdb
cp scratch/$pdb/score.sc minpack/$pdb.score
gzip -c minpack/$pdb.pdb > minpack/$pdb.pdb.gz
ln -sf minpack/$pdb.pdb
ln -sf minpack/$pdb.pdb.gz
