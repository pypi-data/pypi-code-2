# -----------------------------------------------------------------------------
#    pydebmirror - Yet another mirroring tool for debian
#    Copyright (C) 2010  Sameer Rahmani <lxsameer@gnu.org>
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
# -----------------------------------------------------------------------------

from sys import stdout as so


class ColorNotFound (Exception):
    pass


class Console (object):
    """
    Handle the output to console.
    """

    # Default colors for bash.
    colordic = {
        "RED": "\033[31m%s\033[00m",
        "BRED": "\033[1;31m%s\033[00m",
        "PURPLE": "\033[35m%s\033[00m",
        "BPURPLE": "\033[1;35m%s\033[00m",
        "CYAN": "\033[36m%s\033[00m",
        "BCYAN": "\033[1;36m%s\033[00m",
        "BLUE": "\033[34m%s\033[00m",
        "BBLUE": "\033[1;34m%s\033[00m",
        "GREEN": "\033[32m%s\033[00m",
        "BGREEN": "\033[1;32m%s\033[00m",
        "YELLOW": "\033[1;33m%s\033[00m",
        "BROWN": "\033[33m%s\033[00m",
        "DGRAY": "\033[1;30m%s\033[00m",
        "LGRAY": "\033[37m%s\033[00m",
        "WHITE": "\033[1;37m%s\033[00m",
        "DEFAULT": "%s",
        }

    def __init__(self, default="DEFAULT", error="RED",
                 warning="BROWN", info="BGREEN",
                 debug="YELLOW", verbose=False,
                 debuging=False):

        if not default.upper() in self.colordic.keys() or \
               not error.upper() in self.colordic.keys() \
               or not info.upper() in self.colordic.keys() or \
               not debug.upper() in self.colordic.keys() or \
               not warning.upper() in self.colordic.keys():
            raise ColorNotFound("\"%s\" Color not found!." % default)

        self.default = default.upper()
        self.info = info.upper()
        self.debug = debug.upper()
        self.error = error.upper()
        self.warning = warning.upper()
        self._verbose = verbose
        self._debug = debuging

    def printf(self, string, **kwargs):
        """
        Print that string arg with the colors that defined in init function.
        User can define some arg that affect on output
        type = info, error, warning
        """
        ctype = kwargs.get("type", None)
        if ctype == "info":
            self.print_info(string)
        elif ctype == "error":
            self.print_error(string)
        elif ctype == "debug":
            self.print_debug(string)

        elif ctype == "warning":
            self.print_warning(string)
        else:
            self._write("%s\n" % string, self.default)

    # Same as printf but output will be like:
    # [warning/info/erro] : string
    def sprintf(self, string, ctype="info"):
        if ctype == "info":
            self._write("[Info]: ", self.info)
            self.printf(string)

        elif ctype == "error":
            self._write("[Error]: ", self.error)
            self.printf(string)

        elif ctype == "debug":
            if self._debug:
                self._write("[debug]: ", self.debug)
                self.printf(string)

        elif ctype == "warning" or ctype == "warn":
            self._write("[Warning]: ", self.warning)
            self.printf(string)
        else:
            self._write("%s\n" % string, self.default)

    def print_info(self, string):
        self._write("%s\n" % string, self.info)

    def print_debug(self, string):
        if self._debug:
            self._write("%s\n" % string, self.debug)

    def print_error(self, string):
        self._write("%s\n" % string, self.error)

    def print_warning(self, string):
        self._write("%s\n" % string, self.warning)

    # Be awar that this function did not print a \n character.
    def _write(self, string, color):
        """
        print a string on terminal
        """
        txt = self.colordic[color.upper()] % (string)
        so.write(txt)
        so.flush()
