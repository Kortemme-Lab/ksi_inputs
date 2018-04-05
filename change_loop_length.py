#!/usr/bin/env python3

"""\
Create input files for different loop lengths from input files made by hand for 
the wildtype loop length.

Usage:
    change_loop_length.py <path> <delta>

Arguments:
    <delta>
        The change being made to the loop length.  Deletions should be 
        expressed as "del<number of residues to delete>", e.g. "del1" or "del2" 
        for deletions of 1 or 2 residues, respectively.  Insertions should 
        likewise be expressed as "ins<number of residues to insert>".

    <path>
        A file or directory with input parameters based on the wildtype 
        sequence length.

The typical way to use this script is on a directory of manually created input 
files:

    $ ./change_loop_length.py 20180219_res16_loop12_lhkic del1
"""

import re
import docopt
import shutil
from pathlib import Path
from fnmatch import fnmatch
from contextlib import contextmanager
from subprocess import run, PIPE
from textwrap import indent

FIXERS = []

class Delta:
    """
    The number of residues to insert or delete.
    """
    
    def __init__(self, site, delta):
        self.site = site
        self.name = delta
        self.action = delta[:3]
        if self.action not in ('ins', 'del'):
            raise ValueError(f"<delta> must start with 'ins' or 'del', not '{delta}'.")

        try:
            self.count = int(delta[3:])
        except ValueError:
            raise ValueError(f"<delta> must end with an integer, not '{delta}'.")

    def __str__(self):
        return f'<{self.action}{self.count}>'

    def fix_resi(self, resi):
        if resi <= self.site:
            return resi
        if self.action == 'ins':
            return resi + self.count
        if self.action == 'del':
            if resi - self.count <= self.site:
                raise ValueError(f"can't delete {self.count} residues: {resi} - {self.count} <= {self.site}")
            return resi - self.count

    def fix_dir(self, dir):
        dir = Path(dir)
        return dir.parent / f'{dir.name}_{self.action}{self.count}'

    def fix_path(self, dir, path):
        return self.fix_dir(dir) / path

    @property
    def is_insertion(self):
        return self.action == 'ins'

    @property
    def is_deletion(self):
        return self.action == 'del'


class Fixer:
    """
    Base class for algorithms that update a particular kind of input file to 
    the new loop length.

    The `fix()` method is the public interface for converting files.  It takes 
    the path to the original file, the path to the derivative file to create, 
    and the number of residues to insert or delete.  
    
    By default, `fix()` iterates through the input file line-by-line and calls 
    `fix_line()` to determine how to update each line.  `fix_line()` can either 
    return a string (to replace a line) or a list of strings (to insert or
    remove lines).
    """
    paths = []

    def __init_subclass__(cls):
        FIXERS.append(cls)

    def __str__(self):
        return self.__class__.__name__

    def fix(self, src, dest, delta):
        # Read the original file.

        with open(src) as file:
            lines = file.readlines()

        # Update each line one at a time.

        fixed_lines = []

        for line in lines:
            fix = self.fix_line(delta, line)

            if isinstance(fix, str):
                fixed_lines.append(fix)
            elif isinstance(fix, list):
                fixed_lines.extend(fix)
            else:
                raise ValueError(f'{f} must return either str or list, not {type(fix)}.')

        # Write the resulting file.

        with mkdir_and_open(dest) as file:
            file.writelines(fixed_lines)

        shutil.copymode(src, dest)

    def fix_line(self, delta, line):
        """
        Given a line from the original file, return the line (or lines) that 
        should appear in the fixed resfile.  The return value may be either a 
        string (which will be interpreted as one line) or a list of strings 
        (which will be interpreted as a [possibly empty] group of lines).
        """
        raise NotImplementedError

    def diff(self, src, dest):
        cmd = 'diff', src, dest, '--color=always'
        diff = run(cmd, stdout=PIPE).stdout.decode()
        print(indent(diff, '  '))


class PatternFixer(Fixer):
    """
    Search files for any of the regular expressions given in `patterns`, then 
    fix any numbers in any of the capturing groups in any of the matches.
    
    Put another way, `patterns` should be a list of regular expressions that 
    match parts of the file that may need to be updated.  Only the parts of the 
    pattern that are contained in capturing groups (i.e. parentheses) will 
    actually be updated, so it's possible to have patterns that encompass 
    numbers that both should and shouldn't be updated.  The text in the 
    capturing groups is searched for numbers, so it's completely fine to have 
    groups that encompass a mix of text and numbers and/or multiple distinct 
    numbers to update.
    """
    patterns = []
    skip = ['[Uu]naffected by loop length']
    keep_alignment = True
    keep_one_space = False

    def fix_line(self, delta, line):
        # If a line contains any of the "skip" patterns, return in unchanged.
        for pattern in self.skip:
            if re.search(pattern, line):
                return line
            
        for pattern in self.patterns:
            # Iterate from right-to-left so our indexing doesn't get messed up 
            # as we update the line.
            matches = list(re.finditer(pattern, line))
            for match in reversed(matches):
                if not match:
                    continue

                # Ditto the right-to-left thing.
                num_groups = len(match.groups())
                for i in reversed(range(1, num_groups+1)):
                    if not match.group(i):
                        continue

                    before = line[:match.start(i)]
                    after = line[match.end(i):]
                    content = line[match.start(i):match.end(i)]

                    fixed_content = fix_all_numbers(
                            delta,
                            content,
                            self.keep_alignment,
                            self.keep_one_space,
                    )
                    line = before + fixed_content + after

        return line


