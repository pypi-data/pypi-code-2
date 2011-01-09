# -*- coding: utf-8 -*-

__VERSION__ = "0.1" # 2011-01-08

# <p>Copyright © 2011 T.C. Chou, Cirton Ltd</p>
# <p>This module is part of the Tabledown package, which is released under a
# BSD-style licence.</p>

import licences

#
# 2011-01-08 TCC Initial Release.

class TDException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
