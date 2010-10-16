#!python

# HtmlList - Finds repetitive format patterns in an HTML page.
# Copyright (C) 2010  Erez Bibi (erezbibi@users.sourceforge.net)
#
# This file is part of HtmlList.
#
# HtmlList is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# HtmlList is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with HtmlList.  If not, see <http://www.gnu.org/licenses/>.

"""
When run as a stand-alone this module creates a quick and dirty way to break
pages from a web browser in order to test this package.
The user should save web browser pages to a folder. The script runs in the
background, monitors this folder and will process files in it. Then it tries to
open the result as an HTML page again using a web browser.

If the option "--std" is given on the command line, it will process an HTML text
from the standard input and print the output to the standard output.

It process the page using all (enabled) algorithms and print the best X results
from each one. The results will be sorted by a relevance factor (which hopefully
works well)

try: htmllist_demo.py --help
to see all options
"""
# TODO: I have hell of a time with the unicode here

from __future__ import with_statement
from glob import iglob
from webbrowser import open as web_open
from sys import argv
from optparse import OptionParser, OptionGroup
import os, time, re, sys, cPickle

# NOTE: Python 2.6 Only
from collections import namedtuple

from htmllist_break import HtmlListBreak
from utills import strip_tags, strip_scripts, unquote_html, quote_html
from pattern_quality import pattern_quality
from algo_dict import algo_dict, update_algo_dict

## Default Configuration ##

EXCLUDE_TAGS = "b,u,i,em" # Comma separated tags names
INCLUDE_TAGS = None
# Each of these options is over written by the equivalent command line argument
# or the equivalent argument in algo_dict (or the external supplied dictionary)
MIN_LEN = 1
MAX_LEN = 20
MIN_REPEAT = 3
MAX_REPEAT = 60
MAX_STDV = 0.5
MIN_WEIGHT = 0.0
MIN_COVERAGE = 0.0 #0.1
MIN_COMPACTNESS = 0.0
MAX_PATTERNS = 1

## Configuration for this script only ##
MAX_AVG_WORDS = 300 # Limit on the average number of words in an HTML section
MIN_AVG_WORDS = 5
MIN_FACTOR = 0.01

WORDS_IN_TITLE = 6 # This is for the output XML titles of the HTML sections
SLEEP = 0.5

def get_options_parser():
	""" Return the command line arguments parser. """
	parser = OptionParser(description=" ".join(main.__doc__.split()))
	parser.add_option("-m", "--monitor", action="store", type="string",
		default="./temp", dest="monitor",
		help="""Directory to monitor [default: %default]""")
	parser.add_option("-o", "--outfile", action="store", type="string",
		default="./temp", dest="outfile", help="""The name of the output file
[default: %default]""")
	parser.add_option("-f", "--format", action="store", type="string",
		dest="format", default="html", help="""Output format, also the type of
the output file (html|xml)""")
	parser.add_option("-i", "--infile", action="store", type="string",
		dest="infile", help="""Optional input file. Mutual exclusive to
--monitor, --std, --test""")
	parser.add_option("-s", "--std", action="store_true", dest="std", default=False,
		help="""Get the input HTML from the standard input and write the output
to the standard output, mutual exclusive to --monitor, --output and --test
[default: %default]""")
	parser.add_option("-b", "--browser", action="store_false", dest="browser",
		default=True, help="""Open output file in a web-browser [default: %default]""")
	parser.add_option("-v", "--verbose", action="store", type="int", default="0",
		dest="verbose",  help="""Verbose mode (level 0-5) [default: %default]""")

	group = OptionGroup(parser, "Script Configuration",
		"""Pass custom configuration to this script.""")
	group.add_option("--algo_dict", action="store", type="string",
		dest="algo_dict", help="""Path to a file that defines a dictionary to
update the algorithms configuration (see "algo_dict.py" documentation)""")
	group.add_option("--max_words", action="store", type="int",
		dest="max_words", help="""Maximum average number of words in an HTML
section [default: %s]""" % MAX_AVG_WORDS)
	group.add_option("--min_words", action="store", type="int",
		dest="min_words", help="""Minimum average number of words in an HTML
section [default: %s]""" % MIN_AVG_WORDS)
	group.add_option("--min_factor", action="store", type="float",
		dest="min_factor", help="""Minimum pattern factor [default: %s]""" \
		% MIN_FACTOR)
	parser.add_option_group(group)

	group = OptionGroup(parser, "HTML List Configuration",
		"""Pass custom configuration to the htmllist package (See documentation
for help). For updating specific algorithm configuration use the "algo_dict"
option.""")
	group.add_option("--include_tags", action="store", type="string",
		default=INCLUDE_TAGS, dest="include_tags", help="[default: %default]")
	group.add_option("--exclude_tags", action="store", type="string",
		default=EXCLUDE_TAGS, dest="exclude_tags", help="[default: %default]")
	group.add_option("--min_len", action="store", type="int",
		dest="min_len", help="[default: %s]" % MIN_LEN)
	group.add_option("--max_len", action="store", type="int",
		dest="max_len", help="[default: %s]" % MAX_LEN)
	group.add_option("--min_repeat", action="store", type="int",
		dest="min_repeat", help="[default: %s]" % MIN_REPEAT)
	group.add_option("--max_repeat", action="store", type="int",
		dest="max_repeat", help="[default: %s]" % MAX_REPEAT)
	group.add_option("--max_stdv", action="store", type="float",
		dest="max_stdv", help="[default: %s]" % MAX_STDV)
	group.add_option("--min_weight", action="store", type="float",
		dest="min_weight", help="[default: %s]" % MIN_WEIGHT)
	group.add_option("--min_coverage", action="store", type="float",
		dest="min_coverage", help="[default: %s]" % MIN_COVERAGE)
	group.add_option("--min_comp", action="store", type="float",
		dest="min_comp", help="[default: %s]" % MIN_COMPACTNESS)
	group.add_option("--max_patterns", action="store", type="int",
		dest="max_patterns", help="[default: %s]" % MAX_PATTERNS)
	parser.add_option_group(group)

	group = OptionGroup(parser, "For Regression Tests",
		"""Normal user should not use these options (See documentation for help)""")
	group.add_option("--test", action="store_true", dest="test",
		default=False, help="""Create a regression test [default:%default]""")
	parser.add_option_group(group)

	return parser

