#!/usr/bin/env bash
set -euo pipefail

#$ -S /bin/bash
#$ -cwd
#$ -o 1qjg_clean_relax
#$ -j y
#$ -l mem_free=1G
#$ -l arch=linux-x64
#$ -l netapp=1G,scratch=1G
#$ -l h_rt=12:00:00
#$ -t 1-100

source rosetta.sh
relax_ksi 3nhx.pdb $SGE_TASK_ID


