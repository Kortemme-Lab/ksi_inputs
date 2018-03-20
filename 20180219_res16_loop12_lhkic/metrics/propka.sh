#!/usr/bin/env bash
set -euo pipefail

# Installing PROPKA
# =================
# 1. Download the source code from Github and copy it onto the cluster:
#
#       https://github.com/jensengroup/propka-3.1
#
# 2. Run the setup.py script:
#
#       $ scl enable python27 'python setup.py install --user'

# Unzip and aggressively clean the structure.
pdb=$(mktemp '/tmp/propka_input_XXXXXX.pdb')
trap "rm -f $pdb" EXIT
zcat $1 | grep '^ATOM' > $pdb

PKA_WT=6.19  # From running PROPKA on PDB ID: 8cho
PKA_MODEL=$(
    # Run the pKa predictor on the given structure.
    scl enable python27 "~/.local/bin/propka31 $pdb" |
    # Mirror the output to stderr so we can see it.
    tee /dev/stderr |
    # Find the prediction for E38.  Look in the summary section (that's what 
    # the leading spaces are for), because the first section sometimes has a 
    # trailing asterisk...
    grep '^   GLU  38 A' |
    # Report it to stdout, where it will be captured in `PKA_MODEL`
    awk '{ print $4 }'
) 2>&1
PKA_OFFSET=$(python -c "print abs($PKA_MODEL - $PKA_WT)")

# Clean up all the output files that are spewed by PROPKA.
rm -f propka_input_*.{pka,propka_input}

echo "EXTRA_METRIC pKa (E38) ${PKA_MODEL}"
echo "EXTRA_METRIC pKa Offset (E38) ${PKA_OFFSET}"
