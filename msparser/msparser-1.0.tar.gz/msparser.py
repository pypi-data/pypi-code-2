# Copyright (c) 2011 Mathieu Turcotte (mathieuturcotte.ca)
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
# The Software shall be used for Good, not Evil.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
Massif Parser
=============

:Author: Mathieu Turcotte

The msparser module offers a simple interface to parse the Valgrind massif.out
file format, i.e. data files produced the Valgrind heap profiler.

How do I use it?
----------------

Import the Module
`````````````````
As usual, import the module::

    >>> import msparser

Parse a massif.out File
```````````````````````
To extract the data from a massif.out file, you simply have to give its path to the ``parse_file`` function::

    >>> data = msparser.parse_file('massif.out')

You could also use the ``msparser.parse`` function directly with a file descriptor.

Understand the Data
```````````````````

The parsed data is returned as a dictionary which follow closely the massif.out
format. It looks like this::

    >>> from pprint import pprint
    >>> pprint(data, depth=1)
    {'cmd': './a.out',
     'desc': '--time-unit=ms',
     'detailed_snapshots_index': [...],
     'peak_snapshot_index': 16,
     'snapshots': [...],
     'time_unit': 'ms'}

The ``detailed_snapshots_index`` and ``peak_snapshot_index`` fields allow
efficient localisation of the detailled and peak snapshots in the ``snapshots``
list. For example, to retrieve the peak snapshot from the ``snapshots`` list,
we could do::

    >>> peak_index = data['peak_snapshot_index']
    >>> peak_snapshot = data['snapshots'][peak_index]

The ``snapshots`` list stores dictionaries representing each snapshot data::

    >>> second_snapshot = data['snapshots'][1]
    >>> pprint(second_snapshot)
    {'heap_tree': None,
     'id': 1,
     'mem_heap': 1000,
     'mem_heap_extra': 8,
     'mem_stack': 0,
     'time': 183}

If the snapshot is detailled, the ``heap_tree`` field, instead of being None,
will store a heap tree::

    >>> peak_heap_tree = peak_snapshot['heap_tree']
    >>> pprint(peak_heap_tree, depth=3)
    {'children': [{'children': [...], 'details': {...}, 'nbytes': 12000},
                  {'children': [], 'details': {...}, 'nbytes': 10000},
                  {'children': [...], 'details': {...}, 'nbytes': 8000},
                  {'children': [...], 'details': {...}, 'nbytes': 2000}],
     'details': None,
     'nbytes': 32000}

On the root node, the ``details`` field is always None, but on the children
nodes it's a dictionary which looks like this::

    >>> first_child = peak_snapshot['heap_tree']['children'][0]
    >>> pprint(first_child['details'], width=1)
    {'address': '0x8048404',
     'file': 'prog.c',
     'function': 'h',
     'line': 4}

Obviously, if the node is below the massif threshold, the ``details`` field
will be None.

Putting It All Together
```````````````````````
From this data structure, it's very easy to write a procedure that produce a
data table ready for Gnuplot consumption::

    print("# valgrind --tool=massif", data['desc'], data['cmd'])
    print("# id", "time", "heap", "extra", "total", "stack", sep='\t')
    for snapshot in data['snapshots']:
        id = snapshot['id']
        time = snapshot['time']
        heap = snapshot['mem_heap']
        extra = snapshot['mem_heap_extra']
        total = heap + extra
        stack = snapshot['mem_stack']
        print('  '+str(id), time, heap, extra, total, stack, sep='\t')

The output should looks like this::

    # valgrind --tool=massif --time-unit=ms ./a.out
    # id    time    heap    extra   total   stack
      0     0       0       0       0       0
      1     183     1000    8       1008    0
      2     184     2000    16      2016    0
      3     184     3000    24      3024    0
      4     184     4000    32      4032    0
      5     184     5000    40      5040    0
      6     184     6000    48      6048    0
      7     184     7000    56      7056    0
      8     184     8000    64      8064    0
      9     184     9000    72      9072    0
"""

import os, sys, re

__all__ = ["parse", "parse_file"]

_COMMENT_RE = re.compile("\s*#")

# Precompiled regex used to parse various massif.out data fields.
_FIELD_DESC_RE = re.compile("desc:\s(?P<data>\S+)")
_FIELD_CMD_RE = re.compile("cmd:\s(?P<data>\S+)")
_FIELD_TIME_UNIT_RE = re.compile("time_unit:\s(?P<data>ms|B|i)")
_FIELD_SNAPSHOT_RE = re.compile("snapshot=(?P<data>\d+)")
_FIELD_TIME_RE = re.compile("time=(?P<data>\d+)")
_FIELD_MEM_HEAP_RE = re.compile("mem_heap_B=(?P<data>\d+)")
_FIELD_MEM_EXTRA_RE = re.compile("mem_heap_extra_B=(?P<data>\d+)")
_FIELD_MEM_STACK_RE = re.compile("mem_stacks_B=(?P<data>\d+)")
_FIELD_HEAP_TREE_RE = re.compile("heap_tree=(?P<data>\w+)")

# Extract number of children, number of bytes and details section.
#   n1: 0 0x804F50A: function_name (function_file:114)"
_HEAP_ENTRY_RE = re.compile("\s*n(?P<num_children>\d+):\s*(?P<num_bytes>\d*)\s*(?P<details>.*)")

# Need to handle three cases when parsing the details section:
#   0x804F50A: function_name (function_file.cpp:114)
#   0x804F50A: function_name (in usr/local/bin/foo)
#   in 2 places, all below massif's threshold (01.00%)
_HEAP_DETAILS_RE = re.compile(r"""
        (?P<address>[a-fA-f0-9x]+)  # match the hexadecimal address
        :\s                         # skip ': '
        (?P<function>.+)            # match the function name
        \s\(
        (?:in\s)?                   # skip 'in ' if present
        (?P<fname>[^:]+)            # match the file name, non-greedy
        :?                          # skip ':', if present
        (?P<line>\d+)?              # match the line number, if present
        \)
