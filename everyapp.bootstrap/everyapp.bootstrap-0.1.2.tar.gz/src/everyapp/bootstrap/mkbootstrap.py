# -*- coding: utf-8 -*-

#---Header---------------------------------------------------------------------

# This file is part of everyapp.bootstrap.
# Copyright (C) 2010 Krys Lawrence
#
# everyapp.bootstrap is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# everyapp.bootstrap is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.

"""Generate a virtualenv_ bootstrap script with customizations.

.. _virtualenv: http://pypi.python.org/pypi/virtualenv

"""

# Remember: This code should work under at least Python 2.4, if not earlier
#           versions, as that is what virtualenv itself supports.


#---Imports--------------------------------------------------------------------

#---  Standard library imports
import optparse
import os
from os import path

#---  Third-party imports
import pkg_resources
import virtualenv

#---  Project imports


#---Globals--------------------------------------------------------------------

#: Program description as displayed in :option:`--help`.
_DESCRIPTION = """\
Generate an enhanced virtualenv bootstrap script.
"""

#: Program epilogue as displayed in :option:`--help`.
_EPILOGUE = """\
For more information see the documentation at:
http://pypi.python.org/pypi/everyapp.bootstrap/
"""

#: Program version template as displayed in :option:`--help`.
#:
#: In the template ``%%prog`` will be replaced with the program name as it used
#: on the command-line.  The first ``%s`` is replaced with the distribution
#: name (``everyapp.bootstrap``) and the second ``%s`` is replaced with the
#: program's version.
#:
_VERSION_TEMPLATE = """\
%%prog (%s) %s
Copyright (C) 2010 Krys Lawrence
Licence GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.
"""

#: :option:`--version` option help as displayed in :option:`--help`.
#:
#: This is a replacement of the built-in help text to include proper
#: capitalization and punctuation.
#:
_VERSION_HELP = "Show program's version number and exit."

#: :option:`--help` option help as displayed in :option:`--help`.
#:
#: This is a replacement of the built-in help text to include proper
#: capitalization and punctuation.
#:
_HELP_HELP = 'Show this help message and exit.'

#: :option:`--script-name` option help as displayed in :option:`--help`.
_SCRIPT_NAME_HELP = """\
The name of the bootstrap python script to generate.  (Default: %default)
"""

#: :option:`--config-name` option help as displayed in :option:`--help`.
_CONFIG_NAME_HELP = """\
The name of the bootstrap configuration file to generate.  (Default: Same as
script name but with a .cfg extension.)
"""

#: :option:`--etc` option help as displayed in :option:`--help`.
_ETC_HELP = """\
Put the generated configuration file in an etc sub-directory instead of in the
current directory.
"""

#: :option:`--no-customization` option help as displayed in :option:`--help`.
_NO_CUSTOMIZATION_HELP = """\
Only generate a plain vanilla virtualenv bootstrap script without any
customizations or a configuration file.
"""

#: :option:`--customize-script` option help as displayed in :option:`--help`.
_CUSTOMIZE_SCRIPT_HELP = """\
Use your own virtualenv customization code instead of that provided by this
program.  (The $DEFAULT_CONFIG_FILE_NAME$ token in your script will be replaced
with the name of the config file.
"""

#: :option:`--default-config` option help as displayed in :option:`--help`.
_DEFAULT_CONFIG_HELP = """\
Use your own default configuration file instead of the one provided by this
program.  Note: A new configuration file will not be generated if an existing
one is found in the current directory or in an etc sub-directory.
"""


#---Functions------------------------------------------------------------------

def main(args=None, program_name=None):
    """Main program for the :program:`mkbootstrap` command.

    This function will generate the virtualenv_ bootstrap script in the current
    directory, and optionally a default configuration file as well.

    :parameter iterable of strings, or None args: The command-line arguments to
      use.  If it is None, then sys.args[1:] will be used.
    :parameter string or None program_name: The name of the program as it
      appears on the command-line.  If it is None, then sys.argv[0] is used.

    .. todo:: Find a way to automatically include the output of the
      :option:`--help` options in the generated Sphinx docs.

    """
    parser = _build_parser(program_name)
    options = _parse_options(parser, args)
    _create_bootstrap_script(options)
    _create_bootstrap_config(options)


def _build_parser(program_name=None):
    """Return the command-line parser.

    :parameter string or None program_name: The name of the program as it
      appears on the command-line.  If it is None, then sys.argv[0] is used.
    :rtype: optparse.OptionParser

    """
    project_name = 'everyapp.bootstrap'
    version = pkg_resources.get_distribution(project_name).version
    parser = optparse.OptionParser(
      prog=program_name,
      description=_DESCRIPTION,
      epilog=_EPILOGUE,
      version=_VERSION_TEMPLATE % (project_name, version),
    )
    parser.add_option_group(_build_advanced_options_group(parser))
    # Fix up the provided option help messages to include proper capitalization
    # and punctuation.
    parser.get_option('--version').help = _VERSION_HELP
    parser.get_option('--help').help = _HELP_HELP
    parser.add_option('-s', '--script-name',
      metavar='FILE_NAME',
      default='bootstrap.py',
      help=_SCRIPT_NAME_HELP,
    )
    parser.add_option('-c', '--config-name',
      metavar='FILE_NAME',
      help=_CONFIG_NAME_HELP,
    )
    parser.add_option('-e', '--etc',
      action='store_true',
      help=_ETC_HELP,
    )
    parser.add_option('-n', '--no-customization',
      action='store_true',
      help=_NO_CUSTOMIZATION_HELP,
    )
    return parser


