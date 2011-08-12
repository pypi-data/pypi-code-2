from setuptools import setup, find_packages
import sys, os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
NEWS = open(os.path.join(here, 'NEWS.txt')).read()


version = '0.1.2dev002'

install_requires = [
    # List your project dependencies here.
    # "setuptools", # i need it, but it has to be already installed by the moment, we start this script. Possibly breaking setuptools installation
    # For more details, see:
    # http://packages.python.org/distribute/setuptools.html#declaring-dependencies
]


setup(name='ttr.xml.csv2xml',
    version=version,
    description="module, providing conversion of csv file into xml",
    long_description=README + '\n\n' + NEWS,
    classifiers=[
      # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      "Development Status :: 3 - Alpha",
      "Intended Audience :: Developers",
      "License :: OSI Approved :: BSD License",
      "Programming Language :: Python :: 2.5",
      "Programming Language :: Python :: 2.6",
      "Programming Language :: Python :: 2.7",
      "Topic :: Text Processing :: Markup :: XML"
    ],
    keywords='xml csv module',
    author='Jan Vlcinsky',
    author_email='jan.vlcinsky@gmail.com',
    url='https://bitbucket.org/vlcinsky/ttr.xml.csv2xml',
    license='BSD',
    packages=find_packages('src', exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    package_dir = {'': 'src'},
    namespace_packages = ['ttr', 'ttr.xml'],
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    test_suite="ttr.xml.csv2xml.tests",
    entry_points={
#        'console_scripts':
#            ['ttr.xmlutils.csv2xml=ttr.xmlutils.csv2xml:main']
    }
)
