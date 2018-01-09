#!/usr/bin/env python3

"""\
Modify an existing resfile to make it usable for a structure with a different 
loop length.

Usage:
    change_loop_length.py <resfile> <modification> [options]

Arguments:
    <resfile>
        The path to a resfile for the wildtype loop length.

    <modification>
        The change being made to the loop length.  Deletions should be 
        expressed as "del<number of residues to delete>", e.g. "del1" or "del2" 
        for deletions of 1 or 2 residues, respectively.  Insertions should 
        likewise be expressed as "ins<number of residues to insert>".

Options:
    -o --output-file <path>
        The path where the modified resfile should be written.  The default is 
        "<resfile>_<modification>".

    -v --verbose
        Print extra information to help you be sure your resfile is being 
        modified correctly.

Note:  It is assumed that any insertions or deletions are made immediately 
after residue 38, and that any insertions will use the same design rules as 
residue 39.  If this is ever not the case, this script will need to be 
rewritten.
"""

import docopt, re
from pprint import pprint
args = docopt.docopt(__doc__)
VERBOSE = args['--verbose']

# Read the resfile.
with open(args['<resfile>']) as file:
    lines = file.readlines()

# Determine how many residues to insert/delete.
mod = args['<modification>']
action, count = mod[:3], mod[3:]
count = int(count)

if action not in ('ins', 'del'):
    raise ValueError(f"<modification> must start with 'ins' or 'del', not '{action}'.")

# Update the resfile.
fixed_lines = []

def fix_line(line):
    """
    Given a line from the original resfile, return the line (or lines) that 
    should appear in the fixed resfile.  The return value may be either a 
    single string (which will be interpreted as one line) or a list of strings 
    (which will be interpreted as a [possibly empty] group of lines).
    """
    if line.startswith('#'):
        return fix_comment(line)

    match = re.match(r'(\d+)(\s+.*)', line)
    if not match:
        return line

    resi = int(match.group(1))
    task = match.group(2) + '\n'

    if action == 'ins':
        if resi <= 38:
            return line
        elif resi == 39:
            return [line] + [
                    change_resi(39, 39 + j + 1, task, 'Adding')
                    for j in range(count)
            ]
        else:
            return change_resi(resi, resi + count, task)

    if action == 'del':
        if resi <= 38:
            return line
        elif resi - count <= 38:
            if VERBOSE:
                print(f'Removing residue:    {resi:3d}')
            return []
        else:
            return change_resi(resi, resi - count, task)

def fix_comment(line):
    fix = lambda m: str(fix_number(int(m.group())))
    return re.sub('\d+', fix, line)

def fix_number(resi):
    if resi <= 38:
        return resi
    if action == 'ins':
        return resi + count
    if action == 'del':
        return resi - count

def change_resi(old_resi, new_resi, task, verb='Renumbering'):
    if VERBOSE:
        print(f'{verb + " residue:":<20s} {old_resi:3d} → {new_resi:3d}')

    d = len(str(new_resi)) - len(str(old_resi))
    if d > 0: task = task[d:]      # More digits: remove spaces
    if d < 0: task = d*' ' + task  # Fewer digits: add spaces
    return str(new_resi) + task


for line in lines:
    fix = fix_line(line)

    if isinstance(fix, str):
        fixed_lines.append(fix)
    elif isinstance(fix, list):
        fixed_lines.extend(fix)
    else:
        raise ValueError(f'fix_line() must return either str or list, not {type(fix)}.')

# Write the fixed resfile.
fixed_path = args['--output-file'] or f'{args["<resfile>"]}_{mod}'

with open(fixed_path, 'w') as file:
    file.writelines(fixed_lines)
