#!/usr/bin/env python

"""
make a self-extracting virtualenv from directories or URLs
of packages

To package up all files in a virtualenvs source directory (e.g.):

python path/to/carton.py mozmill mozmill/src/*

This will create a self-extracting file, `mozmill.py`, that will unfold
a virtualenv
"""

# imports
import os
import sys
import tarfile
import tempfile
import urllib2
from optparse import OptionParser
from StringIO import StringIO

# global variables
usage = "%prog [options] environment_name directory|url [...]"
virtualenv_url = 'http://pypi.python.org/packages/source/v/virtualenv/virtualenv-1.6.1.tar.gz'
template = """#!/usr/bin/env python

"create a virtualenv at %(ENV)s"

import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
from optparse import OptionParser
from StringIO import StringIO

try:
    call = subprocess.check_call
except AttributeError:
    # old python; boo :(
    call = subprocess.call

# virtualenv name
ENV='''%(ENV)s'''

# packed files
VIRTUAL_ENV='''%(VIRTUAL_ENV)s'''.decode('base64').decode('zlib')
PACKAGE_SOURCES=%(PACKAGE_SOURCES)s

# parse options
usage = os.path.basename(sys.argv[0]) + ' [options]'
parser = OptionParser(usage=usage, description=__doc__)
parser.add_option('--env', dest='env', help="environment name [DEFAULT: " + ENV + "]")
options, args = parser.parse_args()
if options.env:
    ENV = options.env

# unpack virtualenv
tempdir = tempfile.mkdtemp()
buffer = StringIO()
buffer.write(VIRTUAL_ENV)
buffer.seek(0)
tf = tarfile.open(mode='r', fileobj=buffer)
tf.extractall(tempdir)

# find the virtualenv
for root, dirs, files in os.walk(tempdir):
    if 'virtualenv.py' in files:
        virtualenv = os.path.join(root, 'virtualenv.py')
        break
else:
    raise Exception("virtualenv.py not found in " + tempdir)
print virtualenv
        
# create the virtualenv
call([sys.executable, virtualenv, ENV])

# find the bin/scripts directory
for i in ('bin', 'Scripts'):
    scripts_dir = os.path.abspath(os.path.join(ENV, i))
    if os.path.exists(scripts_dir):
        break
else:
    raise Exception("Scripts directory not found in " + ENV)

# find the virtualenv's python
for i in ('python', 'python.exe'):
    python = os.path.join(scripts_dir, i)
    if os.path.exists(python):
        break
else:
    raise Exception("python not found in " + scripts_dir)

# unpack the sources and setup for development
srcdir = os.path.join(ENV, 'src')
os.mkdir(srcdir)
setup_pys = set()
for source in PACKAGE_SOURCES:
    source = source.decode('base64').decode('zlib')
    buffer = StringIO()
    buffer.write(source)
    buffer.seek(0)
    tf = tarfile.open(mode='r', fileobj=buffer)
    tf.extractall(srcdir)

    # setup sources for development if there are any new setup.py files
    # TODO: ideally this would figure out dependency order for you
    for i in os.listdir(srcdir):
        if i in setup_pys:
            continue
        subdir = os.path.join(srcdir, i)
        if os.path.exists(os.path.join(srcdir, i, 'setup.py')):
            call([python, 'setup.py', 'develop'], cwd=subdir)
            setup_pys.add(i)

# cleanup tempdir # TODO (optionally?)
# shutil.rmtree(tempdir)

# TODO:
# - add carton to the virtualenv (!)
# - add virtualenv to the virtualenv (!)
"""

def isURL(path):
    return path.startswith('http://') or path.startswith('https://')

def main(args=sys.argv[1:]):

    # parse CLI arguments
    parser = OptionParser(usage=usage, description=__doc__)
    parser.add_option('-o', dest='outfile',
                      help="specify outfile; otherwise it will come from environment_name")
    parser.add_option('--virtualenv', dest='virtualenv',
                      help="use this virtualenv URL or file tarball")
    options, args = parser.parse_args(args)
    if len(args) < 2:
        parser.print_usage()
        parser.exit()
    environment = args[0]
    if environment.endswith('.py'):
        # stop on .py; will add it in later
        environment = environment[:-3]
    sources = args[1:]

    # tar up the sources
    source_array = []
    for source in sources:
        buffer = None

        if isURL(source):
            # remote tarball or resource
            buffer = urllib2.urlopen(source).read()
        else:
            assert os.path.exists(source), "%s does not exist" % source
            
            # local directory or tarball
            if (not os.path.isdir(source)) and tarfile.is_tarfile(source):
                # check for a tarball
                buffer = file(source).read()
            else:
                source_buffer = StringIO()
                source_tar = tarfile.open(mode="w:gz", fileobj=source_buffer)
                source_tar.add(source, arcname=os.path.basename(source))
                source_tar.close()
                buffer = source_buffer.getvalue()

        # could use git, hg, etc repos. but probably shouldn't
        
        source_array.append(buffer.encode('zlib').encode('base64'))

    # tar up virtualenv if not available
    if options.virtualenv:
        if isURL(options.virtualenv):
            globals()['VIRTUAL_ENV'] = urllib2.urlopen(options.virtualenv).read()
        else:
            assert os.path.exists(options.virtualenv)
            if os.path.isdir(options.virtualenv):
                raise NotImplementedError("Hypothetically you should be able to use a local directory or tarball, but I haven't done this yet")
            else:
                # assert a tarfile
                assert tarfile.is_tarfile(options.virtualenv), "%s must be a tar file" % options.virtualenv
                globals()['VIRTUAL_ENV'] = file(options.virtualenv).read()
    else:
        globals()['VIRTUAL_ENV'] = urllib2.urlopen(virtualenv_url).read()
        # TODO: used the below hashed value of VIRTUAL_ENV if set
        # (set that with another file)

    # interpolate "template" -> output
    outfile = options.outfile
    if outfile is None:
        outfile = environment + '.py'
    variables = {'VIRTUAL_ENV': VIRTUAL_ENV.encode('zlib').encode('base64'),
                 'ENV': environment,
                 'PACKAGE_SOURCES': repr(source_array)}
    f = file(outfile, 'w')
    f.write(template % variables)
    f.close()
    try:
        os.chmod(outfile, 0755)
    except:
        # you probably don't have os.chmod
        pass

VIRTUAL_ENV = """"""

if __name__ == '__main__':
    main()
