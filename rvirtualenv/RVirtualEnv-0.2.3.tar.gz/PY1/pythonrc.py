# main virtual env conf file
# activation of this venv is done here

import sys
from os import path
import site

base = path.abspath(path.dirname(__file__))

# python uses this almost everywhere
sys.prefix = base

# add default python lib dirs, to the beggining of sys.path
this_site_packages = [
    path.join(base, 'lib/python2.7/site-packages'), # generated purelib
    path.join(base, 'lib/python2.7/site-packages'), # generated platlib
    # sys.path from original python environment
    '/usr/lib/python2.7/lib-old',
    '/home/kvbik/GIT/github/kvbik/rvirtualenv',
    '/usr/lib/python2.7/lib-tk',
    '/usr/lib/python2.7/lib-dynload',
    '/usr/lib/python2.7/plat-linux2',
    '/usr/lib/python2.7/site-packages/setuptools-0.6c11.egg-info',
    '/usr/lib/python2.7/site-packages',
    '/usr/lib/python2.7',
    '/usr/lib/python27.zip',
]

for i in reversed(this_site_packages):
    if i not in sys.path:
        site.addsitedir(i)

