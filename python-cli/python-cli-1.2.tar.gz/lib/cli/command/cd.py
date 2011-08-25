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


class CdCommand(Command):

    name = 'cd'
    alias = ('chdir',)
    description = 'change directory'
    args_check = 1
    helptext = """\
        == Usage ==

        cd <directory>

        == Description ==

        Change the current directory to <directory>.
        """

    def execute(self):
        dirname = self.arguments[0]
        try:
            os.chdir(dirname)
        except OSError, e:
            self.error('%s: %s' % (dirname, e.strerror))
