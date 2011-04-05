#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""Custom Parser for TSPlib files"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Add here required modules
import re
from collections import deque

__all__ = ['TSPParser']

# Sleipnir dependences
from sleipnir.core.log import log
from sleipnir.core.parser import Parser, StopParser, BadTokenError


def _log(*args):
    """Sugar for login"""
    log.parser.debug("Token '%s' (LastTok %s). Value %s." % args)


class TSPParser(Parser):
    """ A Simple TSPLIB Parser """

    def __init__(self):
        super(TSPParser, self).__init__()
        # Magic. Keep Definitions Sorted
        self.tokens['emptyline'] = "([\s|\n]*)$"
        self.tokens['EOF'] = "^(EOF)$"
        self.tokens['comment'] = "^[#]\s*([^\r\n]*)$"
        self.tokens['section'] = "^(\w+)(?<!_SECTION)\s*:"
        self.tokens['sec_value'] = "\s*([^\r\n]*)$"
        self.tokens['content'] = "^(\w+_SECTION):?\s*\n$"
        self.tokens['content_value'] = "^\s*([^\r\n]+)\n\n"

        self.regex = re.compile(r"""
          %(emptyline)s                  # Empty Lines
          |%(EOF)s                       # EOF
          |%(comment)s                   # TSPLIB comments
          |%(section)s%(sec_value)s      # Section Description
          |%(content)s                   # Section Content
          |%(content_value)s             # Section Value
          """ % self.tokens, re.MULTILINE | re.VERBOSE)

        self.__clear_state()

    def __clear_state(self):
        self._stopnow = 2
        self._lasttok = None
        if not hasattr(self, '_visited'):
            self._visited = deque()
        self._visited.clear()

    def scanner_TSPLIB(self):
    #pylint: disable-msg=C0103
        """Returns compiled regular expresion"""

        return self.regex

    @Parser.group('index')
    #pylint: disable-msg=W0613,R0201
    def on_emptyline(self, line):
        """Invoked when en empty line is found"""

        log.parser.debug("Empty line found")
        return True

    @Parser.group('index')
    def on_comment(self, comment):
        """Invoked when a comment is foumd"""

        _log('comment', self._lasttok, comment)
        return comment

    @Parser.group('index')
    def on_section(self, section):
        """Invoked when a 'section' name is found"""

        _log('section', self._lasttok, section)
        if section in self._visited:
            raise BadTokenError("Duplicate section %s", section)
        self._visited.appendleft(section)
        self._lasttok = 'section'
        return section

    @Parser.group('index')
    def on_sec_value(self, value):
        """Invoked when a 'value' for an existing section is found"""

        _log('sec_value', self._lasttok, value)
        if self._lasttok != 'section':
            raise BadTokenError(
                "Invalid previous token. "
                "Was '%s', expected 'section'" % self._lasttok)
        self._lasttok = None
        return value

    @Parser.group('index')
    def on_content(self, section):
        """Called when a valid content is found"""

        _log('content', self._lasttok, section)
        if self._lasttok not in (None, 'content_value', ):
            raise BadTokenError(
                "Invalid previous token. "
                "Was '%s', expexted None" % self._lasttok)

        if section not in self._visited:
            self._visited.appendleft(section)
        self._lasttok = 'content'
        return section

    @Parser.group('index')
    def on_content_value(self, value):
        """Invoked when valid content value appears"""

        _log('content_value', self._lasttok, value)
        if self._lasttok not in ('content', 'content_value',):
            raise BadTokenError(
                "Invalid previous token. Was '%s'" % self._lasttok)

        self._lasttok = 'content_value'
        return value

    #pylint: disable-msg=C0103,W0613
    def on_EOF(self, *args, **kwargs):
        """When called, an EOF has been found"""

        log.parser.debug("Token 'EOF' (LastTok %s)." % self._lasttok)
        self._stopnow -= 1
        return self._stopnow == 0

    def parse(self, handler, line_by_line=False):
        # FIXME: Refactor this
        self.__clear_state()
        return super(TSPParser, self).parse(handler, line_by_line)
