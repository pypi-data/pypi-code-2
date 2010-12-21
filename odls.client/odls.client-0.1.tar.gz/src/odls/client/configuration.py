##
## configuration.py
## Login : <uli@pu.smp.net>
## Started on  Thu Dec  3 10:02:01 2009 Uli Fouquet
## $Id$
## 
## Copyright (C) 2009 Uli Fouquet
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
## 
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
## 
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
##
"""Configure ODLSclient via config files and options.

Basically, odls.client configuration is performed by parsing
configuration files, whose settings can be overridden by commandline
options. The result is stored in an :class:`ODLSConfiguration`
instance.
"""

import logging
import os
import pkg_resources
import re
import sys
from ConfigParser import SafeConfigParser, NoOptionError
from cStringIO import StringIO
from optparse import OptionParser, OptionGroup, SUPPRESS_HELP
from odls.client.logger import init_logger

#: Dictionary of defaults for config file parser.
DEFAULTS = dict(
    # SERVER related
    SERVER_URL = "",
    TIMEOUT=3,
    ODLS_USERNAME="",
    ODLS_PASSWORD="",
    ENABLE_SSL=False,
    HTTP_USERNAME=None,
    HTTP_PASSWORD=None,
    # PROXY related
    PROXY_SERVER=None,
    PROXY_USER=None,
    PROXY_PASSWORD=None,
    # CLIENT related
    WATCH_FILES='"./foo", "./bar"',
    WATCH_FOLDERS='".", ".."',
    WATCH_BLACKLIST='"*~", "~*"',
    WATCH_UPDATETIME=600L,
    WATCH_OLD_DISCARD=900L, # -1 for never
    WATCH_IGNORE_ODLS_FAILURE=True,
    WATCH_IGNORE_UNREADABLE=True,
    SEND_BINARIES=True,
    SEND_KEYWORDS=True,
    SEND_FULLTEXT=False,
    SEND_COMPRESSED=True,
    OUTPUT_ENCODING="ISO-8859-15",
    # LOGGING related
    DO_SYSLOG=False,
    LOGFILE="./indexer.log",
    MAX_FILE_SIZE = 1024**2,
    LOGSERVER=None,
    LOGLEVEL = 'WARN',
    LOGNAME = 'odls.client',
    # Other
    TMPFILE = "./indexer.tmp",
    DBFILE = "./indexer.db",
    INPUTFILE = None,
    OUTPUTFILE = "-",
    CMDLINEOUT = False,
    NOHTTPOUT = False,
    EXTERNALPARSER = 'odlsparser',
    )

DEFAULT_INI = os.path.abspath(os.path.join(
    os.path.dirname(__file__), 'default.ini'))

#: Dictionary of defaults for commandline options.
STANDARD_DEFAULTS = dict(
    verbose = False,
    quiet = False,
    configfile = 'indexer.ini',
    input = None,
    externalparser = None,
    background = False,
    fatal_action = None,
    cmdout = False,
    nohttpout = False,
    send_binaries = True,
    send_keywords = True,
    send_fulltext = False,
    send_compressed = True,
    enc = 'utf-8',
    logname = 'odls.client',
    logfile = 'indexer.log',
    loglevel = 3,
    watch_files = [],
    proxy_server = None,
    server_url = None,
    odls_username = '',
    odls_password = '',
    http_username = None,
    http_password = None,
    dbfile = 'indexer.db',
    watch_ignore_odls_failure = True,
    watch_updatetime = 300L,
    )

SYSTEM_INI = os.path.abspath(os.path.join(
        '/etc', 'indexer.ini'))

USER_INI1 = os.path.abspath(os.path.expanduser('~/indexer.ini'))
USER_INI2 = os.path.abspath(os.path.expanduser('~/.indexer.ini'))

