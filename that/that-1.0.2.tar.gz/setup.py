import os
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = 'that',
    version = '1.0.2',
    description = 'The Anti-Zen of Python',
    license = 'BSD',
    long_description = read('README.rst'),
    url = 'https://github.com/pydanny/that',
    
    author = 'Daniel Greenfeld',
    author_email = 'pydanny@gmail.com',
    
    py_modules =  ['that'],
    
    classifiers = (
        'Development Status :: 6 - Mature',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',        
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',                        
        'Programming Language :: Python',
    ),
)
