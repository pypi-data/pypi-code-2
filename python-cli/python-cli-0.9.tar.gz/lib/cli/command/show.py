#
# This file is part of python-cli. python-cli is free software that is
# made available under the MIT license. Consult the file "LICENSE" that
# is distributed together with this file for the exact licensing terms.
#
# python-cli is copyright (c) 2011 by the python-cli authors. See the
# file "AUTHORS" for a complete overview.

from cli.error import CommandError
from cli.command.command import Command


class ShowCommand(Command):

    name = 'show'
    description = 'show configuration variables'
    usage = '%command\n' \
            '%command <name>'
    nargs = (0, 1)

    def run(self):
        context = self.context
        stdout = context.terminal.stdout
        if len(self.args) == 1:
            names = [self.args[0]]
        else:
            names = context.settings.keys()
        names.sort()
        fancy = stdout.isatty() and len(names) > 1
        if fancy:
            stdout.write('Current settings:\n\n')
        for name in names:
            if fancy:
                stdout.write('    ')
            stdout.write('%s = "%s"\n' % (name, context.settings[name]))
        if fancy:
            stdout.write('\n')
