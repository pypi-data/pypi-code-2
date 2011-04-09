# -*- coding: utf-8 -*-
##############################################################################
#       Copyright (C) 2010, Joel B. Mohler <joel@kiwistrawberry.us>
#
#  Distributed under the terms of the GNU General Public License (GPLv2 or later)
#                  http://www.gnu.org/licenses/
##############################################################################
"""
fuzzyparsers library initialization
"""

from strings import default_match, fuzzy_match
from dates import *

# backwards compatibility function
sanitized_date = parse_date
