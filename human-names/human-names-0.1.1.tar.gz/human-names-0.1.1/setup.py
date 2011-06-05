""" human-names
    human-names is a simple utility to generate random names based on 
    actual names collected by the US Census. These are, of course, biased
    based on the US population.
    See http://www.census.gov/genealogy/names/names_files.html for details. 
"""

classifiers = """\
Development Status :: 3 - Alpha
Intended Audience :: Developers
License :: OSI Approved :: GNU General Public License (GPL)
Natural Language :: English
Programming Language :: Python
Topic :: Utilities
Topic :: Software Development :: Libraries :: Python Modules
Topic :: Sociology :: Genealogy
Operating System :: OS Independent
"""

from distutils.core import setup, sys

if sys.version_info < (2, 3):
    _setup = setup
    def setup(**kwargs):
        if kwargs.has_key("classifiers"):
            del kwargs["classifiers"]
        _setup(**kwargs)

doclines = __doc__.split("\n")

setup(name="human-names",
      version="0.1.1",
      maintainer="Justin Chudgar",
      maintainer_email="justin@justinzane.com",
      url = "http://www.justinzane.com/",
      license = "http://www.gnu.org/licenses/gpl.html",
      platforms = ["any"],
      description = doclines[0],
      classifiers = filter(None, classifiers.split("\n")),
      long_description = "\n".join(doclines[2:]),
      packages=['human-names'],
      package_dir={'human-names': '../human-names'},
      package_data={'human-names': ['data/*.csv']},
      )
