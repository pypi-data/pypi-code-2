# -*- encoding: utf8 -*-
"""\
In this test we get a directory of files with different permissions, owners,
hardlinks, symlinks and duplicates. We then add it to a store and generate a
browsable copied directory of it. We then run rsync in archive mode with
``--dry-run`` and expect no output.

The size of the store should be less than the size of the original files.

On the command line:

::

    . path/to/pyenv/bin/env/activate
    rm -r dst/* dst1/* src1 first first_hardlink second output; mkdir src1; cp -pr src/* src1/; rm -r src1/link_src; python test_all.py

It has to be run from the ``test`` directory because one of the tests uses
a relative path that includes the ``test directory.

It has to be run from a terminal with an activated Python environment with
``BuildKit`` and ``Archiver`` installed because the tests execute each time
from the command line as a different process.

You need the ``rsync`` command installed for the tests to run.
"""

from __future__ import unicode_literals
import sys
import os
import logging
from buildkit import run as run_external
import StringIO
from archiver.command import Archiver

cmd = Archiver()
def run(cmd, cmd_args):
    print 'Running: %s'%(' '.join(cmd_args))
    lines = []
    def out(string, *args, **opts):
        if opts.get('end') is None:
            end = '\n'
        else:
            end = opts.get('end')
        try:
            res = (string+u'\n') % args
        except Exception, e:
            raise Exception('Could not print this string: %r with these args: %s. The original error was %r'%(string, args, e))
        print res
        lines.append(res)
    def err(string, *args, **p):
        out(string, *args, **p)
    def exit(code):
        print "Exiting with %r"%code
    result = cmd.handle_command_line(cmd_args, program='python -m archiver.command', out=out, err=err, exit=exit)
    if result:
        raise Exception(result)
    return result, ''.join(lines)

# First add the files from the src directory to the first store (via the command line):
res = run(cmd, ['-s', 'first', 'add', '--extras-function', 'archiver.test:extras_b', 'src/', 'FIRST'])
if "failure" in res[1]:
    raise Exception('Adding files failed')
# Same as before, but using hardlinks
res = run(cmd, ['-s', 'first_hardlink', 'add', '--extras-function', 'archiver.test:extras_b', '--hardlink', 'src/', 'FIRST_HARDLINK'])
if "failure" in res[1]:
    raise Exception('Adding files failed')
# Then restore a directory with the FIRST and FIRST_HARDLINK sources
res = run(cmd, ['-s', 'first', '-v', 'restore', '-m', 'dst'])
res = run(cmd, ['-s', 'first_hardlink', 'restore', '-m', 'dst'])
# And check they are the same
cmd_args = ['rsync', '-aHxv', '--progress',  '--stats', '--numeric-ids', 'dst/FIRST/', 'dst/FIRST_HARDLINK']
print ' '.join(cmd_args)
res = run_external(cmd_args, echo_stdout=True, echo_stderr=True)
if 'Number of files transferred: 0\n' not in unicode(res[1].decode('utf8')):
    raise Exception('Test failed: had to copy files between the two types of restored store')
cmd_args = ['rsync', '-aHxv', '--progress',  '--stats', '--numeric-ids', '--dry-run', 'src/', 'dst/FIRST']
print ' '.join(cmd_args)
res = run_external(cmd_args, echo_stdout=True, echo_stderr=True)
if 'Number of files transferred: 0\n' not in unicode(res[1].decode('utf8')):
    raise Exception('Test failed: had to copy files between src and dst/FIRST')
# Finally, check that updating the source doesn't result in any files changing:
res = run(cmd, ['-s', 'first_hardlink', 'update', '--hardlink', 'dst/FIRST_HARDLINK/', 'FIRST_HARDLINK'])
res = run(cmd, ['-s', 'first', 'update', '--hardlink', '--ignore-new-symlink-times', 'dst/FIRST', 'FIRST'])
assert """ files:                  19
               stored successfully: 0
               storage failed:      0
               metadata added:      0
               metadata replaced:   0
            dirs:                   12
               metadata added:      0
               metadata replaced:   2""" in res[1]
# Then add similar files again via the command line from a different source (the link_src directory is the same):
res = run(cmd, ['-s', 'second', 'add', '--extras-function', 'archiver.test:extras_d', 'src1/', 'SECOND'])
if "failure" in res[1]:
    raise Exception('Adding files failed')
# Check the extras have been updated
res = run(cmd, ['-s', 'second', 'extras', 'show', 'SECOND', 'all/d/d1.png'])
if not "owner: d" in res[1]:
    raise Exception('Extras failed to include the line "owner: d"')
