#!/usr/bin/env python
# vi:si:et:sw=4:sts=4:ts=4
# encoding: utf-8
try:
    from setuptools import setup
except:
    from distutils.core import setup

def get_bzr_version():
    return 7 #import os
    rev = int(os.popen('bzr revno').read())
    if rev:
        return u'%s' % rev
    return u'unknown'

setup(
    name="python-firefogg",
    version="1.0.%s" % get_bzr_version() ,
    description='''python-firefogg - video encoding and uploading for python

python-firefogg provides a simple interface to transcode videos
and upload them to sites that have Firefogg chunk upload support. 
''',
    author="j",
    author_email="j@mailb.org",
    url="http://firefogg.org/dev/python-firefogg",
    download_url="http://firefogg.org/dev/python-firefogg/download",
    license="GPLv3",
    packages=['firefogg'],
    keywords = [
    ],
    classifiers = [
      'Operating System :: OS Independent',
      'Programming Language :: Python',
      'Topic :: Software Development :: Libraries :: Python Modules',
      'License :: OSI Approved :: GNU General Public License (GPL)',
    ],
)

