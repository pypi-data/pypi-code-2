# -*- coding: UTF-8 -*-

import os
# BEFORE importing distutils, remove MANIFEST. distutils doesn't properly
# update it when the contents of directories change.
if os.path.exists('MANIFEST'): os.remove('MANIFEST')

def setup_module():
    from distutils.core import setup
    import mpy

    setup(
        name='mpy',
        version=mpy.__version__,
        author='Yung-Yu Chen',
        author_email='yyc+mpy@seety.org',
        url='http://bitbucket.org/yungyuc/mpy/',
        description=mpy.__description__.strip(),
        long_description=mpy.__doc__,
        classifiers=[
            'Development Status :: 4 - Beta',
            'Environment :: Console',
            'Environment :: No Input/Output (Daemon)',
            'Intended Audience :: Developers',
            'Intended Audience :: Education',
            'License :: OSI Approved :: BSD License',
            'Topic :: Scientific/Engineering',
            'Topic :: System :: Distributed Computing',
            'Operating System :: POSIX :: Linux',
            'Programming Language :: Python',
        ],
        platforms=[
            'Linux',
        ],
        license='BSD',
        py_modules=[
            'mpy',
        ],
    )

if __name__ == '__main__':
    setup_module()
