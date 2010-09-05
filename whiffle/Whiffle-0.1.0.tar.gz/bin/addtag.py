#!/usr/bin/python

import sys
from optparse import OptionParser
from whiffle import wikidotapi

def dotag(api, page, tag, remove):
	if remove:
		removetag(api, page, tag)
	else:
		addtag(api, page, tag)
		
def addtag(api, page, tag):
	print "Adding tag '"+tag+"' to '"+page+"'"
	try:
		api.add_tag(page, tag, ErrorIfRedundant=False)
	except Exception as e:
		print "Error (", page, "add", tag,"): ", e

def removetag(api, page, tag):
	print "Removing tag '"+tag+"' from '"+page+"'"
	try:
		api.remove_tag(page, tag, ErrorIfRedundant=False)
	except Exception as e:
		print "Error (", page, "remove", tag,"): ", e

parser = OptionParser(usage="%prog [options] page [tag]\nAdds or removes tags from Wikidot pages.")
parser.disable_interspersed_args()
parser.add_option("-i", "--identity",
                  action="store", dest="identity", default="default",
                  help="define the name of the entry in the identity.ini file to use. The default is 'default'.")
parser.add_option("-r", "--remove",
                  action="store_true", dest="remove", default=False,
                  help="remove the specified tag (default action is to add it).")
parser.add_option("-f", "--file",
                  action="store", dest="filename", default=None,
                  help="define the name of the a file, each line of which contains <page>SPACE<tag> or just <page>. "+
		  "If <tag> is not specified on any line, then the one specified on the command line is used. "+
		  "If every line specifies a tag, then a tag is not required on the command line.", metavar="FILE")
(options, args) = parser.parse_args()

if options.filename==None:
	if len(args) < 2:
		parser.error("page and tag arguments are required unless a file is specified.")
		sys.exit(1)
	else:
		page = args[0]
		tag = args[1]
		f = None
else:
	f = open (options.filename, "r")

	if len(args) < 1:
		page = None
		tag = None
	else:
		page = None
		tag = args[0]


api = wikidotapi.connection(options.identity)

if f == None:
	dotag(api, page, tag, options.remove)
else:
	i = 0
	for l in f:
		i = i + 1
		words = l.split()
		if len(words) == 2:
			dotag(api, words[0], words[1], options.remove)
		elif len(words) == 1:
			if tag == None:
				print "Line", i,"does not contain a tag, and no tag is specified on the command line"
				sys.exit(1)
			dotag(api, words[0], tag, options.remove)
		elif len(words) != 0:
			print "Line", i,"does not contain either a page and a tag or just a page"
			sys.exit(1)

