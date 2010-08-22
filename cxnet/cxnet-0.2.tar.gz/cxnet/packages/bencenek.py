#!/usr/bin/env python3

try:
    import gettext
    transl = gettext.translation("packages", "./locale")
    # transl = gettext.translation("packages", "/usr/share/locale") #Ha rootként tudom elhelyezni.
    _ = transl.gettext
except ImportError:
    _ = lambda str: str

import math
import sys

for i in range(315//5):
    print (" "*int(30*math.sin(i/10)+20*math.cos(i/ 7)+50), "**              **")

l=range(13)
print(l)
