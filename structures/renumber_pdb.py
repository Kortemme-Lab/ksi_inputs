#!/usr/bin/env python3

""" 
Rewrite the given PDB file with residue numbers counting consecutively up from 
1.

Usage:
    ./renumber-pdb.py <path>
"""

import docopt

if __name__ == '__main__':
    arguments = docopt.docopt(__doc__)
    path = arguments['<path>']

    with open(path) as file:
        pdb_in = file.readlines()

    pdb_out = []
    atom_id = 0
    residue_id = 0
    last_residue = 0

    for line_in in pdb_in:
        if line_in.startswith('ATOM') or line_in.startswith('HETATM'):
            atom_id += 1
            current_residue = int(line_in[23:26])

            if current_residue != last_residue:
                residue_id +=1
                last_residue = current_residue
            
            line_out = line_in[:7]
            line_out += '{:4d}'.format(atom_id)
            line_out += line_in[11:23]
            line_out += '{:3d}'.format(residue_id)
            line_out += line_in[26:]

            pdb_out.append(line_out)

        else:
            pdb_out.append(line_in)


    with open(path, 'w') as file:
        file.writelines(pdb_out)
