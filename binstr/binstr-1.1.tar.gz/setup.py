from distutils.core import setup

long_desc = open('README.txt').read()

setup(
    name                = 'binstr',
    version             = '1.1',
    py_modules          = ['binstr'],
    description         = 'Utility functions for strings of binary digits',
    author              = 'David McEwan',
    author_email        = 'dmcewa15@caledonian.ac.uk',
    license             = 'GLPv3',
    platforms           = 'Python >2.6 including 3.x (OS Independent)',
    url                 = 'https://github.com/DavidMcEwan/binstr',
    
    classifiers         = [
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Software Development :: Code Generators',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Development Status :: 5 - Production/Stable'
                          ],
    
    long_description    = long_desc
     )
