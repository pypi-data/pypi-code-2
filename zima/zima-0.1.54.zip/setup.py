# -*- coding: utf-8 -*-
import os
import sys
import glob

from distutils.core import setup

# Манипуляции со схемами нужны для того, чтобы все устанавливалось в
# site-packages
from distutils.command.install import INSTALL_SCHEMES

for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']

try:
    import py2exe
except:
    pass

opts = {'py2exe': {'includes' : ['pygments']}}

data_files=[('zima/themes',
			 glob.glob('zima/themes/*.html')
			 + glob.glob('zima/themes/*.py')),
            ('zima/resources', glob.glob('zima/resources/*')),
            ('zima/static', glob.glob('zima/static/*')),
            ('zima/media/src', ['zima/media/src/.ph']),
            ('zima/media/thumb', ['zima/media/thumb/.ph'])]

import ver
[major, minor, build] = ver.version

if sys.argv[1] == 'sdist':
	build += 1
	open('ver.py', 'w').write('version = %s' % str([major, minor, build]))

setup(
    name='zima',
    version='%d.%d.%d' % (major, minor, build),
    author='Neil Faclly',
    author_email='nyufac@gmail.com',
    packages=['zima', 'zima.backends', 
              'zima.captcha', 'zima.hooks'],
    install_requires=['PIL >= 1.1', 'Pygments >= 1.3', 'bottle >= 0.8.5',
					  'nannou >= 0.7'],
    scripts=['zima/tools/zwipe.py'],
    url='http://pypi.python.org/pypi/zima/',
    license='LICENSE.txt',
    description='Zima image board',
    long_description=open('README').read(),

    # Py2exe options
    console=['zima/__init__.py'], 
    options=opts, 
    data_files=data_files
)