def prepare(options, pattern_cls, break_cls=None):
	""" Create an HtmlList object  by the algorithm name """
	hl = HtmlListBreak(pattern_cls=pattern_cls, break_cls=break_cls)
	conf = algo_dict[pattern_cls]
	if not options.std:
		print "using the %s algorithm" % conf.name

	if options.exclude_tags:
		hl.exclude_tags += options.exclude_tags.split(',')
	if options.include_tags:
		hl.include_tags += options.include_tags.split(',')

	hl.min_len = options.min_len or conf.min_len or MIN_LEN
	hl.max_len = options.max_len or conf.max_len or MAX_LEN
	hl.min_repeat = options.min_repeat or conf.min_repeat or MIN_REPEAT
	hl.max_repeat = options.max_repeat or conf.max_repeat or MAX_REPEAT
	hl.max_stdv = options.max_stdv or conf.max_stdv or MAX_STDV
	hl.min_weight = options.min_weight or conf.min_weight or MIN_WEIGHT
	hl.min_coverage = options.min_coverage or conf.min_coverage or MIN_COVERAGE
	hl.min_comp = options.min_comp or conf.min_comp or MIN_COMPACTNESS
	hl.max_patterns = options.max_patterns or conf.max_patterns or MAX_PATTERNS
	hl.debug_level = options.verbose
	return hl

def find_title(html):
	""" Find a possible title for this HTML section (XML version only). """
	text = strip_scripts(html)
	text = strip_tags(text, " ")
	lst = text.split(None, WORDS_IN_TITLE)
	title = quote_html(' '.join(lst[:WORDS_IN_TITLE]))
	if len(lst) > WORDS_IN_TITLE:
		title += " ..."
	return title

def orderd_htmllists(hls):
	""" A generator for html-lists ordered by the quality and the factor.
	"""
	TmpData = namedtuple("TmpData",
		["hl", "hl_index", "data", "factor", "quality", "avrg_words"])
	lst = [TmpData(hl, i, algo_dict[hl.pattern_cls.__class__],
			hl.factor, pattern_quality(hl.pattern_cls, hl.break_cls),
			hl.avrg_words_in_section()) \
			for hl in hls for i in hl]

	# TODO: Decide here...
	lst = filter(lambda x: True
		and x.quality >= x.data.min_quality \
		and x.avrg_words < MAX_AVG_WORDS and x.avrg_words > MIN_AVG_WORDS \
		and x.factor > MIN_FACTOR \
		, lst)
	lst.sort(key=lambda x: (
		#x.data.order,
		#x.quality * -1,
		#x.factor * -1,
		x.quality * x.factor * x.data.algo_factor * -1,
		#x.avrg_words * -1,
	))

	for item in lst:
		# Setting pattern_num value has the same effect as iterating through
		# the HtmlList object
		hl = item.hl
		hl.pattern_num = item.hl_index
		hl.algo_name = item.data.name
		hl.quality = item.quality
		hl.avrg_words = item.avrg_words
		yield hl


