#
# This file is part of python-cli. python-cli is free software that is
# made available under the MIT license. Consult the file "LICENSE" that
# is distributed together with this file for the exact licensing terms.
#
# python-cli is copyright (c) 2011 by the python-cli authors. See the
# file "AUTHORS" for a complete overview.

import sys
import textwrap
from optparse import OptionParser

from cli.object import create
from cli.settings import Settings
from cli.context import ExecutionContext


class TestExecutionContext(ExecutionContext):

    welcome = textwrap.dedent("""\
        Welcome to cli-test. This is a test driver for the python-cli.
        Type 'exit' to exit or 'help' for help.
        """)
    goodbye = 'Goodbye!'


def main():
    """Test driver for python-cli."""
    parser = create(OptionParser)
    parser.add_option('-f', '--filter', metavar='FILE',
                      help='execute commands from FILE')
    parser.add_option('-d', '--debug', action='store_true',
                      help='enable debugging mode')
    opts, args = parser.parse_args()

    if opts.filter:
        try:
            sys.stdin = file(opts.filter)
        except IOError, e:
            sys.stderr.write('error: %s\n' % e.strerror)
            sys.exit(1)

    context = create(TestExecutionContext)

    if len(args) == 0:
        context.execute_loop()
    else:
        command = ' '.join(args) + '\n'
        context.execute_string(command)

    sys.exit(context.status)