def _build_advanced_options_group(parser):
    """Return the Advanced Options group for the command-line parser.

    :parameter optparse.OptionParser parser: The command-line parser to which
      the group belongs.
    :rtype: optparse.OptionGroup

    """
    group = optparse.OptionGroup(parser, 'Advanced Options')
    group.add_option('-S', '--customize-script',
      metavar='FILE_NAME',
      help=_CUSTOMIZE_SCRIPT_HELP,
    )
    group.add_option('-C', '--default-config',
      metavar='FILE_NAME',
      help=_DEFAULT_CONFIG_HELP,
    )
    return group


def _parse_options(parser, args=None):
    """Parse the command-line arguments.

    :parameter optparse.OptionParser parser: The command-line parser to use.
    :parameter iterable of strings, or None args: The command-line arguments to
      use.  If it is None, then sys.args[1:] will be used.
    :returns: The parsed option values.
    :rtype: optparse.Values

    .. note:: Positional command-line arguments are not supported.

    .. seealso:: :func:`_build_parser` for details about creating the parser.

    """
    options, _ = parser.parse_args(args)
    if not options.config_name:
        options.config_name = path.splitext(options.script_name)[0] + '.cfg'
    return options


def _create_bootstrap_script(options):
    """Generate the virtualenv_ bootstrap script in the current directory.

    :parameter optparse.Values options: The options values used to configure
      the program.

    .. seealso: :func:`_parse_options` for details about creating the
      configuration values.

    """
    if options.no_customization:
        customize_source = ''
    else:
        customize_source = _get_customize_source(options)
    bootstrap_source = virtualenv.create_bootstrap_script(customize_source)
    # Patch to fix virtualenv 1.5 bug #60 on Windows.  For details see
    # http://bitbucket.org/ianb/virtualenv/issue/60.
    # This patch should be removed when virtualenv 1.5.1 is released.
    bootstrap_source = bootstrap_source.replace(
      "assert relpath[0] == '/'",
      "assert relpath[0] == os.sep",
    )
    script_file = open(options.script_name, 'wb')
    try:
        script_file.write(bootstrap_source)
    finally:
        script_file.close()


def _get_customize_source(options):
    """Return the customization source code.

    If a customization script file has been specified in the options, the it is
    read in and returned.  Otherwise, the default customization script
    provided by this package is returned.

    Also, if the script contains the token ``$DEFAULT_CONFIG_FILE_NAME$``, it
    is replaced with the path of the bootstrap configuration file as specified
    in the given options.

    :parameter optparse.Values options: The options values used to configure
      the program.

    .. seealso: :func:`_parse_options` for details about creating the
      configuration values.

    """
    file_name = options.customize_script
    if file_name:
        source_file = open(file_name, 'rb')
        try:
            source = source_file.read()
        finally:
            source_file.close()
    else:
        source = pkg_resources.resource_string(__name__, 'customize.py')
    source = source.replace('$DEFAULT_CONFIG_FILE_NAME$', options.config_name)
    return source


def _create_bootstrap_config(options):
    """Generate the configuration file to be used by the bootstrap script.

    If the given options indicate not to generate a configuration file, no file
    will be generated.  Otherwise, a configuration file will either be
    generated in the current directory or in an :file:`etc` sub-directory of
    the current directory, depending on the given options.  The :file:`etc`
    sub-directory will automatically be created if necessary.

    Also, if a configuration file already exists in either of the above two
    locations, it will not be overwritten and a new configuration file will not
    be generated.

    :parameter optparse.Values options: The options values used to configure
      the program.

    .. seealso: :func:`_parse_options` for details about creating the
      configuration values.

    """
    file_name = options.config_name
    etc_dir = 'etc'
    etc_file_name = path.join(etc_dir, file_name)
    default_config = options.default_config
    if options.no_customization:
        return
    if path.exists(file_name) or path.exists(etc_file_name):
        return
    if default_config:
        source = open(default_config, 'rb').read()
    else:
        source = pkg_resources.resource_string(__name__, 'bootstrap.cfg')
    if options.etc:
        if not path.exists(etc_dir):
            os.makedirs(etc_dir)
        file_name = etc_file_name
    config_file = open(file_name, 'wb')
    try:
        config_file.write(source)
    finally:
        config_file.close()


#---Classes--------------------------------------------------------------------


#---Module initialization------------------------------------------------------


#---Late Imports---------------------------------------------------------------


#---Late Globals---------------------------------------------------------------


#---Late Functions-------------------------------------------------------------


#---Late Classes---------------------------------------------------------------


#---Late Module initialization-------------------------------------------------
