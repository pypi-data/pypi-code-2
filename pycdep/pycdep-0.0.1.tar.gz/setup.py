from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
NEWS = open(os.path.join(here, 'NEWS.txt')).read()

version = '0.0.1'

install_requires = [
    # List your project dependencies here.
    # For more details, see:
    # http://packages.python.org/distribute/setuptools.html#declaring-dependencies
    'path.py>=2.2.2',
    'mako>=0.4.1',
    'oset>=0.1.1'
]

setup(name='pycdep',
      version=version,
      description="Header file dependency analysis and visualization for C/C++.",
      long_description=README + '\n\n' + NEWS,
      classifiers=[
      # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      "Development Status :: 3 - Alpha",
      "Environment :: Console",
      "Intended Audience :: Developers",
      "License :: OSI Approved :: GNU General Public License (GPL)",
      "Natural Language :: English",
      "Operating System :: OS Independent",
      "Programming Language :: Python :: 2.6",
      "Programming Language :: Prolog",
      "Topic :: Software Development :: Quality Assurance"
    ],
    keywords='header file dependency analysis visualization C C++ prolog',
    author='stefaan himpe',
    author_email='stefaan.himpe@gmail.com',
    url='http://pycdep.sourceforge.net',
    license='GPLv3',
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    entry_points={
        'console_scripts':
            ['pycdep=pycdep:main']
    }
)
