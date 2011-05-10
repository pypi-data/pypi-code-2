# -*- coding: utf-8 -*-


# Podis -- Retrieve INSEE codes of french communes from their postal distributions
# By: Romain Soufflet <rsoufflet@easter-eggs.com>
#
# Copyright (C) 2010 Easter-eggs
#
# This file is part of Podis.
#
# Podis is free software; you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Podis is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


"""Little library for podis"""


import unicodedata


def simplify_route_name(s):
    """Convert unicode string to a uppercase space-separated slug."""
    return ' '.join(
        'ST' if word == 'SAINT'
        else 'STE' if word == 'SAINTE'
        else 'SAINTES' if word == 'STES' # Saintes is a commune and must not be abbreviated.
        else str(int(word)) if word.isdigit() # Remove leading zeros from cedex numbers.
        else word
        for word in ''.join(simplify_route_name2(s)).strip().split()
        ) or None


def simplify_route_name2(s):
    if s is not None:
        previous = None
        for c in unicodedata.normalize('NFD', unicode(s).replace(u'Œ', u'OE').replace(u'œ', u'oe').replace(
                u'’', u"'")).encode('ASCII', 'ignore').upper():
            if c not in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                if previous != ' ':
                    yield ' '
                    previous = ' '
            else:
                if previous is not None \
                        and ('0' <= c <= '9' and 'A' <= previous <= 'Z' or 'A' <= c <= 'Z' and '0' <= previous <= '9'):
                    # Add space between number and words (=> replace "CEDEX10" with "CEDEX 10").
                    yield ' '
                yield c
                previous = c
