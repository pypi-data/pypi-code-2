#
# This file is part of python-cli. python-cli is free software that is
# made available under the MIT license. Consult the file "LICENSE" that
# is distributed together with this file for the exact licensing terms.
#
# python-cli is copyright (c) 2011 by the python-cli authors. See the
# file "AUTHORS" for a complete overview.

import os
from cli.command.command import Command


class PwdCommand(Command):

    name = 'pwd'
    description = 'print working directory'
    helptext = """\
        == Usage ==

        pwd

        == Description ==
        
        Print the current working directory.
        """

    def execute(self):
        stdout = self.context.terminal.stdout
        stdout.write('%s\n' % os.getcwd())
