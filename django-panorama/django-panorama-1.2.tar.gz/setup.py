APP_NAME='panorama'
from setuptools import setup, find_packages
import os

version = '1.2'

setup(name='django-%s'%APP_NAME,
      version=version,
      description="Show panoramic photos in django",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Maider Likona',
      author_email='pisoni@gisa-elkartea.org',
      url='http://lagunak.gisa-elkartea.org/projects/djangopanorama',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      package_dir={
          APP_NAME: APP_NAME,
      },
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'PIL',
          'django-multilingual-ng',
          'django-tinymce',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
