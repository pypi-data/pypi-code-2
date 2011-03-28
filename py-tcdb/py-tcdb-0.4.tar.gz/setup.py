import os
from distutils.core import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='py-tcdb',
      version='0.4',
      description='A Python wrapper for Tokyo Cabinet database using ctypes.',
      long_description=read('README'),
      author='Alberto Planas',
      author_email='aplanas@gmail.com',
      url='http://code.google.com/p/py-tcdb/',
      download_url='http://py-tcdb.googlecode.com/files/py-tcdb-0.4.tar.gz',
      packages=['tcdb'],
      classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Database',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
      license='LGPL',
      keywords=['tokyo cabinet', 'ctypes', 'database'],
      )
