from setuptools import setup, find_packages
import os

here    = os.path.abspath(os.path.dirname(__file__))
README  = open(os.path.join(here, 'README.rst')).read()
NEWS    = open(os.path.join(here, 'NEWS.txt')).read()


version = '0.1'

install_requires = [
    "Preferences    == 0.08",
]


setup(
    name                    = 'bp.preferences',
    version                 = version,
    description             = "Preference system for applications",
    long_description        = README + '\n\n' + NEWS,
    classifiers             = [
      # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    ],
    keywords                = '',
    author                  = 'Andreas Kaiser',
    author_email            = 'disko@binary-punks.com',
    url                     = 'http://github.com/disko/bp.preferences',
    license                 = 'BSD',
    packages                = find_packages('src'),
    package_dir             =  {'': 'src'},
    namespace_packages      =  ['bp'],
    include_package_data    = True,
    zip_safe                = False,
    install_requires        = install_requires,
    entry_points            = {}
)
