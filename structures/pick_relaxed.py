#!/usr/bin/env python3

from pathlib import Path

def score_pdb(path):
    with open(path) as file:
        lines = file.readlines()

    for line in lines:
        if line.startswith('label'):
            fields = line.split()
            total_i = fields.index('total')
            try: cst_i = fields.index('coordinate_constraint')
            except ValueError: cst_i = None

        if line.startswith('pose'):
            fields = line.split()
            total = float(fields[total_i])
            try: cst = float(fields[cst_i])
            except TypeError: cst = 0

            return total - cst

def find_best_pdb(dir):
    scores = {
            pdb: score_pdb(pdb)
            for pdb in Path(dir).glob('*.pdb')
    }
    return sorted(scores.items(), key=lambda x: x[1])[0]

def pick_best_pdb(dir):
    if not list(Path(dir).glob('*.pdb')):
        print(f"No PDBs in {dir}")
        return

    pdb, score = find_best_pdb(dir)
    pick = Path(f'{dir}.pdb')
    if pick.exists(): pick.unlink()
    pick.symlink_to(pdb)

    print(f"Picked {pdb} ({score} REU)")


if __name__ == '__main__':
    pick_best_pdb('1qjg_clean_relax')




