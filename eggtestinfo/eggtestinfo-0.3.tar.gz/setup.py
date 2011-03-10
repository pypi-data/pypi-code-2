__version__ = '0.3'

from setuptools import setup
README = open('README.txt').read()
CHANGES = open('CHANGES.txt').read()

setup(
    name="eggtestinfo",
    version=__version__,
    description="Add test information to .egg-info",
    author="Tres Seaver",
    author_email="tseaver@palladion.com",
    license="PSF or ZPL",
    long_description = '\n\n'.join(('', README,CHANGES)),
    keywords = "setuptools eggs testing",
    url = "http://pypi.python.org/pypi/eggtestinfo",
    packages = (),
    py_modules = ['eggtestinfo'],
    zip_safe = True,
    test_suite = 'test_egginfo',

    entry_points = {

        "egg_info.writers": [
            "test_info.txt = eggtestinfo:write_test_info",
        ],

    },
    classifiers = [f.strip() for f in """
    Development Status :: 3 - Alpha
    Framework :: Setuptools Plugin
    Intended Audience :: Developers
    License :: OSI Approved :: Python Software Foundation License
    License :: OSI Approved :: Zope Public License
    Operating System :: OS Independent
    Programming Language :: Python :: 2
    Programming Language :: Python :: 3
    Topic :: Software Development :: Libraries :: Python Modules
    Topic :: System :: Archiving :: Packaging""".splitlines() if f.strip()],
)
