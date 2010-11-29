from setuptools import setup
import os, sys

_here = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(_here, 'weewar'))
from version import VERSION

def read(fname):
    return open(os.path.join(_here, fname)).read()

setup(
    name="python-weewar",
    version=VERSION,
    
    description="Python wrapper for the Weewar XML API",
    long_description=read('README'),
    
    author="Sebastian Rahlf",
    author_email="basti AT redtoad DOT de",
    url="http://bitbucket.org/basti/python-weewar/downloads/",
    license='lgpl',
    
    packages=['weewar'],
    install_requires=['lxml>=2.1.5'],
    
    classifiers=[
        'Development Status :: 3 - Alpha', 
        'Intended Audience :: Developers', 
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)', 
        'Programming Language :: Python :: 2.5', 
        'Programming Language :: Python :: 2.6', 
        'Topic :: Games/Entertainment :: Turn Based Strategy', 
    ]

)