class PdbFixer(Fixer):
    """
    Insert or remove residues from PDB files as necessary.

    The algorithm is to iterate through to file residue by residue (a little 
    complicated because each residue spans multiple lines) and to either delete 
    or duplicate the residues after the site indicated by the delta, which for 
    KSI is 38.
    """
    paths = '*.pdb', '*.pdb.gz'

    class IdCounter:

        def __init__(self):
            self.atom = 1
            self.residue = 1


    class Residue:

        def __init__(self, id_counter, resi):
            self.lines = []
            self.resi = resi
            self.id_counter = id_counter
            self.fix_called = False

        def add_atom(self, line):
            self.lines.append(line)

        def fix(self, delta):
            # This algorithm won't produce correct output if this function is 
            # ever called more than once on the same residue.  It's actually 
            # not hard to think of input that would trigger this condition 
            # (e.g. literally any non-atom line in the middle of a residue), 
            # but such input should not occur (fingers crossed) and handling it 
            # would make this code a lot more complex.
            assert not self.fix_called
            self.fix_called = True

            residues = self.insert_or_delete_residues(delta)
            fixed_lines = self.renumber_residues(residues)

            return fixed_lines

        def insert_or_delete_residues(self, delta):
            if delta.is_insertion:
                if self.resi == delta.site + 1:
                    return [self.lines] * (delta.count + 1)
                else:
                    return [self.lines]

            if delta.is_deletion:
                if delta.site < self.resi <= delta.site + delta.count:
                    return []
                else:
                    return [self.lines]

        def renumber_residues(self, residues):
            fixed_lines = []

            for residue in filter(lambda x: x, residues):
                for atom in residue:
                    fixed_atom = atom[:7]
                    fixed_atom += '{:4d}'.format(self.id_counter.atom)
                    fixed_atom += atom[11:23]
                    fixed_atom += '{:3d}'.format(self.id_counter.residue)
                    fixed_atom += atom[26:]
                    fixed_lines.append(fixed_atom)

                    self.id_counter.atom += 1
                self.id_counter.residue += 1

            return fixed_lines


    def fix(self, src, dest, delta):
        # Read the original file.

        import gzip, builtins
        if src.suffix == '.gz':
            open = gzip.open
        else:
            open = builtins.open

        with open(src, 'rt') as file:  # 'rt' forces the file to be opened
            lines = file.readlines()   # in text mode.

        # Insert or remove residues from the file as necessary, then renumber 
        # all the atoms to account for the change in length.

        fixed_lines = []
        residue_lines = []
        id_counter = self.IdCounter()
        residue = self.Residue(id_counter, 1)
        resi = 0

        def is_atom(line): #
            return line.startswith('ATOM') or line.startswith('HETATM')

        for line in lines:
            if not is_atom(line):
                fixed_lines += residue.fix(delta)
                residue = self.Residue(id_counter, -1)
                fixed_lines.append(line)

            else:
                resi = int(line[23:26])

                if resi != residue.resi:
                    fixed_lines += residue.fix(delta)
                    residue = self.Residue(id_counter, resi)

                residue.add_atom(line)
            
        if not residue.fix_called:
            fixed_lines += residue.fix(delta)

        # Write the resulting file.

        dest.parent.mkdir(parents=True, exist_ok=True)
        with open(dest, 'wt') as file:
            file.writelines(fixed_lines)


class ResfileFixer(Fixer):
    paths = 'resfile', '*.resfile'

    def fix_line(self, delta, line):
        if line.startswith('#'):
            return fix_all_numbers(delta, line)

        match = re.match(r'(\d+)(\s+)(.*)', line)
        if not match:
            return line

        resi = int(match.group(1))
        space = match.group(2)
        task = match.group(3) + '\n'

        if delta.is_insertion:
            if resi <= delta.site:
                return line
            elif resi == delta.site + 1:
                return [line] + [
                        self.add_task(
                            delta.site + 1,
                            delta.site + j + 2,
                            task, space)
                        for j in range(delta.count)
                ]
            else:
                return self.fix_task(delta, resi, task, space)

        if delta.is_deletion:
            if resi <= delta.site:
                return line
            elif resi - delta.count <= delta.site:
                return self.remove_task(resi)
            else:
                return self.fix_task(delta, resi, task, space)

    def add_task(self, old_resi, new_resi, task, space=' '):
        return self._make_task(old_resi, new_resi, task, space)

    def fix_task(self, delta, resi, task, space=' '):
        return self._make_task(resi, delta.fix_resi(resi), task, space)

    def remove_task(self, resi):
        return []

    def _make_task(self, old_resi, new_resi, task, space):
        d = len(str(new_resi)) - len(str(old_resi))
        if d > 0: space = space[d:]  # More digits: remove spaces
        if d < 0: space += d*' '     # Fewer digits: add spaces

        return str(new_resi) + (space or ' ') + task


