from setuptools import setup

name = "erp5.appliance.test"
version = '2.11'

def r(n): return open(n).read()

install_requires = ['pexpect']
import sys
if sys.version_info < (2, 5):
  install_requires.append('uuid')
setup(
    name=name,
    version=version,
    author='Lukasz Nowak',
    author_email='luke@nexedi.com',
    description="ERP5 Appliance testing system",
    long_description=r('README.txt') + '\n' + r('CHANGES.txt'),
    license="GPL",
    keywords="erp5 appliance test",
    classifiers=[
      "Environment :: Console",
      "Intended Audience :: Developers",
      "License :: OSI Approved :: GNU General Public License (GPL)",
      "Operating System :: POSIX",
      "Topic :: Software Development :: Testing",
      "Programming Language :: Python :: 2.4",
      "Programming Language :: Python :: 2.5",
      "Programming Language :: Python :: 2.6",
      "Programming Language :: Python :: 2.7",
      ],
    package_dir={'':'src'},
    url='http://svn.erp5.org/erp5/trunk/utils/%s' % name,
    py_modules=['test'],
    install_requires=install_requires,
    entry_points="""
    [console_scripts]
    erp5apptest212 = test:main212
    erp5apptest28 = test:main28
    """,
    )
