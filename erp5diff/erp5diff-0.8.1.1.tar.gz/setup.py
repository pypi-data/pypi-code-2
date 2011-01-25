#! /usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import re

api_version = re.search(r'\s*__version__\s*=\s*(\S+)',
                        open('src/ERP5Diff.py').read()).group(1).strip()
revision = 1
version = '%s.%s' % (api_version.replace("'", ''), revision)


setup(name="erp5diff",
      version=version,
      description="XUpdate Generator for ERP5",
      author="Yoshinori OKUJI",
      author_email="yo@nexedi.com",
      url="http://www.erp5.org/",
      license="GPL",
      packages=find_packages('src'),
      package_dir={'': 'src'},
      entry_points={'console_scripts': ["erp5diff = ERP5Diff:main"]},
      data_files=[('share/man/man1', ['src/erp5diff.1'])],
      install_requires=['lxml'],
      classifiers=['License :: OSI Approved :: GNU General Public License (GPL)',
                  'Operating System :: OS Independent',
                  'Topic :: Text Processing :: Markup :: XML',
                  'Topic :: Utilities'],
      include_package_data=True,
      zip_safe=False,
      test_suite='tests',
     )
