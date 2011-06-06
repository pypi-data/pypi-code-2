# -*- encoding: utf-8- -*-

import sys
from optparse import make_option

from django.core.management.base import CommandError, LabelCommand

from frontweb import comandos

class Command(LabelCommand):
    help = "Crea un plugin frontweb."
    args = "[plugin_name]"
    label = 'plugin name'

    option_list = LabelCommand.option_list + (
        make_option('--plugins-dir',
            action="store",
            type="string",
            dest='plugins_dir',
            default="plugins",
            help='Path to plugins directory'),
        )

    requires_model_validation = False
    can_import_settings = False

    def handle_label(self, plugin_name, **options):
        plugins_dir = options.get('plugins_dir')
        comandos.crear_plugin(plugin_name, plugins_dir)

if __name__ == "__main__":
    cmnd = Command()
    if len(sys.argv) == 1:
        cmnd.print_help("frontweb_plugin", "")
    else:
        sys.argv.insert(0, "") # Hack run_from_argv
        cmnd.run_from_argv(sys.argv)
