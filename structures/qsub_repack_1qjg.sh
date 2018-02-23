#!/usr/bin/env sh

rm -rf 1qjg_clean_relax_repack
mkdir -p 1qjg_clean_relax_repack
qsub repack_1qjg.sh 