# Now update the second source with new extras
res = run(cmd, ['-s', 'second', 'extras', 'update', 'archiver.test:extras_d_cap', 'SECOND', 'src1'])
# Now test a file to see if the extras have been added properly
res = run(cmd, ['-s', 'second', 'extras', 'show', 'SECOND', 'all/d/d1.png'])
if not "owner: D" in res[1]:
    raise Exception('Extras failed to update the line "owner: D"')
# Check the generated FIRST directory is the same as the src directory it came from
cmd_args = ['rsync', '-aHxv', '--progress',  '--stats', '--numeric-ids', 'src/', 'dst/FIRST/']
print ' '.join(cmd_args)
res = run_external(cmd_args, echo_stdout=True, echo_stderr=True)
if 'Number of files transferred: 0\n' not in unicode(res[1].decode('utf8')):
    raise Exception('Test failed: had to copy files between the source and restore')
if not os.path.islink('dst/FIRST/all/a1.png'):
    raise Exception('Test failed: symlink file not present at end')
if not os.path.islink('dst/FIRST/a/b'):
    raise Exception('Test failed: symlink dir not present at end')
assert ('a/a1.png', '../b') == (os.readlink('dst/FIRST/all/a1.png'), os.readlink('dst/FIRST/a/b'))
# Check the generated SECOND directory is the same as the src1 directory it came from
# Then restore a directory with the FIRST directory
res = run(cmd, ['-s', 'second', 'restore', '-m', 'dst1'])
# Try rinning it again
res = run(cmd, ['-s', 'second', 'restore', '-m', 'dst1'])
if res[1] != u"Restoring u'SECOND' to u'dst1'\nDone.\n":
    raise Exception(res[1])
cmd_args = ['diff', '-ru', 'src1/', 'dst1/SECOND/']
print ' '.join(cmd_args)
res = run_external(cmd_args, echo_stdout=True, echo_stderr=True)
if unicode(res[1].decode('utf8')):
    raise Exception(res[1])
cmd_args = ['rsync', '-aHxv', '--progress',  '--stats', '--numeric-ids', 'src1/', 'dst1/SECOND/']
print ' '.join(cmd_args)
res = run_external(cmd_args, echo_stdout=True, echo_stderr=True)
if 'Number of files transferred: 0\n' not in unicode(res[1].decode('utf8')):
    raise Exception('Test failed: had to copy files between the source and restore')
if not os.path.islink('dst1/SECOND/all/a1.png'):
    raise Exception('Test failed: symlink file not present at end')
if not os.path.islink('dst1/SECOND/a/b'):
    raise Exception('Test failed: symlink dir not present at end')
assert ('a/a1.png', '../b') == (os.readlink('dst1/SECOND/all/a1.png'), os.readlink('dst1/SECOND/a/b'))
# Now generate the second browse directory in ths same directory as the first (since the sources are different it won't overwrite)
res = run(cmd, ['-s', 'second', 'restore', '-m', 'dst'])
# Now we merge the two stores:
res = run(cmd, ['-v', 'merge', 'output', '../test/first/', 'second/'])
# Create a browse structure from the merged store
res = run(cmd, ['-s', 'output', 'restore', '-m', 'dst1'])
# Finally compare the browse structure generated from the two sources, with the one generated from the merged copy
cmd_args = ['rsync', '-aHxv', '--progress', '--stats', '--numeric-ids', 'dst/FIRST/', 'dst1/FIRST/']
print ' '.join(cmd_args)
res = run_external(cmd_args, echo_stdout=True, echo_stderr=True)
if 'Number of files transferred: 0\n' not in unicode(res[1].decode('utf8')):
    raise Exception('Test failed: had to copy files for the merged FIRST')
cmd_args = ['rsync', '-aHxv', '--progress', '--stats', '--numeric-ids', 'dst/SECOND/', 'dst1/SECOND/']
print ' '.join(cmd_args)
res = run_external(cmd_args, echo_stdout=True, echo_stderr=True)
if 'Number of files transferred: 0\n' not in unicode(res[1].decode('utf8')):
    raise Exception('Test failed: had to copy files for the merged SECOND')
## Check that we always get Unicode return values
#print os.path.exists('src/')
#for root, dirs, files in os.walk(u'src/'):
#    for directory in dirs:  
#        print root, directory, type(directory)
#    for filename in files:
#        print root, filename
#print "Done."
#from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, DateTime, Enum, select, and_, create_engine
#from archiver.api import make_batch, file_records
#db = 'sqlite:///first/paths.db'
#raw_engine = create_engine(db)
#for row in raw_engine.execute('''
#    SELECT 
#        *
#    FROM file
#'''):
#    print row, row[0]
#for row in raw_engine.execute('''
#    SELECT 
#        path, link
#    FROM directory
#'''):
#    print row, row[0]
# 
# sa_engine = make_batch('first')
# files = sa_engine.metadata.connection.execute(
#     select([file_records])
# )
# for row in files:
#     print (row.path,), row.path
# 

