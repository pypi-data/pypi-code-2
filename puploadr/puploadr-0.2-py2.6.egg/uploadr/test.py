#! /usr/bin/python

import shelve
from configobj import ConfigObj
# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__ = "elek"
__date__ = "$Oct 15, 2010 8:37:28 PM$"

if __name__ == "__main__":
    d = shelve.open("/tmp/uploadr.history")
    with open("/tmp/flickr.photos","w") as f:
        n = ConfigObj()
        for k, v in d.iteritems():
            if k.startswith("/home"):
                img = k[k.rfind("/")+1:]
                n[img] = v
        n.write(f)
