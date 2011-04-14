from setuptools import setup, find_packages
import os

version = '0.2'

tests_require = [
    ]

setup(name='dolmen.collection',
      version=version,
      description="Collection of named entities",
      long_description=open("README.txt").read() + "\n" +
        open(os.path.join("src", "dolmen", "collection", "README.txt"))
                                                                   .read() +
        open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='collection library',
      author='Dolmen Team',
      author_email='dolmen@list.dolmen-project.org',
      url='http://pypi.python.org/pypi/dolmen.collection',
      license='BSD',
      package_dir={'': 'src'},
      packages=find_packages('src'),
      namespace_packages=['dolmen', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'zope.interface',
          'zope.component',
          ],
      tests_require=tests_require,
      extras_require={'test': tests_require},
      )
