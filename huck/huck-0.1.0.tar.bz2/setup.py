from distutils.core import setup
from huck import __version__

long_description = """
Huck is a web application framework based on Twisted and derived
from Tornado and Cyclone.
"""

setup(
    name='huck',
    version=__version__,
    description='A web application framework based on Twisted',
    long_description=long_description.strip(),
    author='Silas Sewell',
    author_email='silas@sewell.ch',
    license='Apache 2',
    url='https://github.com/silas/huck',
    packages=[
        'huck',
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
