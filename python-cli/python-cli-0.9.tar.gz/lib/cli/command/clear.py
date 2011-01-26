#
# This file is part of python-cli. python-cli is free software that is
# made available under the MIT license. Consult the file "LICENSE" that
# is distributed together with this file for the exact licensing terms.
#
# python-cli is copyright (c) 2011 by the python-cli authors. See the
# file "AUTHORS" for a complete overview.

import os
from cli.error import CommandError
from cli.command.command import Command


class ClearCommand(Command):

    name = 'clear'
    aliases = ('cls',)
    description = 'clear the screen'

    def run(self):
        self.context.terminal.clear()
