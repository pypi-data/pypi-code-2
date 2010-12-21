from distutils.core import setup, Extension
from setuptools import find_packages

tests_require = [
    'zope.testing',
    'zc.recipe.egg',
    'Cherrypy',
    'unittest2',
    ]

docs_require = [
    'Sphinx',
    'collective.recipe.sphinxbuilder',
    'docutils',
    'roman',
    ]

setup (name = 'odls.client',
       version = '0.1',
       description = 'A Python client for ODLS',
       author = 'Uli Fouquet',
       author_email = 'uli at gnufix.de',
       url = 'http://pypi.python.org/pypi/odls.client',
       long_description=open("README.txt").read() + "\n\n" +
                       open("CHANGES.txt").read(),
       classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Framework :: Buildout",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: System Administrators",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "Topic :: Text Processing :: Indexing",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        ],
       keywords='ODLS client server filesystem indexer odls_client',
       packages=find_packages('src', exclude=['ez_setup']),
       namespace_packages=['odls', ],
       package_dir = {'': 'src'},
       install_requires = [
        'ulif.pynotify [sqlite]',
        'setuptools',
        'pysqlite',
        ],
       extras_require=dict(
        test = tests_require,
        docs = docs_require,
        ),
       entry_points="""
       [console_scripts]
       indexer = odls.client.main:main
       """
       )
