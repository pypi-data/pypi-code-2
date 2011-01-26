#
# This file is part of python-cli. python-cli is free software that is
# made available under the MIT license. Consult the file "LICENSE" that
# is distributed together with this file for the exact licensing terms.
#
# python-cli is copyright (c) 2011 by the python-cli authors. See the
# file "AUTHORS" for a complete overview.

from cli.command.command import Command


class StatusCommand(Command):

    name = 'status'
    description = 'show status'

    def run(self):
        context = self.context
        stdout = context.terminal.stdout
        status = context.status
        if status is not None:
            sstatus = str(status)
            for sym in dir(context):
                if sym[0].isupper() and getattr(context, sym) == status:
                    sstatus += ' (%s)' % sym[7:]
        else:
            sstatus = 'N/A'
        stdout.write('last command status: %s\n' % sstatus)
