# -*- coding: utf-8 -*-
import sys
import os

def abracadabra():
    paths = sys.path[:]
    match_path = "%(sep)sDjango" % {'sep': os.sep}
    for path in paths:
        if match_path in path or match_path.lower() in path:
            del sys.path[sys.path.index(path)]
    modules = sys.modules.keys()
    for module in modules:
        if module.startswith('django'):
            del sys.modules[module]

