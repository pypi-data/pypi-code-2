from os.path import abspath, dirname, join
try:
  # try to use setuptools
  from setuptools import setup
  setupArgs = dict(
      include_package_data=True,
      namespace_packages=['dm'],
      zip_safe=True,
      test_suite='dm.reuse.tests.testsuite',
      )
except ImportError:
  # use distutils
  from distutils import setup
  setupArgs = dict(
    )

cd = abspath(dirname(__file__))
pd = join(cd, 'dm', 'reuse')

def pread(filename, base=pd): return open(join(base, filename)).read().rstrip()

setup(name='dm.reuse',
      version=pread('VERSION.txt'),
      description='Support for object reuse with slight modifications',
      long_description=pread('README.txt'),
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development',
        'Topic :: Utilities',
        ],
      author='Dieter Maurer',
      author_email='dieter@handshake.de',
      packages=['dm', 'dm.reuse',],
      keywords='reuse ',
      license='BSD (see "dm/reuse/LICENSE.txt", for details)',
      **setupArgs
      )



