import os
from setuptools import setup

os.system("cp docup.py docup")
setup(name='DocUp',
      description='Documentation Uploader',
      author='Tony Bashi',
      install_requires=[
       "markdown>=2.0.3",
        ],
      author_email='bashia@uvic.ca',
      version='0.5',
      py_modules=['docup'],
      scripts= ['docup']
      )
os.system("rm docup")
