#! /usr/bin/python
from distutils.core import setup
from glob import glob

# to install type:
# python setup.py install --root=/

setup (name='ghalatawi', version='0.2',
      description='Ghalatawi: Arabic AUtocorrect',
      author='Taha Zerrouki',
      author_email='taha.zerrouki@gmail.com',
      url='http://ghalatawi.sourceforge.net/',
      license='GPL',
      Description="Ghalatawi: Arabic AUtocorrect",
      Platform="OS independent",
      package_dir={'ghalatawi': 'ghalatawi',},
      packages=['ghalatawi'],
      # include_package_data=True,
      package_data = {
        'ghalatawi': ['doc/*.*','data/arabic.acl', ],
        },
      classifiers=[
          'Development Status :: 5 - Beta',
          'Intended Audience :: Developpers',
          'Operating System :: OS independent',
          'Programming Language :: Python',
          ],
    );

