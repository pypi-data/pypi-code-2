#!python

"""Note! Some of these modules require the gpklib C++ libraries.
These can be obtained from http://sourceforge.org/projects/speechresearch
"""

from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

import os
import sys
import numpy
Include_dirs = [ '.', 'lib', numpy.get_include()]
Ldirs = os.environ.get('LD_LIBRARY_PATH', '').split(':')
# Ldirs = [ os.path.join(os.environ['HOME'], 'local', 'lib') ]
for l in Ldirs:
	if l.endswith('/lib'):
		Include_dirs.append( '/'.join(l.split('/')[:-1] + ['include']) )
print 'Ldirs=', Ldirs
print 'Include_dirs=', Include_dirs
del l


setup(name = "gmisclib", version = "0.73.0",
	description = "Various Python Libraries, mostly scientific purposes",
	author = "Greg Kochanski",
	url = "http://kochanski.org/gpk/code/speechresearch/gmisclib",
	author_email = "gpk@kochanski.org",
	packages = ['gmisclib'],
	package_dir = {'gmisclib': '.'},
	scripts = ["bin/select_fiat_entries.py", 'bin/gpk_wavio.py',
			'bin/pylab_server.py', 'bin/q3html.py',
			'bin/run_several.py', 'bin/mcmc_cooperate.py',
			'bin/dtw4', 'bin/get_gcc_flags.py',
			'bin/summarize_logs'
			],
	ext_modules=[ 
    		Extension("gmisclib.dtw4",         ["dtw4.pyx"],
				include_dirs = Include_dirs,
				depends = [],
				library_dirs = Ldirs,
				libraries = ['gpk'],
				language = 'c++'
				),
    		# Extension("gmisclib.idle",         ["idle.c"],
				# include_dirs = Include_dirs,
				# depends = [],
				# library_dirs = Ldirs,
				# libraries = ['gpk'],
				# language = 'c'
				# ),
		],
	cmdclass = {'build_ext': build_ext},
	license = 'GPL2',
	keywords = "phonetics speech computational linguistics basic library python science optimize",
	platforms = "All",
	classifiers = [
		'License :: OSI Approved :: GNU General Public License (GPL)',
		'Operating System :: OS Independent',
		'Development Status :: 4 - Beta',
		'Topic :: Scientific/Engineering',
		'Environment :: Console',
		'Intended Audience :: Science/Research',
		'Programming Language :: Python',
		'Operating System :: OS Independent',
		'Programming Language :: Python',
		],
	long_description = """Various Python Libraries, mostly scientific purposes.
	See http://kochanski.plus.com/code/speechresearch/gmisclib for documentation
	and http://sourceforge.net/projects/speechresearch for downloads,
	or look on the Python Cheese shop, http://pypi.python.org .

	Note that most of the algorithms here are carefully tested, but the stuff that
	I don't use may have suffered from bit rot.
	"""
	)

