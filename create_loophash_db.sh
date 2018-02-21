#!/usr/bin/env bash
set -euo pipefail

mpirun \
    -np 32 ~/Softwares/Rosetta/main/source/bin/loophash_createfiltereddb.mpi.linuxgccrelease \
    -lh:db_path loophash_db/ \
    -in:file:vall ~/Softwares/Rosetta/tools/fragment_tools/vall.jul19.2011.gz \
    -lh:loopsizes  3 4 5 6 7 8 9 10 11 12 13 14  \
    -lh:num_partitions 32 \
    -lh:createdb_rms_cutoff 4.5 6 7.5 9 10.5 12 13.5 15 16.5 18 19.5 21 \
    > loophash_db/log.txt

# Or you could just copy Xingjie's files:
#    scp guybrush:/kortemmelab/home/xingjiepan/Databases/LoopHash/loophash_db .

