"""\
In this test we get a directory of files with different permissions, owners,
hardlinks, symlinks and duplicates. We then add it to a store and generate a
browsable copied directory of it. We then run rsync in archive mode with
``--dry-run`` and expect no output.

The size of the store should be less than the size of the original files.

On the command line:

::

    . path/to/pyenv/bin/env/activate
    rm -r dst/* dst1/* first second output; python test.py

It has to be run from the ``test`` directory because one of the tests uses
a relative path that includes the ``test directory.

It has to be run from a terminal with an activated Python environment with
``BuildKit`` and ``Archiver`` installed because the tests execute each time
from the command line as a different process.

You need the ``rsync`` command installed for the tests to run.
"""

import sys
import os
import logging
from buildkit import run

# First add the files via the command line:
cmd = [sys.executable, '-m', 'archiver.command', '-s', 'first', 'add', '--extras-function', 'archiver.test:extras_b','src/', 'FIRST']
print ' '.join(cmd)
res = run(cmd, echo_stdout=True, echo_stderr=True)
if "failure" in res[1]:
    raise Exception('Adding files failed')

# Then add similar files again via the command line from a different source:
cmd = [sys.executable, '-m', 'archiver.command', '-s', 'second', 'add', '--extras-function', 'archiver.test:extras_d', 'src1/', 'SECOND']
print ' '.join(cmd)
res = run(cmd, echo_stdout=True, echo_stderr=True)
if "failure" in res[1]:
    raise Exception('Adding files failed')

# Check the extras have been updated
cmd = [sys.executable, '-m', 'archiver.command', '-s', 'second', 'extras', 'show', 'SECOND', 'all/d/d1.png']
print ' '.join(cmd)
res = run(cmd, echo_stdout=True, echo_stderr=True)
if not "owner: d" in res[1]:
    raise Exception('Extras failed to include the line "owner: phil"')

# Now update the second source with new extras
cmd = [sys.executable, '-m', 'archiver.command', '-s', 'second', 'extras', 'update', 'archiver.test:extras_d_cap', 'SECOND', 'src1']
print ' '.join(cmd)
res = run(cmd, echo_stdout=True, echo_stderr=True)

# Now test a file to see if the extras have been added properly
cmd = [sys.executable, '-m', 'archiver.command', '-s', 'second', 'extras', 'show', 'SECOND', 'all/d/d1.png']
print ' '.join(cmd)
res = run(cmd, echo_stdout=True, echo_stderr=True)
if not "owner: D" in res[1]:
    raise Exception('Extras failed to update the line "owner: Phil"')

# Then generate a directory
cmd = [sys.executable, '-m', 'archiver.command', '-s', 'first', 'restore', 'dst']
print ' '.join(cmd)
res = run(cmd, echo_stdout=True, echo_stderr=True)

# Finally check the generated directory is the same as the source
cmd = ['rsync', '-aHxv', '--dry-run', '--stats', '--numeric-ids', 'src/', 'dst/FIRST/']
print ' '.join(cmd)
res = run(cmd, echo_stdout=True, echo_stderr=True)
if 'Number of files transferred: 0\n' not in res[1]:
    raise Exception('Test failed: had to copy files between the source and restore')
if not os.path.islink('dst/FIRST/all/a1.png'):
    raise Exception('Test failed: symlink file not present at end')
if not os.path.islink('dst/FIRST/a/b'):
    raise Exception('Test failed: symlink dir not present at end')
assert ('a/a1.png', '../b') == (os.readlink('dst/FIRST/all/a1.png'), os.readlink('dst/FIRST/a/b'))

# Now generate the second browse directory in ths same directory as the first (since the sources are different it won't overwrite)
cmd = [sys.executable, '-m', 'archiver.command', '-s', 'second', 'restore', 'dst']
print ' '.join(cmd)
res = run(cmd, echo_stdout=True, echo_stderr=True)
# Now we merge the two stores:
cmd = [sys.executable, '-m', 'archiver.command', '-v', 'merge', 'output', '../test/first/', 'second/']
print ' '.join(cmd)
res = run(cmd, echo_stdout=True, echo_stderr=True)
# Create a browse structure from the merged store
cmd = [sys.executable, '-m', 'archiver.command', '-s', 'output', 'restore', 'dst1']
print ' '.join(cmd)
res = run(cmd, echo_stdout=True, echo_stderr=True)
# Finally compare the browse structure generated from the two sources, with the one generated from the merged copy
cmd = ['rsync', '-aHxv', '--dry-run', '--stats', '--numeric-ids', 'dst/FIRST/', 'dst1/FIRST/']
print ' '.join(cmd)
res = run(cmd, echo_stdout=True, echo_stderr=True)
if 'Number of files transferred: 0\n' not in res[1]:
    raise Exception('Test failed: had to copy files for the merged FIRST')
cmd = ['rsync', '-aHxv', '--dry-run', '--stats', '--numeric-ids', 'dst/SECOND/', 'dst1/SECOND/']
print ' '.join(cmd)
res = run(cmd, echo_stdout=True, echo_stderr=True)
if 'Number of files transferred: 0\n' not in res[1]:
    raise Exception('Test failed: had to copy files for the merged SECOND')

