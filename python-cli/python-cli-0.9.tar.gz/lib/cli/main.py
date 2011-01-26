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
        Welcome to cli-test. This is a test driver for the python-cli CLI
        construction toolkit. Type 'exit' to exit or 'help' for help.
        """)


def main():
    """Test driver for python-cli."""
    parser = OptionParser()
    parser.add_option('-f', '--filter', metavar='FILE',
                      help='execute commands from FILE')
    parser.disable_interspersed_args()
    opts, args = parser.parse_args()
    if len(args) == 0:
        command = None
    else:
        command = ' '.join(args)

    settings = create(Settings)
    context = create(TestExecutionContext, settings)

    if command is not None:
        context.execute_command(command)
    elif opts.filter:
        context.command_loop(opts.filter)
    else:
        context.command_loop(sys.stdin)

    sys.exit(context.status)

if __name__ == '__main__':
    main()
