# -*- coding: utf-8 -*-

import gettext
from locale import *

from ikazuchi import LOCALE_DIR

t = gettext.translation("ikazuchi", localedir=LOCALE_DIR, fallback=True)
_ = t.ugettext
