from setuptools import setup, find_packages
import os

version = '0.5'

setup(name='buildout.umask',
      version=version,
      description="Use a custom umask when running buildout.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Buildout",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Topic :: Software Development :: Build Tools",
        "Operating System :: POSIX",
        ],
      keywords='',
      author='Servilio Afre Puentes',
      author_email='afrepues@mcmaster.ca',
      url='https://launchpad.net/buildout.umask',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['buildout'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points={
        'zc.buildout.extension': ['default = buildout.umask:load'],
        },
      )