class XmlFixer(PatternFixer):
    paths = '*.xml',
    patterns = [
            r'resnums?="(.*?)"',
            r'start_res="(.*?)"',
            r'end_res="(.*?)"',
            r'residue="(.*?)"',
            r'<Span (.*?)/>',
    ]

class RestraintsFixer(PatternFixer):
    paths = 'restraints', '*.restraints'

    # The ".+?" bits match atom names (e.g. CA), and the "(\s*\d+)" bits match 
    # the residue indices to update.
    patterns = [
            r'^CoordinateConstraint .+? (\s*\d+)',
            r'^AtomPair .+? (\s*\d+) .+? (\s*\d+)',
            r'^Angle .+? (\s*\d+) .+? (\s*\d+) .+? (\s*\d+)',
            r'^Dihedral .+? (\s*\d+) .+? (\s*\d+) .+? (\s*\d+) .+? (\s*\d+)',
    ]

class FoldtreeFixer(PatternFixer):
    paths = 'foldtree', '*.foldtree'

    # End the pattern after the two residue indices, so we leave the jump 
    # number alone.
    patterns = r'EDGE (\s*\d+) (\s*\d+)',

class LoopsFixer(PatternFixer):
    paths = 'loops', '*.loops'

    # End the pattern after the three residue indices, so we leave everything 
    # else alone.
    patterns = r'^LOOP (\s*\d+) (\s*\d+) (\s*\d+)',

class PymolFixer(PatternFixer):
    paths = '*.sho',

    # These files are arbitrary scripts, so there's no way to know exactly 
    # which numbers we should or shouldn't change.  But we know at least that 
    # we should update any arguments to `resi`, which is used to select 
    # residues by index in pymol.
    patterns = r'resi (.*?)[\'",]',

class TextFixer(Fixer):
    paths = '*.txt', '*.rst', '*.md'

    def fix_line(self, delta, line):
        return fix_all_numbers(delta, line)


class CopyUnchanged(Fixer):
    paths = '*'

    def fix(self, src, dest, delta):
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dest)
        shutil.copymode(src, dest)



def fix_directory(dir, delta):
    sort_by = lambda x: (x.suffix, x.name)

    for src in sorted(dir.glob('**/*'), key=sort_by):
        if src.is_dir():
            continue

        path = src.relative_to(dir)
        dest = delta.fix_path(dir, path)

        # Don't copy hidden files.
        if src.name.startswith('.'):
            continue

        fix_file(src, dest, delta)

def fix_file(src, dest, delta):
    from subprocess import run, PIPE

    print('Source:', src)
    print('Destination:', dest)

    fixer = fixer_from_path(src)

    print('Fixer:', fixer)
    print()

    fixer.fix(src, dest, delta)
    fixer.diff(src, dest)

    print()

def fixer_from_path(path):
    for fixer in FIXERS:
        for glob in fixer.paths:
            if fnmatch(path.name, glob):
                return fixer()

def fixer_from_name(name):
    for fixer in FIXERS:
        if name.lower in fixer.__name__:
            return fixer()

def fix_all_numbers(delta, line, keep_alignment=False, keep_one_space=True):

    def fix(match): #
        old_resi_str = match.group()
        old_resi = int(old_resi_str)
        new_resi = delta.fix_resi(old_resi)
        new_resi_str = f'{new_resi:{len(old_resi_str)}d}'
        space = match.group(1)

        if not keep_alignment:
            return space + str(new_resi)

        # If there is leading space, don't get rid of it completely, since that 
        # could change the meaning of the line.
        if keep_one_space and space and new_resi_str[0] != ' ':
            new_resi_str = ' ' + new_resi_str

        return new_resi_str

    return re.sub(r'(\s*)\d+', fix, line)

@contextmanager
def mkdir_and_open(path, mode='w'):
    if 'w' in mode:
        path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, mode) as file:
        yield file


if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    path = Path(args['<path>'])
    delta = Delta(39, args['<delta>'])

    if path.is_dir():
        shutil.rmtree(delta.fix_dir(path), ignore_errors=True)
        fix_directory(path, delta)
    else:
        stem, suffix = path.name.split('.', 1)
        dest = path.parent / f'{stem}_{delta.name}.{suffix}'
        fix_file(path, dest, delta)
