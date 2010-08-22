#!/usr/bin/env python
"""
This example demonstrates the internal working of ec-sorter.
"""

"""
pycallgraph

Derivative of examples filter.py and regex.py.

U{http://pycallgraph.slowchop.com/}

Copyright Gerald Kaszuba 2007
Copyright Arpad Horvath 2008

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""

import pycallgraph
import sys
sys.path.append('/home/ha/num/complex_networks/packages')


def main():
    filter_func = pycallgraph.GlobbingFilter(exclude=['re.*',
      'sre_parse.*', 'sre_compile.*',
      'stat.*', 'string.*',
      'getopt.*', 'posixpath.*',
      'pycallgraph.*',
      '__main__'
      ])
    pycallgraph.start_trace(filter_func=filter_func)
    import packages
    pycallgraph.make_dot_graph('packages-callgraph.png')
    print "See packages-callgraph.png"

if __name__ == '__main__':
    main()

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
