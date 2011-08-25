#
# This file is part of python-cli. python-cli is free software that is
# made available under the MIT license. Consult the file "LICENSE" that
# is distributed together with this file for the exact licensing terms.
#
# python-cli is copyright (c) 2011 by the python-cli authors. See the
# file "AUTHORS" for a complete overview.

from cli.command.command import Command


class SaveCommand(Command):

    name = 'save'
    description = 'save configuration variables'
    args_check = 0
    helptext = """\
        == Usage ==

        save

        == Description ==

        Save the current value of all configuration settings.
        """

    def execute(self):
        self.context.settings.write_config_file()
