# -*- coding: utf-8 -*-

import os

from issues.plugin import PluginManager

HOOKS = None
initialized = False

def initialize():
    """Imports all python files from the hook directory."""
    global HOOKS
    if initialized:
        return
    HOOKS = PluginManager()
    HOOKS.add_directory(os.path.abspath(os.path.join(os.path.dirname(
        __file__))))
    HOOKS.rescan_directories()