
from distutils.core import setup
import sys


VERSION = '0.4.0'


setup(
    name = 'wddx',
    py_modules = ['wddx'],
    version = VERSION,
    author = 'Leon Matthews',
    author_email = 'python@lost.co.nz',
    url = 'http://lost.co.nz/',
    download_url = 'https://github.com/leon-matthews/wddx',
    license='LICENSE.txt',

    description='A Python decoder for the WDDX XML serialisation format.',
    long_description=open('README.txt').read(),

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: Markup :: XML',
        ],
    )
