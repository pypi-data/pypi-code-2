from setuptools import setup

name = "erp5.appliance.test"
version = '1.0'

def r(n): return open(n).read()

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
      ],
    package_dir={'':'src'},
    url='http://svn.erp5.org/erp5/trunk/utils/%s' % name,
    py_modules=['test'],
    install_requires=['pexpect'],
    entry_points="""
    [console_scripts]
    erp5apptest212 = test:main212
    erp5apptest212ex = test:mainex212
    erp5apptest28 = test:main28
    erp5apptest28ex = test:mainex28
    """,
    )
