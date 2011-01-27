from distutils.core import setup
from txldap import __version__

long_description = """
txldap is a Twisted wrapper for python-ldap.
"""

setup(
    name='txldap',
    version=__version__,
    description='Twisted wrapper for python-ldap',
    long_description=long_description.strip(),
    author='Silas Sewell',
    author_email='silas@sewell.ch',
    license='MIT',
    url='https://github.com/silas/txldap',
    py_modules=['txldap'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
