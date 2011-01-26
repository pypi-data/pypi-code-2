#
# This file is part of python-cli. python-cli is free software that is
# made available under the MIT license. Consult the file "LICENSE" that
# is distributed together with this file for the exact licensing terms.
#
# python-cli is copyright (c) 2011 by the python-cli authors. See the
# file "AUTHORS" for a complete overview.

from cli.error import CommandError
from cli.command.command import Command


class SetCommand(Command):

    name = 'set'
    usage = 'set <name> <value>'
    description = 'set a configuration variable'
    nargs = 2

    def run(self):
        try:
            self.context.settings[self.args[0]] = self.args[1]
        except (KeyError, ValueError), e:
            raise CommandError, e.message
