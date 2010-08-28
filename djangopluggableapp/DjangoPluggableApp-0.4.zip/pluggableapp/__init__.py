# -*- coding: utf-8 -*-
import logging
from pluggableapp.core import PluggableApp

logging.basicConfig(level=logging.ERROR)

PluggableApp.setLevel(logging.ERROR)

setLevel = PluggableApp.setLevel
initialize = PluggableApp.initialize
patterns = PluggableApp.patterns


