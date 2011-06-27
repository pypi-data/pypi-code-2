# Copyright (C) 2010, 2011 Linaro Limited
#
# Author: Zygmunt Krynicki <zygmunt.krynicki@linaro.org>
#
# This file is part of lava-dev-tool
#
# lava-dev-tool is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3
# as published by the Free Software Foundation
#
# lava-dev-tool is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with lava-dev-tool.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function

"""
User interface helper module
"""

import contextlib


class TextUI(object):
    """
    Simple plain text user interface
    """

    def __init__(self):
        self.nesting = []

    def say(self, msg="", *args, **kwargs):
        print("".join(self.nesting) + msg.format(*args, **kwargs))

    @contextlib.contextmanager
    def indent(self, text="  "):
        self.nesting.append(text)
        try:
            yield
        finally:
            self.nesting.pop()

    @contextlib.contextmanager
    def section(self, msg="", *args, **kwargs):
        self.say(msg, *args, **kwargs)
        with self.indent():
            yield

    def display_subprocess_output(self, stream_name, line):
        if stream_name == "stdout":
            on = ANSI.sequence(ANSI.cmd_bright, ANSI.cmd_fg + ANSI.white)
        else:
            on = ANSI.sequence(ANSI.cmd_bright, ANSI.cmd_fg + ANSI.yellow)
        off = ANSI.sequence(ANSI.cmd_not_bright, ANSI.cmd_fg + ANSI.default)
        self.say("- {on}{stream_name}{off}: {line}", 
                 on=on, stream_name=stream_name,
                 line=line.rstrip(), off=off)


class ANSI(object):

    CSI = "\033["

    black, red, green, yellow, blue, magenta, cyan, white = map(str, range(8))
    default = "9"

    cmd_fg = "3"
    cmd_bg = "4"
    cmd_bright = "1"
    cmd_not_bright = "22"
    cmd_underline = "4"
    cmd_no_underline = "24"
    cmd_reset = "0"

    @classmethod
    def sequence(cls, *cmds):
        return cls.CSI + ';'.join(cmds) + "m"
