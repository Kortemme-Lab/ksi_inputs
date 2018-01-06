#!/usr/bin/env python3

"""\
Modify an existing loops file to adapt it to a structure with a different 
loop length.

Usage:
    change_loop_length.py <loops> <modification> [options]

Arguments:
    <loops>
        The path to a resfile for the wildtype loop length.

    <modification>
        The change being made to the loop length.  Deletions should be 
        expressed as "del<number of residues to delete>", e.g. "del1" or "del2" 
        for deletions of 1 or 2 residues, respectively.  Insertions should 
        likewise be expressed as "ins<number of residues to insert>".

Options:
    -o --output-file <path>
        The path where the modified resfile should be written.  The default is 
        "<loops>_<modification>.loops".

Note:  It is assumed that any insertions or deletions are made immediately 
after residue 38.  If this is ever not the case, this script may need to be 
rewritten.
"""

import docopt, re
from pathlib import Path
from pprint import pprint
args = docopt.docopt(__doc__)

# Read the resfile.
loops_path = Path(args['<loops>'])
with loops_path.open() as file:
    lines = file.readlines()

# Determine how many residues to insert/delete.
mod = args['<modification>']
action, count = mod[:3], mod[3:]
count = int(count)

if action not in ('ins', 'del'):
    raise ValueError(f"<modification> must start with 'ins' or 'del', not '{action}'.")

# Update the resfile.
fixed_lines = []

def update(resi_str):
    x = update_resi(int(resi_str))
    num_digits = len(resi_str)
    return f'{x:{num_digits}d}'

def update_resi(resi):
    if resi < 38:
        return resi

    if action == 'ins':
        return resi + count

    if action == 'del':
        if resi - count <= 38:
            raise ValueError(f"can't delete {count} residues: {resi} - {count} <= 38")
        return resi - count


for line in lines:
    match = re.match(r'LOOP (\s*\d+) (\s*\d+) (\s*\d+) (.*)', line)

    if match:
        start, stop, cut, remainder = match.groups()
        line = f'LOOP {update(start)} {update(stop)} {update(cut)} {remainder}\n'

    fixed_lines.append(line)

# Write the fixed resfile.
default_path = loops_path.parent / f'{loops_path.name}_{mod}'
fixed_path = Path(args['--output-file'] or default_path)

with fixed_path.open('w') as file:
    file.writelines(fixed_lines)
