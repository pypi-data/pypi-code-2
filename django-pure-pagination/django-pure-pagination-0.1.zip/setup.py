import os
from distutils.core import setup
from setuptools import setup, find_packages

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))

long_description = ''
try:
    if 'README.rst' in list(os.walk(CURRENT_DIR))[0][2]:
        long_description = open(os.path.join(CURRENT_DIR, 'README.rst'), 'rb').read()
except IOError:
    pass

setup(name='django-pure-pagination',
      version='0.1',
      author='James Pacileo',
      long_description = long_description,
      license='BSD',
      keywords='pagination, django',
      classifiers=[
          "Programming Language :: Python",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "Framework :: Django",
          "Environment :: Web Environment",
      ],
      author_email='jamespacileo@gmail.com',
      url='https://github.com/jamespacileo/django-pure-pagination/',
      packages = ['pure_pagination'],
      include_package_data=True,
      zip_safe = False,
      package_data = {
        'pure_pagination': ['pure_pagination/templates', 'pure_pagination/templates/pure_pagination', 'pure_pagination/templates/pure_pagination/index.html'],
      },
      )