#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# Use Roland and Noah's clash-based repack shell algorithm to add repack 
# positions to a resfile.

rosetta=${1:-}
repack_shell_app=$rosetta/source/bin/create_clash-based_repack_shell
design_positions=${2:-}
output_path='resfile'

if [[ -z $rosetta | -z $design_positions ]]; then
    echo "Usage: add_repack_positions.sh <path_to_rosetta> <design_positions>"
    exit 1
fi

if [[ ! -e $repack_shell_app ]]; then
    echo "Error: Couldn't find '$repack_shell_app'"
    echo "Try compiling rosetta with:"
    echo "    ./scons.py bin/create_clash-based_repack_shell"
    exit 1
fi

if [[ -e $output_path ]]; then
    echo "'$output_path' already exists.  Press [Enter] to overwrite..."
    read
fi

cp $design_positions $output_path
$repack_shell_app                                                           \
    -in:file:s '../../structures/wt_lig_dimer.pdb'                          \
    -in:file:extra_res_fa '../../ligand/EQU.fa.params'                      \
    -in:file:extra_res_cen '../../ligand/EQU.cen.params'                    \
    -packing:resfile $output_path