class ODLSConfigParser(SafeConfigParser):
    """A parser for configuration files.

    `ODLSConfigParser` retrieves settings from eventually different
    configuration files. It is derived from
    :class:`ConfigParser.SafeConfigParser`.

    The :meth:`read` method retrieves default values from a default
    configuration placed in the package itself (file ``default.ini``).

    Additionally, an :class:`ODLSConfigParser` provides methods to
    cast certain settings to expected types.
    """
    default_ini = DEFAULT_INI

    default_config_files = [
        USER_INI1, USER_INI2, SYSTEM_INI, DEFAULT_INI]

    _option_settings = [
        ('do_syslog', 'LOG', 'bool'),
        ('loglevel', 'LOG', 'loglevel'),
        ('logname', 'LOG', 'odls.client'),
        ('max_file_size', 'LOG', 'int'),
        ('odls_password', 'SERVER', 'string'),
        ('odls_username', 'SERVER', 'string'),
        ('http_password', 'SERVER', 'string'),
        ('http_username', 'SERVER', 'string'),
        ('output_encoding', 'CLIENT', 'string'),
        ('send_binaries', 'CLIENT', 'bool'),
        ('send_compressed', 'CLIENT', 'bool'),
        ('send_fulltext', 'CLIENT', 'bool'),
        ('send_keywords', 'CLIENT', 'bool'),
        ('dbfile', 'CLIENT', 'string'),
        ('server_url', 'SERVER', 'string'),
        ('proxy_server', 'SERVER', 'string'),
        ('timeout', 'CLIENT', 'int'),
        ('watch_blacklist', 'CLIENT', 'filelist'),
        ('watch_files', 'CLIENT', 'filelist'),
        ('watch_folders', 'CLIENT', 'filelist'),
        ('watch_old_discard', 'CLIENT', 'int'),
        ('watch_ignore_unreadable', 'CLIENT', 'bool'),
        ('watch_ignore_odls_failure', 'CLIENT', 'bool'),
        ('watch_updatetime', 'CLIENT', 'int'),
        ]
    
    def read(self, files=[]):
        """Read all configuration files and set options accordingly.

        `files` can be a single string containing the path to a
        configuration file or a list of paths to be parsed in that
        order.

        If no `files` are given some default locations are looked up.
        The default locations are (in that order):

        * ``~/indexer.ini``
        * ``~/.indexer.ini``
        * ``/etc/indexer.ini``
        * The ``default.ini`` placed in the package itself.

        Settings in former config files override those in latter ones.

        .. seealso:: :ref:`default_ini`
        """
        if isinstance(files, basestring):
            files = [files]
        for path in self.default_config_files:
            files.insert(0, path)
        return SafeConfigParser.read(self, files)

    def getloglevel(self, section, option):
        """Interpret setting in `section` and `option` as loglevel.

        Returns an integer representing the loglevel set in the given
        option and section.

        If setting is none of ['debug', 'info', 'notice', 'warn',
        'error', 'crit', 'fatal', 'emerg'] a `ValueError` is raised.
        
        """
        val = self.get(section, option)
        try:
            val = int(val)
        except:
            val = val.lower()
            loglevels = [
                'debug', 'info', 'notice', 'warn', 'error', 'crit',
                'fatal', 'emerg']
            if val not in loglevels:
                raise ValueError('Illegal loglevel in config file: %s' % val)
            val = loglevels.index(val)
            pass
        return val

    def getint(self, section, option):
        """Interpret setting in `section` and `option` as integer.

        Returns an integer read from the (string) value set in the
        according `section` and `option`.

        Raises `ValueError` if the value set cannot be transformed
        into a string.

        Trailing comments (starting with ``#``) are stripped before
        processing.
        """
        val = self.get(section, option)
        if '#' in val:
            val = val.split('#')[0]
        return int(val)

    def getstring(self, section, option):
        """Interpret setting in `section` and `option` as string.

        Any comments (starting with ``#``) are stripped before
        processing.
        """
        val = self.get(section, option)
        val = val.replace('\n', '').strip()
        val = val.split('#')[0]
        return val

    def getlist(self, section, option):
        """Interpret setting in `section` and `option` as list of strings.

        A list in a configuration file can be written on different
        lines where the second and following lines are indented by one
        or more whitespaces::
        
          [SECTION_NAME]
          optionkey = val1
            val2
            val3

        Parsing this will give the list ['val1', 'val2', 'val3'] as
        result. Note the indentation of lines with ``val2`` and
        ``val3``.
        """
        val = self.get(section, option)
        # We use StringIO and readlines to get a proper linesep parsing.
        val = StringIO(val).readlines()
        return [x.strip() for x in val]

    def getoptions(self, files=[]):
        """Get options as set in configuration files.

        Returns a dict of options. Parses the `files` given (or
        the default files. See :meth:`read` for details), extracts the
        values set, casts eventually types of the values set and
        returns the results as a dict.
        """
        read = self.read(files)
        result = dict()
        for name, section, type in self._option_settings:
            try:
                if type == 'bool':
                    val = self.getboolean(section, name)
                elif type == 'int':
                    val = self.getint(section, name)
                elif type == 'string':
                    val = self.getstring(section, name)
                elif type == 'loglevel':
                    val = self.getloglevel(section, name)
                elif type == 'filelist':
                    val = self.getlist(section, name)
                    # Don't accept empty filenames...
                    val = [x for x in val if x != '']
                else:
                    val = self.get(section, name)
            except NoOptionError:
                # Unset options should not pollute the default options
                # set by option parsers...
                continue
            result[name] = val
        # We have to handle key vars separately...
        keyvars = dict()
        if self.has_section('ODLS_VARS'):
            for option in self.options('ODLS_VARS'):
                val = self.get('ODLS_VARS', option)
                keyvars[option] = val
        result['odls_vars'] = keyvars
        return result
    
