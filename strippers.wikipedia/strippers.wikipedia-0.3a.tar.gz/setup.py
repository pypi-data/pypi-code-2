from setuptools import setup, find_packages
import os.path

def getversion(fname):
    """Get the __version__ reading the file: works both in Python 2.X and 3.X,
    whereas direct importing would break in Python 3.X with a syntax error"""
    for line in open(fname):
        if line.startswith('__version__'):
            return eval(line[13:])
    raise NameError('Missing __version__ in wikipedia.py')

VERSION = getversion(
    os.path.join(os.path.dirname(__file__), 'strippers/wikipedia.py'))


setup(
    name                 = 'strippers.wikipedia',
    version              = VERSION,
    packages             = find_packages(),
    package_dir          = {'strippers': 'strippers'},
    namespace_packages   = ['strippers'],

    # Package dependencies
    install_requires     = ['setuptools', 'BeautifulSoup', 'jcconv'],

    # Packaging options
    include_package_data = True,
    
    author               = 'Tomohiro Otsuka',
    author_email         = 't.otsuka@gmail.com',
    description          = 'Wikipedia(ja) article parser',
    #long_description     = open('README.rst').read(),
    url                  = 'http://pypi.python.org/pypi/strippers.wikipedia',
    license              = 'LGPL',
    keywords             = 'Wikipedia',
    zip_safe             = False,
    classifiers          = [
                            'Development Status :: 3 - Alpha',
                            'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
                            'Intended Audience :: Developers',
                            'Topic :: Software Development :: Libraries :: Python Modules',
                            'Programming Language :: Python :: 2.6',
                            'Operating System :: OS Independent',
                            'Natural Language :: Japanese',
                            ],
    )

