from setuptools import setup, find_packages
import os

version = '0.1.4'

setup(name='zopyx.trashfinder',
      version=version,
      description="Find package trash on PyPI",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='Trash Crap PyPI',
      author='Andreas Jung',
      author_email='info@zopyx.com',
      url='http://pypi.python.org/pypi/zopyx.trashfinder',
      license='ZPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['zopyx'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points=dict(console_scripts=(
        'pypi-trashfinder=zopyx.trashfinder.cli:main',
        )),
      )
