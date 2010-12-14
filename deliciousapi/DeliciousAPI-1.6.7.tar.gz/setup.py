#!/usr/bin/env python
from distutils.core import setup

setup(
    name="DeliciousAPI",
    version="1.6.7",
    keywords='del.icio.us delicious api research social bookmarking python',
    description="Unofficial Python API for retrieving data from Delicious.com",
    long_description="""This module provides the following features plus some more:

    * retrieving a URL's full public bookmarking history including
        * users who bookmarked the URL including tags used for such bookmarks
          and the creation time of the bookmark (up to YYYY-MM-DD granularity)
        * top tags (up to a maximum of 10) including tag count
        * title as stored on Delicious.com
        * total number of bookmarks/users for this URL at Delicious.com
    * retrieving a user's full bookmark collection, including any private bookmarks
      if you know the corresponding password
    * retrieving a user's full public tagging vocabulary, i.e. tags and tag counts
    * retrieving a user's network information (network members and network fans)
    * HTTP proxy support
    * updated to support Delicious.com "version 2" (mini-relaunch as of August 2008)

    The official Delicious.com API and the JSON/RSS feeds do not provide all
    the functionality mentioned above, and in such cases this module will query
    the Delicious.com *website* directly and extract the required information
    by parsing the HTML code of the resulting Web pages (a kind of poor man's
    web mining). The module is able to detect IP throttling, which is employed
    by Delicious.com to temporarily block abusive HTTP request behavior, and
    will raise a custom Python error to indicate that. Please be a nice netizen
    and do not stress the Delicious.com service more than necessary.

    It is strongly advised that you read the Delicious.com Terms of Use
    before using this Python module. In particular, read section 5
    'Intellectual Property'.

    The code is licensed to you under version 2 of the GNU General Public
    License.

    More information about this module can be found at
    http://www.michael-noll.com/wiki/Del.icio.us_Python_API

    Changelog is available at
    http://code.michael-noll.com/?p=deliciousapi;a=log

    Copyright 2006-2010 Michael G. Noll <http://www.michael-noll.com/>

    """,
    author="Michael G. Noll",
    author_email="coding[AT]michael-noll[DOT]com",
    license='GNU General Public License version 2',
    url="http://www.michael-noll.com/wiki/Del.icio.us_Python_API",
    py_modules=['deliciousapi'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Sociology',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=["simplejson>=1.9.2", "BeautifulSoup>=3.0.7"],
)
