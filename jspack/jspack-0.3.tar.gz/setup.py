from setuptools import setup, find_packages
import sys, os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()


version = '0.3'

install_requires = [
    # List your project dependencies here.
    # For more details, see:
    # http://packages.python.org/distribute/setuptools.html#declaring-dependencies
#    'jsmin',
#    'slimit',
]


setup(name='jspack',
    version=version,
    description="A simple tool for javascript packging using config files",
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
      # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      'Programming Language :: JavaScript',
      'Topic :: Software Development :: Build Tools',
      'Topic :: Software Development :: Code Generators',
      'License :: OSI Approved :: MIT License'
    ],
    keywords='javascript tools',
    author='Pablo Caro',
    author_email='pcaro@yaco.es',
    url='http://pypi.python.org/pypi/jspack',
    license='MIT',
    packages=find_packages('src'),
    package_dir = {'': 'src'},include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    entry_points={
        'console_scripts':
            ['jspack=jspack:main']
    }
)
