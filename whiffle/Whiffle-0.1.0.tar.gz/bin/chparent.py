#!/usr/bin/python

import sys
from optparse import OptionParser
from whiffle import wikidotapi

def chparent(api, parent,child):
	print "Changing parent of '"+child+"' to '"+parent+"'"
	try:
		api.set_page_item(child, "parent_page", parent)
	except Exception as e:
		print "Error (", parent, child,"): ", e

parser = OptionParser(usage="%prog [options] parent child\n")
parser.disable_interspersed_args()
parser.add_option("-i", "--identity",
                  action="store", dest="identity", default="default",
                  help="Define the name of the wikidot user with permission to make the required change.")
parser.add_option("-f", "--file",
                  action="store", dest="filename", default=None,
                  help="define the name of the operations file", metavar="FILE")
(options, args) = parser.parse_args()

if options.filename==None:
	if len(args) < 2:
		parser.error("parent and child arguments are required.")
		sys.exit(1)
	else:
		f = None
else:
	f = open (options.filename, "r")

api = wikidotapi.connection(options.identity)

if f == None:
	chparent(api, args[0],args[1])
else:
	for l in f:
		p = l.find(" ")
		child = l[p+1:-1]
		parent = l[:p]
		chparent(api, parent,child)

#print "Done"

