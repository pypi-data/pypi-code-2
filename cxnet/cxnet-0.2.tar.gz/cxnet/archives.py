#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
It pull (and will put) network data from (and to) archives.
"""

import urllib
import zipfile
import os

def get_netdata(archive_name=None):
    """Get network data from archives.
    """

    baseurls = (
            "http://mail.roik.bmf.hu/cxnet/netdata/",
            "http://www-personal.umich.edu/~mejn/netdata/",
            )
    unzip = True

# The first item of the values is an url list or an url.
# The second item of the values is the list of file names without zip extension,
#   or False. If it is False it downloads first the file_list.txt
#   and get he file name from it.
    network_archives = {
            "newman": (baseurls,
                """karate lesmis adjnoun football
                 dolphins polblogs polbooks celegansneural
                 power cond-mat cond-mat-2003 cond-mat-2005
                 astro-ph hep-th netscience as-22july06""".split()
                 ),
            "deb_files": (
                baseurls[:1], 
                """ubuntu-10.04-packages-2010-08-19
                ubuntu-9.10-packages-2010-07-16
                ubuntu-9.10-packages-2010-07-22
                """.split()
                ), #False means you need to download the list from the server.
            }

    if archive_name is None or archive_name not in network_archives.keys():
        print """You need to choose an archive name.
Archives are:"""
        for i in network_archives.keys():
            print "- %s" % i
        return

    try:
        os.mkdir("netdata_zip")
    except OSError:
        pass # directories exists
    try:
        os.mkdir("netdata")
    except OSError:
        pass # directories exists

    baseurls, networks = network_archives[archive_name]
    for net in networks:
        zipfile_name = "%s.zip" % net
        baseurl=baseurls[0]
        url = "%s%s" % (baseurl, zipfile_name)
        stored_zipfile = "netdata_zip/%s" % zipfile_name
        urllib.urlretrieve(url, stored_zipfile)
        print stored_zipfile
        if unzip:
            zf = zipfile.ZipFile(stored_zipfile)
            print zf.namelist()
            zf.extractall("netdata")

def put_debnetdata():
    """Put the data of debian package dependency network into the archive.
    """
    print """Send them to Arpad Horvath <horvath.arpad@arek.uni-obuda.hu>."""

if __name__ == "__main__":
    get_netdata()
