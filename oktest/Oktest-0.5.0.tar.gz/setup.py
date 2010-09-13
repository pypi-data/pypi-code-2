###
### $Release: 0.5.0 $
### $Copyright: copyright(c) 2010 kuwata-lab.com all rights reserved $
### $License: MIT License $
###

import sys, re, os
arg1 = len(sys.argv) > 1 and sys.argv[1] or None
if arg1 == 'egg_info':
    from ez_setup import use_setuptools
    use_setuptools()
if arg1 == 'bdist_egg':
    from setuptools import setup
else:
    from distutils.core import setup


name     = 'Oktest'
version  = '0.5.0'
author   = 'makoto kuwata'
email    = 'kwa@kuwata-lab.com'
maintainer = author
maintainer_email = email
url      = 'http://pypi.python.org/pypi'
desc     = 'a new-style testing library'
detail   = (
            "Oktest is a new-style testing library.\n"
            "::\n"
            "\n"
            "    from oktest import ok\n"
            "    ok (x) > 0                 # same as assert_(x > 0)\n"
            "    ok (s) == 'foo'            # same as assertEqual(s, 'foo')\n"
            "    ok (s) != 'foo'            # same as assertNotEqual(s, 'foo')\n"
            "    ok (f).raises(ValueError)  # same as assertRaises(ValueError, f)\n"
            "    ok (u'foo').is_a(unicode)  # same as assert_(isinstance(u'foo', unicode))\n"
            "    not_ok (u'foo').is_a(int)  # same as assert_(not isinstance(u'foo', int))\n"
            "    ok ('A.txt').is_file()     # same as assert_(os.path.isfile('A.txt'))\n"
            "    not_ok ('A.txt').is_dir()  # same as assert_(not os.path.isdir('A.txt'))\n"
            "\n"
            "You can use ok() instead of 'assertXxx()' in unittest.\n"
            "\n"
            "Oktest requires Python 2.4 or later. Oktest is ready for Python 3.\n"
            "\n"
            "NOTICE!! Oktest is a young project and specification may change in the future.\n"
            "\n"
            "See README_ for details.\n"
            "\n"
            ".. _README: http://packages.python.org/Oktest\n"
           )
license  = 'MIT License'
platforms = 'any'
#download = 'http://downloads.sourceforge.net/oktest/Oktest-%s.tar.gz' % version
download = 'http://pypi.python.org/packages/source/O/Oktest/Oktest-%s.tar.gz' % version
classifiers = [
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    #'Programming Language :: Python :: 2.3',
    'Programming Language :: Python :: 2.4',
    'Programming Language :: Python :: 2.5',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.0',
    'Programming Language :: Python :: 3.1',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Software Development :: Testing'
]


setup(
    name=name,
    version=version,
    author=author,  author_email=email,
    maintainer=maintainer, maintainer_email=maintainer_email,
    description=desc,  long_description=detail,
    url=url,  download_url=download,  classifiers=classifiers,
    license=license,
    #platforms=platforms,
    #
    py_modules=['oktest'],
    package_dir={'': 'lib'},
    #scripts=['bin/pytenjin'],
    #packages=['tenjin'],
    zip_safe = False,
)
