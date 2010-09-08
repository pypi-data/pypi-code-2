##############################################################################
#
# Copyright (c) 2010 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

import os
import shutil
import urllib2
import urlparse
import zipfile

VERSION = '1.2.4'
BASEURL = "http://cdn.jquerytools.org/%s/all/jquery.tools.min.js" %VERSION
FILENAME = "jquery.tools.min.js"

def prepare_jquerytools():
    jquerytools_dest_path = os.path.dirname(__file__)
    library_path = os.path.join(jquerytools_dest_path, "jquerytools-build")

    # remove previous slimbox library
    print 'recursivly removing "%s"' % library_path
    shutil.rmtree(library_path, ignore_errors=True)

    url = BASEURL
    print 'downloading "%s"' % url
    f = urllib2.urlopen(url)
    file_data = f.read()
    f.close()
    dest_filename = os.path.join(jquerytools_dest_path, FILENAME)
    dest = open(dest_filename, 'wb')
    print 'writing data to "%s"' % dest_filename
    dest.write(file_data)
    dest.close()
    os.mkdir(library_path)
    shutil.move(dest_filename, library_path)

def main():
    prepare_jquerytools()


def entrypoint(data):
    """Entry point for zest.releaser's prerelease script"""
    prepare_jquerytools()
