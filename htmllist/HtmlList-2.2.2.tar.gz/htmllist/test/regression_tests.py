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
This module creates and run regression tests.
When it is run without arguments it let you create a new test using the
htmllist_demo script, and save it under a name.
When run with an argument, the argument should be a saved test name. if the
argument is "all", it will run all saved tests. If adding an "accept" argument
after a test name, it will accept the current results of this test and save them.

usage: regression_tests.py [test-name|"all" ["accept"] [debug-level]]

This script can be run from the main htmllist directory as
"test/regression_tests.py"
"""

from __future__ import with_statement
from glob import iglob
from sys import argv, path
import os, cPickle

cur_dir = os.getcwd()
if cur_dir.endswith("test"):
	test_dir = cur_dir
	main_dir = os.path.dirname(cur_dir)
else:
	test_dir = os.path.join(cur_dir, "test")
	main_dir = cur_dir

path.append(main_dir)
from htmllist_demo import process, orderd_htmllists
from utills import not_empty_iter

TEMP_DIR = "temp"
HTML_EXT = "html"
RESULT_EXT = "rslt"
RESULT_FILE = "temp." + RESULT_EXT


class Config: pass

def get_new_config():
	""" Get configuration data from user """
	config = Config() # So I can pickle it
	config.include_tags = raw_input("Include Tags (comma separated w/o spaces): ")
	config.exclude_tags = raw_input("Exclude Tags: ")
	config.min_len = raw_input ("Minimum Length (int): ")
	config.min_repeat = raw_input("Minimum Repeats (int > 1): ")
	config.max_repeat = raw_input("Maximum Repeats (int 0 = no limit): ")
	config.max_stdv = raw_input("Maximum STDV (float 0-1): ")
	return config

def make_new_test():
	""" Long function that basically run the htmllist_demo script and save the
	input and output if the user choose to.
	"""
	# Configure
	change = raw_input("Do you want to change the default configuration (Y/N)? ")
	config = None
	if change.lower() == 'y':
		config = get_new_config()
	# Build the command line for htmllist_demo
	command = "python htmllist_demo.py --test "
	if config:
		if config.include_tags:
			command += " --include_tags=%s" % config.include_tags
		if config.exclude_tags:
			command += " --exclude_tags=%s" % config.exclude_tags
		if config.min_len:
			command += " --min_len=%s" % config.min_len
		if config.min_repeat:
			command += " --min_repeat=%s" % config.min_repeat
		if config.max_repeat:
			command += " --max_repeat=%s" % config.max_repeat
		if config.max_stdv:
			command += " --max_stdv=%s" % config.max_stdv
	command += " --verbose=1"
	# Build the test
	print "Save an HTML page to the %s directory" % TEMP_DIR
	os.chdir(main_dir)
	print ">>>", command
	os.system(command)
	html_file = "%s/%s" % (TEMP_DIR, os.listdir(TEMP_DIR)[0])
	ok = raw_input("Is it good (Y/N)?")
	if ok.lower() == 'y':
		while True:
			name = raw_input("What do you want to call this test? ")
			if os.path.exists("%s/%s.%s" % (cur_dir, name, HTML_EXT)):
				delete = raw_input("This test already exists, replace it (Y/N)? ")
				if not delete.lower() == 'y':
					continue
				os.remove("%s/%s.%s" % (cur_dir, name, HTML_EXT))
				os.remove("%s/%s.%s" % (cur_dir, name, RESULT_EXT))
			break
		os.rename(html_file, "%s/%s.%s" % (cur_dir, name, HTML_EXT))
		os.rename(RESULT_FILE, "%s/%s.%s" % (cur_dir, name, RESULT_EXT))
	else:
		os.remove(html_file)
		os.remove(RESULT_FILE)
	os.chdir(cur_dir)

def run_test(name, debug=0, for_profiling=False, repair=False):
	""" Run a specific test. Compare the saved result to the result from the
	HtmlList package.

	for_profiling - Will process the file w/o testing.
	repair - Will save the current processing results.
	"""
	assert os.path.exists("%s/%s.%s" % (test_dir, name, RESULT_EXT)), \
		"%s: No Results Defined" % name
	fl = open("%s/%s.%s" % (test_dir, name, HTML_EXT))
	with open("%s/%s.%s" % (test_dir, name, RESULT_EXT)) as test_data:
		lst = cPickle.load(test_data)
		algo_name = cPickle.load(test_data)
		config = cPickle.load(test_data)
		config.verbose = debug
	hls = process(fl, config)
	tmp_itr = not_empty_iter(orderd_htmllists)(hls)
	if not tmp_itr:
		assert False, "%s: Test Failed - Empty Results" % name
	hl = tmp_itr.next()
	itr = hl.get_html_list()
	if repair:
		with open("%s/%s.%s" % (test_dir, name, RESULT_EXT), "wb") as rslt:
			cPickle.dump(tuple(itr), rslt)
			cPickle.dump(hl.algo_name, rslt)
			cPickle.dump(config, rslt)
	elif not for_profiling:
		if itr and lst:
			itr = tuple(itr)
			assert lst == itr, "%s: Test Failed - Different results" % name
		elif lst:
			assert False, "%s: Test Failed - Before got results" % name
		elif itr:
			assert False, "%s: Test Failed - Now got results" % name
		print name, "Passed"

def run_all_tests(debug):
	""" Run all test in the directory by searching for files with .html
	extension.
	"""
	tests = iglob("%s/*.%s" % (test_dir, HTML_EXT))
	failed = []
	for test in tests:
		name = os.path.basename(test)[:-1 * (len(HTML_EXT) + 1)]
		print "Running:", name
		try:
			run_test(name, debug)
		except AssertionError, msg:
			print msg
			failed.append(name)
	if failed:
		print "\n===", len(failed), "Test Failed ==="
		for name in failed:
			print "\t", name
	else:
		print "\n=== All Tests Passed ==="

if __name__ == '__main__':
	if len(argv) > 1:
		debug = 0
		if argv[-1].isdigit():
			debug = int(argv[-1])
		if argv[1] == 'all':
			run_all_tests(debug)
		else:
			accept =  len(argv) > 2 and argv[2] == "accept"
			run_test(argv[1], debug, repair=accept)
	else:
		make_new_test()

