#!/usr/bin/env python
#
# Copyright (c) 2009-2010 Alfredo Deza <alfredodeza [at] gmail [dot] com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import os
import optparse

class Pygora(object):
    """Discover the test files, read them line by line and then
    compare them with non-test code"""

    def __init__(self,
            path = os.getcwd(),
            match = False,
            verbose = False):
        self.path = path
        self.match = match
        self.verbose = verbose
        self.test_lines = 0
        self.source_lines = 0

    def locate_py(self):
        """Search for source and test files"""
        verbose = self.verbose

        for root, dirs, files in os.walk(self.path):
            for item in files:
                if self.match and self.match in item: continue
                if item.lower().endswith("py"):
                    absolute_path = os.path.join(root, item)
                    if "test" in item.lower():
                         lines = self.line_count(absolute_path)
                         self.test_lines += int(lines) 
                         if verbose:
                            print "Test lines:\t%s\t\t %s" % (lines, item)
                    else:
                         lines = self.line_count(absolute_path)
                         self.source_lines += int(lines) 
                         if verbose:
                            print "Python lines:\t%s\t\t %s" % (lines, item)

    def line_count(self, source_file):
        """Count all the code lines in a file"""
        count = 0
        open_file = open(source_file)
        skip  = self.skip_line 
        for line in open_file.read().split('\n'):
            if skip(line):
                count += 1
        return "%d" % count

    def skip_line(self, line):
        """Determines if this is a source line or something
        pygora should be skipping"""
        startswith = line.startswith('#')
        strip = line.strip()
        if startswith: #no lines with comments
            return False
        elif not strip: #do not count empty lines
            return False
        else:
            return True


def main():
    """Parse the options"""
    parse = optparse.OptionParser(description="Autodiscover Python code and\
compares source versus test code with a nice ratio/percentage as a result.\
Always run it on the working directory.",
    usage = "\npygora\n\
pygora --ignore [match]", version='0.0.3')
    parse.add_option("--ignore", help="Match file(s) to ignore when running")
    parse.add_option("--verbose","-v", action="store_true",
            help="Prints all the matching files with line numbers")
    parse.add_option("--path", help="Specify a path to report on")
    options, arguments = parse.parse_args()

    verbose = False
    match = False
    path = os.getcwd()

    if options.verbose:
        verbose = True 

    if options.ignore:
        match = options.ignore

    if options.path:
        path = os.path.abspath(options.path)

    run = Pygora(path=path, match=match, verbose=verbose)

    run.locate_py()
    total = run.test_lines + run.source_lines
    print "\nTest lines \t= %10s" % run.test_lines
    print "Source lines \t= %10s" % run.source_lines
    print "Total lines \t= %10d" % total

    #lets get a nice percentage:
    if run.source_lines == 0:
        print '\nYour test code is 100% of your source code\n'
    else:
        percentage = float(run.test_lines * 100.00 / run.source_lines)
        print '\nYour test code is %.2f%% of your source code\n' % percentage

if __name__ == "__main__":
    main()


