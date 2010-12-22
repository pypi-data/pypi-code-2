#! /usr/bin/env python
import urllib2
import sys

def fetch_book(address):
    f = urllib2.urlopen(address)
    print f.read()


if __name__ == "__main__":
    fetch_book(sys.argv[1])