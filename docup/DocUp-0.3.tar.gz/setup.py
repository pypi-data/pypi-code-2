import os
from setuptools import setup

setup(name='DocUp',
      description='Documentation Uploader',
      author='Tony Bashi',
      install_requires=[
       "markdown>=2.0.3",
        ],
      author_email='bashia@uvic.ca',
      version='0.3',
      py_modules=['docup'],
      scripts= ['docup.py']
      )

