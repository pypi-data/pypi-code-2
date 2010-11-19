import os
from distutils.core import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = 'fromagerie',
    version = '0.1a1',
    license = 'BSD',
    description = 'A pluggable PyPI for Django projects',
    long_description = read('README'),
    author = 'Jeff Kistler',
    author_email = 'jeff@jeffkistler.com',
    url = 'https://bitbucket.org/jeffkistler/fromagerie',
    packages = ['fromagerie',],
    package_dir = {'': 'src'},
    package_data = {'fromagerie': ['fixtures/*', 'templates/*']},
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ]
)
