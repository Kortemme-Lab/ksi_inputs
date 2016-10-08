#!/usr/bin/env sh

pdb=1qjg
make_symmetry_file='../../../../../public/symmetry/make_symmdef_file.pl'
$make_symmetry_file -m NCS -p "$pdb.pdb" -a A -i B > "$pdb.symm"
