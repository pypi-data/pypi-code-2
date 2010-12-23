# me2/version.py
#
#

""" version related stuff. """

## me2 imports

from me2.lib.datadir import getdatadir

## basic imports

import os

## defines

version = "0.1 ALPHA1"

## getversion function

def getversion(txt=""):
    """ return a version string. """
    try: tip = open(getdatadir() + os.sep + "TIP", 'r').read()
    except: tip = None
    if tip: version2 = version + " " + tip
    else: version2 = version
    if txt: return "BOTME2 %s %s" % (version2, txt)
    else: return "BOTME2 %s" % version2
