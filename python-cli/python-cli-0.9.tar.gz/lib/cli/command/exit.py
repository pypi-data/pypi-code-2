#
# This file is part of python-cli. python-cli is free software that is
# made available under the MIT license. Consult the file "LICENSE" that
# is distributed together with this file for the exact licensing terms.
#
# python-cli is copyright (c) 2011 by the python-cli authors. See the
# file "AUTHORS" for a complete overview.

from cli.command.command import Command


class ExitCommand(Command):

    name = 'exit'
    description = 'quit this interactive terminal'

    def run(self):
        self.context.exit_loop()
