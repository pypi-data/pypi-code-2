from setuptools import setup, find_packages
import sys, os

version = '1.0'

setup(name='django-garcimore',
      version=version,
      description="A magic trick to make Django disappear",
      long_description=open('README.txt').read(),
      classifiers=[
            'Framework :: Django',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
            'Development Status :: 5 - Production/Stable',
          ],
      keywords='django garcimore magic',
      author='Gael Pasgrimaud',
      author_email='gael@gawel.org',
      url='http://github.com/gawel/django-garcimore',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
