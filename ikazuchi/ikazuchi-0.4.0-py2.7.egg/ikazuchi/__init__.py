# -*- coding: utf-8 -*-

from os.path import (dirname, realpath, join as pathjoin)

BASE_DIR = dirname(realpath(__file__))
CORE_DIR = pathjoin(BASE_DIR, "core")
LOCALE_DIR = pathjoin(BASE_DIR, "locale")

from ikazuchi import main
