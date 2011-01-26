#
# This file is part of python-cli. python-cli is free software that is
# made available under the MIT license. Consult the file "LICENSE" that
# is distributed together with this file for the exact licensing terms.
#
# python-cli is copyright (c) 2011 by the python-cli authors. See the
# file "AUTHORS" for a complete overview.

from cli.command.command import Command


class HelpCommand(Command):

    name = 'help'
    usage = 'help [topic]'
    description = 'show this help text'
    nargs = (0, 1)

    def run(self):
        if len(self.args) == 0:
            self._show_commands()
        else:
            self._show_help_topic(self.args[0])

    def _show_commands(self):
        stdout = self.context.terminal.stdout
        fancy = stdout.isatty()
        if fancy:
            stdout.write('Available commands\n\n')
        commands = []
        for cmd in self.context.commands:
            commands.append((cmd.name, cmd.description))
        commands.sort()
        for name,description in commands:
            if fancy:
                stdout.write('    ')
            stdout.write('%-18s %s\n' % (name, description))
        if fancy:
            stdout.write('\n')

    def _show_help_topic(self, topic):
        cls = self.context.get_command(topic)
        if cls is None:
            self.error('unknown help topic: %s' % topic)
        args = []; opts = [('--help', None)]
        command = cls(args, opts)
        command.execute(self.context)
