from setuptools import setup, find_packages
import sys, os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
NEWS = open(os.path.join(here, 'NEWS.txt')).read()

version = '0.1'

install_requires = [
    # List your project dependencies here.
    # For more details, see:
    # http://packages.python.org/distribute/setuptools.html#declaring-dependencies
    'Flask',
    'Flask-SQLAlchemy',
    'unittest2',
]


setup(name='pywebuml',
    version=version,
    description="Creates UML diagrams from code",
    long_description=README + '\n\n' + NEWS,
    classifiers=[
      "Development Status :: 4 - Beta",
      "Programming Language :: Java",
      "Programming Language :: C#",
      "Topic :: Documentation",
      "Topic :: Software Development :: Documentation",
      "Intended Audience :: Developers",
      "License :: OSI Approved :: BSD License",
      "Operating System :: OS Independent",
      "Programming Language :: Python :: 2.7"
      
      # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    ],
    keywords='uml',
    author='Tomas Zulberti',
    author_email='tzulberti@gmail.com',
    url='',
    license='BSD',
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    entry_points={
        'console_scripts':
            ['pywebuml=pywebuml.commands:main']
    }
)
