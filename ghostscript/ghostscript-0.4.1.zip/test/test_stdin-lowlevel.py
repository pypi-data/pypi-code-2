#!/usr/bin/env python
"""

Test program for stdout callbacks.

"""
# -*- coding: utf-8 -*-
#
# Copyright 2010 by Hartmut Goebel <h.goebel@goebel-consult.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

__author__ = "Hartmut Goebel <h.goebel@goebel-consult.de>"
__copyright__ = "Copyright 2010 by Hartmut Goebel <h.goebel@goebel-consult.de>"
__licence__ = "GNU General Public License version 3 (GPL v3)"

import StringIO
import sys
import ghostscript._gsprint as gs

postscript_doc = "0 0 moveto (Hello World) show showpage"

args = """test.py -dSAFER
       -sDEVICE=bmp16 -g10x10 -sOutputFile=- -
       """.split()

instance = gs.new_instance()

stdout = StringIO.StringIO() # create buffer for collecting output

stdin = StringIO.StringIO(postscript_doc)

# wrappers like in http://pages.cs.wisc.edu/~ghost/doc/cvs/API.htm#set_stdio
gsdll_stdin  = gs._wrap_stdin(stdin)
gsdll_stdout = gs._wrap_stdout(stdout)
gsdll_stderr = gs._wrap_stderr(sys.stderr)

gs.set_stdio(instance, gsdll_stdin, gsdll_stdout, gsdll_stderr)

gs.init_with_args(instance, args)
#gs.run_string(instance, postscript_doc)
gs.delete_instance(instance)

# print data collected from ghostscripts stdout
print 'Read data', repr(stdout.getvalue())
