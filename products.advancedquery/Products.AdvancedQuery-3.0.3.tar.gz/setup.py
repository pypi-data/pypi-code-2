from os.path import abspath, dirname, join
try:
  # try to use setuptools
  from setuptools import setup
  setupArgs = dict(
      include_package_data=True,
      namespace_packages=['Products'],
      zip_safe=False, # to let the tests work
      )
except ImportError:
  # use distutils
  from distutils import setup
  setupArgs = dict(
    )

cd = abspath(dirname(__file__))
pd = join(cd, 'Products', 'AdvancedQuery')

def pread(filename, base=pd): return open(join(base, filename)).read().rstrip()

setup(name='Products.AdvancedQuery',
      version=pread('VERSION.txt').split('\n')[0],
      description='Flexible high level search construction and execution. For Zope 2.11 and above.',
      long_description=pread('README.txt'),
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Framework :: Zope2',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
        ],
      author='Dieter Maurer',
      author_email='dieter@handshake.de',
      url='http://www.dieter.handshake.de/pyprojects/zope',
      packages=['Products', 'Products.AdvancedQuery', 'Products.AdvancedQuery.tests'],
      keywords='Zope 2, flexible, search, construction, execution',
      license='BSD (see "Products/AdvancedQuery/LICENSE.txt", for details)',
      **setupArgs
      )



