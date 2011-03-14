from setuptools import setup, find_packages
import os

here = os.path.dirname(__file__)
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()

version = '0.2.0'

install_requires = [
    # List your project dependencies here.
    # For more details, see:
    # http://packages.python.org/distribute/setuptools.html#declaring-dependencies
    'Flask',
    'Flask-SQLAlchemy',
    'unittest2',
]


setup(
    name = 'pywebuml',
    version = version,
    description = "Creates UML diagrams from code",
    long_description = README + '\n\n' + CHANGES,
    classifiers = [
      "Development Status :: 4 - Beta",
      "Programming Language :: Java",
      "Programming Language :: C#",
      "Topic :: Documentation",
      "Topic :: Software Development :: Documentation",
      "Intended Audience :: Developers",
      "License :: OSI Approved :: BSD License",
      "Operating System :: OS Independent",
      "Programming Language :: Python :: 2.6",
      "Programming Language :: Python :: 2.7",

      # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    ],
    keywords = 'uml',
    author = 'Tomas Zulberti',
    author_email = 'tzulberti@gmail.com',
    url = 'http://bitbucket.org/tzulberti/pywebuml',
    license = 'BSD',
    packages = find_packages(exclude=['tests']),
    include_package_data = True,
    install_requires = install_requires,
    zip_safe = False,
    entry_points= {
        'console_scripts':
            ['pywebuml=pywebuml.commands:main']
    }
)