""", re.VERBOSE)

_HEAP_BELOW_THRESHOLD_RE = re.compile(r"""in.*places?.*""")

class ParsingError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return "ParsingError: " + str(self.value)

def parse_file(filepath):
    """
    Convenience function taking a file path instead of a file descriptor.
    """
    with open(filepath) as fd:
        return parse(fd) # may throw

def parse(fd):
    """
    Parse an already opened massif output file.

    """
    mdata = {}
    mdata['snapshots'] = []
    mdata['detailed_snapshots_index'] = []

    # Parse header data.
    mdata['desc'] = _get_next_field(fd, _FIELD_DESC_RE)
    mdata['cmd'] = _get_next_field(fd, _FIELD_CMD_RE)
    mdata['time_unit'] = _get_next_field(fd, _FIELD_TIME_UNIT_RE)

    while _get_next_snapshot(fd, mdata):
        continue

    return mdata

def _get_next_line(fd, may_reach_eof=False):
    """
    Read another line from fd. If may_reach_eof is False, reaching EOF will
    be considered as an error.
    """
    line = fd.readline()
    # Readline return an empty string on EOF.
    if len(line) == 0:
        if may_reach_eof is False:
            raise ParsingError("unexpected EOF")
        else:
            return None
    else:
        return line.strip('\n')

def _get_next_field(fd, field_regex, may_reach_eof=False):
    """
    Read the next data field. The field_regex arg is a regular expression that
    will be used to match the field. Data will be extracted from the MatchObject
    by calling m.group('data'). If may_reach_eof is False, reaching EOF will
    be considered as an error.
    """
    line = _get_next_line(fd, may_reach_eof)
    while line:
        if _COMMENT_RE.match(line):
            line = _get_next_line(fd, may_reach_eof)
        else:
            match = field_regex.match(line)
            # If we have no match, it's an error.
            if match is None:
                raise ParsingError("".join(["can't match field against", line]))

            return match.group('data')

    return None

def _get_next_snapshot(fd, mdata):
    """
    Parse another snapshot, appending it to the mdata['snapshots'] list. On EOF,
    False will be returned.
    """
    snapshot_id = _get_next_field(fd, _FIELD_SNAPSHOT_RE, may_reach_eof=True)

    if snapshot_id is None:
        return False

    snapshot_id = int(snapshot_id)
    time = int(_get_next_field(fd, _FIELD_TIME_RE))
    mem_heap = int(_get_next_field(fd, _FIELD_MEM_HEAP_RE))
    mem_heap_extra = int(_get_next_field(fd, _FIELD_MEM_EXTRA_RE))
    mem_stacks = int(_get_next_field(fd, _FIELD_MEM_STACK_RE))
    heap_tree = _get_next_field(fd, _FIELD_HEAP_TREE_RE)

    # Handle the heap_tree field.
    if heap_tree != "empty":
        if heap_tree == "peak":
            mdata['peak_snapshot_index'] = snapshot_id
        heap_tree = _parse_heap_tree(fd)
        mdata['detailed_snapshots_index'].append(snapshot_id)
    else:
        heap_tree = None

    mdata['snapshots'].append({
        "id":snapshot_id,
        "time":time,
        "mem_heap":mem_heap,
        "mem_heap_extra":mem_heap_extra,
        "mem_stack":mem_stacks,
        "heap_tree":heap_tree
    })

    return True

def _parse_heap_tree(fd):
    """
    Parse a snapshot heap tree.
    """

    line = _get_next_line(fd)
    matches = _HEAP_ENTRY_RE.match(line)
    if matches is None:
        raise ParsingError("can't match heap tree entry: '" + line + "'")

    children = []
    for i in range(0, int(matches.group("num_children"))):
        children.append(_parse_heap_node(fd))

    root_node = {}
    root_node['details'] = None
    root_node['nbytes'] = int(matches.group("num_bytes"))
    root_node['children'] = children

    return root_node

def _parse_heap_node(fd):
    """
    Parse a normal heap tree node.
    """

    line = _get_next_line(fd)
    entry = _HEAP_ENTRY_RE.match(line)
    if entry is None:
        raise ParsingError("".join(["can't match heap tree entry: '", line, "'"]))

    details = entry.group('details')
    if _HEAP_BELOW_THRESHOLD_RE.match(details):
        details = None
    else:
        matches = _HEAP_DETAILS_RE.match(details)
        # The 'line' field could be None if the binary wasn't
        # compiled with debug info. To avoid errors on this,
        # we need to make sure that line is not None before
        # converting it to an integer.
        line = matches.group(4)
        if line is not None:
            line = int(line)

        details = {
            'address': matches.group('address'),
            'function': matches.group('function'),
            'file': matches.group('fname'),
            'line': line
        }

    children = []
    for i in range(0, int(entry.group("num_children"))):
        children.append(_parse_heap_node(fd))

    heap_node = {}
    heap_node['nbytes'] = int(entry.group("num_bytes"))
    heap_node['children'] = children
    heap_node['details'] = details

    return heap_node

if __name__ == '__main__':
    pass
