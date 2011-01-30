# -*- coding:utf-8 -*-
#
# kurzfile/__init__.py
#
"""A package for handling Kurzweil K-series object files.

Thanks to Geoffrey Mayer <geoffrey@nktelco.net> for reverse engneering the
format and providing his findings to the public.

"""

from kurzfile.release import version as __version__
from kurzfile.api import *
from kurzfile.util import *
from kurzfile.constants import *
