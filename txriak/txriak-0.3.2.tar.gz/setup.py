"""
txriak setup.py
Copyright (c) 2010 Appropriate Solutions, Inc. All rights reserved.
See txriak.__LICENSE__ for details.
"""
# http://peak.telecommunity.com/DevCenter/setuptools#eggsecutable-scripts

from setuptools import setup, find_packages
from txriak import VERSION

# zip_safe = False because we do not want to install zipped eggs.
# we tend to build py2exe and py2app packages and they do not work with zipped eggs.

setup(name='txriak',
      version=VERSION,
      description="""txriak is a Twisted module that communicates with the
                     HTTP interface of Basho Technologies Riak data store.""",
      author="Appropriate Solutions, Inc.",
      author_email="asi@AppropriateSolutions.com",
      license="Apache 2.0",
      url="http://bitbucket.org/asi/txriak",
      platforms="Linux",
      long_description="""Currently tested under Python 2.6, Python 2.7, and Linux.
      Uses the yield form of deferreds.""",
      keywords="twisted riak txriak",
#      url="to be determined when we upload",
      classifiers=["Framework :: Twisted",
                   "Development Status :: 3 - Alpha",
                  ],
      packages=find_packages(),
      package_data={
                     '':['README', '*.txt', 'docs/*.py', ]
                   },
      zip_safe=False,
     )

