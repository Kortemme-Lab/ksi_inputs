#!/usr/bin/env bash
set -euo pipefail

#$ -cwd
#$ -o 1qjg_clean_relax
#$ -j y
#$ -l mem_free=1G
#$ -l h_rt=12:00:00
#$ -t 1-100

hostname
date
pwd
echo "$@"

source rosetta.sh
relax_1qjg $SGE_TASK_ID


