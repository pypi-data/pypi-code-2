from os.path import abspath, dirname, join
try:
  # try to use setuptools
  from setuptools import setup
  setupArgs = dict(
      install_requires=['dm.reuse',],
      include_package_data=True,
      namespace_packages=['dm'],
      zip_safe=True,
      )
except ImportError:
  # use distutils
  from distutils import setup
  setupArgs = dict(
    )

cd = abspath(dirname(__file__))
pd = join(cd, 'dm', 'pdb')

def pread(filename, base=pd): return open(join(base, filename)).read().rstrip()

setup(name='dm.pdb',
      version=pread('VERSION.txt'),
      description='Slightly extended and sanitized Python debugger -- Debugger with Zope support',
      long_description=pread('README.txt'),
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development',
        ],
      author='Dieter Maurer',
      author_email='dieter@handshake.de',
      packages=['dm', 'dm.pdb',],
      keywords='debugger pdb Zope',
      license='BSD (see "dm/pdb/LICENSE.txt", for details)',
      **setupArgs
      )