usage = "usage: %prog [options]"

VERSION = pkg_resources.get_distribution(
    'odls.client').version


def yes_no_callback(option, opt_str, value, parser):
    """An option parser callback function to turn integers into booleans.

    It sets the passed option to False if the given value (a number)
    is zero and to `True` else.
    """
    if value == 0:
        setattr(parser.values, option.dest, False)
        return
    setattr(parser.values, option.dest, True)
    return

class ODLSOptionParser(OptionParser, object):
    """Parser for commandline options.

    Derived from :class:`optparse.OptionParser`. Contains all options
    supported on commandline.
    """

    def __init__(self, *args, **kw):
        if 'version' not in kw.keys():
            kw.update(dict(version=VERSION))
        result = super(ODLSOptionParser, self).__init__(*args, **kw)
        self.add_option("-v", "--verbose",
                        action="store_true", dest="verbose",
                        help="Produce verbose output")
        self.add_option("-q", "--quiet",
                        action="store_true", dest="quiet",
                        help="Don't produce any output")
        self.add_option("-c", "--config", metavar="FILE", dest="configfile",
                        help="Read configuration from FILE")
        self.add_option("-i", "--input", metavar="FILE", dest="input",
                        help="Examine FILE and exit (disables HTTP "
                        "output, enables cmdout)")
        self.add_option("-e", "--executable", metavar="PROGRAM",
                        dest="externalparser",  default=None,
                        help="Call PROGRAM for external parsing.")
        self.add_option("", "--dbfile", metavar="FILEPATH",
                        dest="dbfile", default=None,
                        help="Store status in FILEPATH. Default: indexer.db.")
        
        # XXX: WIN only
        self.add_option("-b", "--background",
                        action="store_true", dest="background",
                        help="Force application to run in background")
        # XXX: WIN only
        self.add_option("", "--fatal-action", metavar="SCRIPT_PATH",
                        dest="fscript",
                        help="Script to run when uncatched exceptions happen")

        # SUPPRESSED options...
        self.add_option("", "--watch-files", dest="watch_file",
                        action="append", type="string",
                        help=SUPPRESS_HELP)
        self.add_option("", "--max-file-size", dest="max_file_size",
                        type="int",
                        help=SUPPRESS_HELP)
        self.add_option("", "--proxy-server", dest="proxy_server",
                        type="string",
                        help=SUPPRESS_HELP)
        self.add_option("", "--server-url", dest="server_url",
                        type="string",
                        help=SUPPRESS_HELP)
        self.add_option("", "--odls-username", dest="odls_username",
                        type="string",
                        help=SUPPRESS_HELP)
        self.add_option("", "--odls-password", dest="odls_password",
                        type="string",
                        help=SUPPRESS_HELP)
        self.add_option("", "--http-username", dest="http_username",
                        type="string",
                        help=SUPPRESS_HELP)
        self.add_option("", "--http-password", dest="http_password",
                        type="string",
                        help=SUPPRESS_HELP)
        self.add_option("", "--ignore-odls-failure",
                        dest="watch_ignore_odls_failure",
                        action="store_true",
                        help=SUPPRESS_HELP)
        self.add_option("", "--watch-updatetime", dest="watch_updatetime",
                        type="int",
                        help=SUPPRESS_HELP)

        output_group = OptionGroup(self, "Output-related options", "")
        output_group.add_option("-1", "--cmdout", action="store_true",
                                dest="cmdout",
                                help="Output parsed documents to commandline "
                                     "(disabled by default)")
        output_group.add_option("-2", "--nohttpout", action="store_true",
                                dest="nohttpout",
                                help="Send no output to remote HTTP server "
                                     "(enabled by default)")
        output_group.add_option("-o", "--output", metavar="FILE",
                                dest="output",
                                help="Output to FILE instead of standard "
                                     "output")
        output_group.add_option("", "--send-binaries",
                                dest="send_binaries",
                                type="int",
                                action="callback", callback=yes_no_callback,
                                help="Send parsed file as a whole to server. "
                                     "0 for do not send, any other number "
                                     "else (enabled by default)")
        output_group.add_option("", "--send-keywords",
                                dest="send_keywords",
                                type="int",
                                action="callback", callback=yes_no_callback,
                                help="Send keywords of parsed files to "
                                     "server. 0 for do not send, any other "
                                     "number else (disabled by default)")
        output_group.add_option("", "--send-fulltext",
                                dest="send_fulltext",
                                type="int",
                                action="callback", callback=yes_no_callback,
                                help="Send extracted text of parsed files to "
                                     "server. 0 for do not send, any other "
                                     "number else (disabled by default)")
        output_group.add_option("", "--send-compressed",
                                dest="send_compressed",
                                type="int",
                                action="callback", callback=yes_no_callback,
                                help="Compress transfered files. 0 for no "
                                     "compression, any other number else "
                                     "(enabled by default)")
        output_group.add_option("", "--enc", metavar="CHARSET",
                                default='utf-8', dest="encoding",
                                help="Use CHARSET as output encoding "
                                     "(default 'utf-8')")

        logging_group = OptionGroup(self, "Logging-related options", "")
        logging_group.add_option("-n", "--name", dest="logname",
                                help="Name of instance (for logging)")
        logging_group.add_option("-l", "--log", metavar="FILE",
                                 dest="logfile",
                                 help="Log to FILE")
        logging_group.add_option("", "--loglevel", dest='loglevel',
                                 type="int",
                                 #choices=['0', 1, 2, 3, 4, 5, 6, 7],
                                 help="Log only messages of given level or "
                                      "above:\n0 (debug), 1 (info), 2 "
                                      "(notice), 3 (warn), 4 (error), 5 "
                                      "(critical), 6 (fatal), 7(emergency). "
                                      "Default is 3 (warn)")
                                
        self.add_option_group(output_group)
        self.add_option_group(logging_group)
        self.set_defaults()
        return result

    def set_defaults(self, defaults=dict()):
        """Set defaults for option parser.

        Sets dict in :data:`STANDARD_DEFAULTS` as default dict and
        eventually overrides single settings if also defined in
        `defaults` parameter.

        This can be used to feed the commandline parser with default
        options before actually parsing the real options and args from
        commandline.
        """
        internal_defaults = STANDARD_DEFAULTS
        internal_defaults.update(defaults)
        result = super(ODLSOptionParser, self).set_defaults(
            **internal_defaults)
        return result

