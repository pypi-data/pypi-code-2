# DjangoDE, an integrated development environment for Django
# Copyright (C) 2010-2011 Andrew Wilkinson
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import re

from djangode import global_objects
from djangode.utils.config import get_config_value
from djangode.utils.qt import QtCore, QtGui

class PythonHighlighter(QtGui.QSyntaxHighlighter):
    def __init__(self, document):
        QtGui.QSyntaxHighlighter.__init__(self, document)

        self.rules = []

        for keyword in keywords:
            self.rules.append((re.compile(keyword), 0, self.get_format("keyword")))

        self.rules += [
                (re.compile('"[^"]*"'), 0, self.get_format("string")),
                (re.compile("'[^']*'"), 0, self.get_format("string")),
                (re.compile("#[^\n]*"), 0, self.get_format("comment"))
            ]

    def highlightBlock(self, text):
        for regex, index, _format in self.rules:
            for match in regex.finditer(text):
                start, end = match.start(index), match.end(index)

                self.setFormat(start, end-start, _format)

    def get_format(self, colour=None, bgcolour=None):
        _format = QtGui.QTextCharFormat()

        if colour is not None:
            qcolour = QtGui.QColor(*get_config_value(colour+"_colour"))
            _format.setForeground(qcolour)

        if bgcolour is not None:
            bgqcolour = QtGui.QColor()
            bgqcolour.setNamedColor(bgcolour)
            _format.setBackground(bgqcolour)

        return _format

keywords = [
        'and', 'assert', 'break', 'class', 'continue', 'def',
        'del', 'elif', 'else', 'except', 'exec', 'finally',
        'for', 'from', 'global', 'if', 'import', 'in',
        'is', 'lambda', 'not', 'or', 'pass', 'print',
        'raise', 'return', 'try', 'while', 'yield',
        'None', 'True', 'False',
    ]