def print_html(hls, fl):
	""" Build an HTML version of the list and write it to the file object 'fl'. """
	fl.write(u"<HTML><HEAD><TITLE>Html-List Breakdown</TITLE></HEAD><BODY><DIV>\n\n")
	for hl in orderd_htmllists(hls):
		lst = hl.get_html_list()
		if not lst or not hl.is_list_valid: continue
		fl.write(u"""\n</DIV><HR>===
			Algorithm: %s (Factor=%s, Quality=%s, AvrgWord=%s, Duration=%s)
			===<HR><DIV>\n""" % (hl.algo_name, round(hl.factor, 3),
				round(hl.quality, 3), round(hl.avrg_words, 1),
				round(hl.duration, 3)))
		for sub in lst:
			fl.write(sub)
			fl.write(u"\n</DIV><HR><DIV>\n")
	fl.write(u"\n</DIV></BODY></HTML>")

def print_xml(hls, fl):
	""" Build an XML version of the list and write it to the file object 'fl'. """
	fl.write(u'<?xml version="1.0"?>\n')
	fl.write(u'\n<LISTS>\n')
	for hl in orderd_htmllists(hls):
		lst = hl.get_html_list()
		if not lst or not hl.is_list_valid: continue
		fl.write(u'\n<SECTIONS algo="%s" factor="%s" quality="%s" avrg_word="%s" duration="%s">' % \
			(hl.algo_name, round(hl.factor, 3),  round(hl.quality, 3),
			round(hl.avrg_words, 1), round(hl.duration, 3)))
		for sub in lst:
			fl.write(u'\n\t<SECTION>\n\t<TITLE>\n\t\t')
			fl.write(find_title(sub))
			fl.write(u'\n\t</TITLE> \n\t<HTML><![CDATA[\n')
			fl.write(sub.replace("]]>", "]]->"))
			fl.write(u'\n\t]]></HTML>\n\t</SECTION>\n')
		fl.write(u'\n</SECTIONS>\n')
	fl.write(u'\n</LISTS>\n')

def process(fl, options):
	""" Process an HTML file, returns a list of iterators """
	results = []
	text = fl.read()
	count = 0
	for cls in algo_dict.keys():
		if not algo_dict[cls].enabled: continue
		if count == 0:
			hl = prepare(options, cls)
			hl.set_text(text)
		else:
			hl = prepare(options, cls, break_cls=hl.break_cls)
		count += 1
		start = time.time()
		hl.process()
		hl.duration = time.time() - start # Only for tracking performance
		results.append(hl)
	return results

def process_std(options):
	""" Run the script once on stdin, the output goes to sdtout. """
	hls = process(sys.stdin, options.old, options)
	options.browser = False
	output_results(hls, options, out=sys.stdout)

def output_results(hls, options, out=None):
	""" Main function to output the results
	out is an optional file-object to output the results to, if it is not given
	it will output the results to a file named <options.outfile>.<options.format>
	"""
	if not out:
		outfile = options.outfile + '.' + options.format
		out = open(outfile, "wb")
	if options.format.lower() == "xml":
		print_xml(hls, out)
	else:
		print_html(hls, out)
	out.close()

	if options.browser:
		web_open("file://%s" % os.path.abspath(outfile), new=2, autoraise=1)

def main(argv):
	""" A quick and dirty way to process HTML pages from a web browser. Save
	pages as "HTML only" to the MONITOR directory. The script runs in the
	background, will process these files, and reopen the result page.
	In addition the user can supply an input and/or output file names, or work
	from the stdin/stdout.
	There are also options to change the default configuration of the package.
	"""
	global algo_dict, MAX_AVG_WORDS, MIN_AVG_WORDS, MIN_FACTOR

	options, args = get_options_parser().parse_args(argv)

	if options.algo_dict:
		algo_dict = update_algo_dict(options.algo_dict)
	if options.max_words:
		MAX_AVG_WORDS = options.max_words
	if options.min_words:
		MIN_AVG_WORDS = options.min_words
	if options.min_factor:
		MIN_FACTOR = options.min_factor

	if options.std:
		process_std(options)
	elif options.infile:
		with open(options.infile) as html_file:
			hls = process(html_file, options)
			output_results(hls, options)
	else:
		if not os.path.isdir(options.monitor):
			os.mkdir(options.monitor)
		print "Save web pages as 'HTML Only' to:", os.path.abspath(options.monitor)
		print "Waiting..."
		while True: #  Poll a folder indefinitely (need to work on Windows too:)
			time.sleep(SLEEP)
			for fl in iglob(options.monitor + "/*"):
				# If file exists - process, open in browser and delete them
				print "Handling:", fl
				with open(fl) as html_file:
					start = time.time()
					hls = process(html_file, options)
					duration = time.time() - start
					if options.test:
						hl = orderd_htmllists(hls).next()
						lst = hl.get_html_list()
					output_results(hls, options)
				print "Processing took:", duration
				if options.test:
					with open("temp.rslt", "wb") as rslt:
						cPickle.dump(lst, rslt)
						cPickle.dump(hl.algo_name, rslt)
						cPickle.dump(options, rslt)
					return
				os.remove(fl)
				print "Waiting..."

if __name__ == '__main__':
	main(sys.argv)

