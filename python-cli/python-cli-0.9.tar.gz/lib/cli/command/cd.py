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
    usage = 'cd <directory>'
    description = 'change directory'
    nargs = 1

    def run(self):
        dirname = self.args[0]
        try:
            os.chdir(dirname)
        except OSError, e:
            m = '%s: %s' % (dirname, e.strerror)
            raise CommandError, m