class ODLSConfiguration(object):
    """An ODLS configuration.

    The configuration is mainly a set of options and args set by
    commandline options or configuration file settings.

    Commandline options always override config file settings.

    If no `argv` is passed values from :data:`sys.argv` are used.
    
    After initialization any :class:`ODLSConfiguration` instance
    provides options set by config files and commandline in the
    `options` attribute.

    Retrieving the options considering all kinds of defaults is done
    as follows:

    1) A commandline parser is created and run to get all options from
       commandline for the first time. We basically only need this
       step to grab any configuration file path set by commandline
       (``-c`` option).

    2) A config file parser is created, that also respects any
       configuration file set during step 1. As a result we get a dict
       of options as set by various configuration files.

    3) The option dict retrieved in step 2 is then used as a set of
       defaults for running the commandline parser for a second
       time. This time the `options` and `args` of the
       :class:`ODLSConfiguration` instance are really set.

    .. seealso:: :class:`ODLSConfigParser`, :class:`ODLSOptionParser`,
    """
    
    #: The options set after commandline and config file parsing. An
    #: instance of :class:`optparse.Values`.
    options = None

    #: The args delivered by commandline. A list of strings.
    args = None
    
    def __init__(self, argv=None):
        if argv is None: argv=sys.argv[1:]
        # We have to parse cmdline opts first to get any configuration
        # file setting.
        cmdline_parser = ODLSOptionParser()
        (opts, args) = cmdline_parser.parse_args(argv)
        conffile = opts.configfile

        # Now we can parse the config files...
        conf_parser = ODLSConfigParser()
        result = conf_parser.read(conffile)
        conffile_opts = conf_parser.getoptions(conffile)
        
        # ...and update the results with commandline opts.
        cmdline_parser.set_defaults(conffile_opts)
        self.options, self.args = cmdline_parser.parse_args(argv)
        return
