#! /usr/bin/python
from distutils.core import setup
from glob import glob

# to install type:
# python setup.py install --root=/

setup (name='Naftawayh', version='0.1',
      description='Naftawayh: Arabic word tagger',
      author='Taha Zerrouki',
      author_email='taha.zerrouki@gmail.com',
      url='http://naftawayh.sourceforge.net/',
      license='GPL',
      Description="Naftawayh: Arabic word tagger",
      Platform="OS independent",
      package_dir={'naftawayh': 'naftawayh'},
      packages=['naftawayh'],
      # include_package_data=True,
      package_data = {
        'naftawayh': ['doc/*.*','doc/html/*'],
        },
      classifiers=[
          'Development Status :: 5 - Beta',
          'Intended Audience :: End Users/Desktop',
          'Operating System :: OS independent',
          'Programming Language :: Python',
          ],
    );

