from setuptools import setup, find_packages
import sys, os

scripts = [
    os.path.join('bin', 'kforge-install'),
]

setup(name='kforgeinstall',
      version='0.1',
      description='',
      long_description='',
      classifiers=[],
      keywords='',
      author='Appropriate Software Foundation',
      author_email='',
      url='',
      license='',
      package_dir={'': 'src'},
      packages=find_packages('src'),
      scripts=scripts,
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      )
