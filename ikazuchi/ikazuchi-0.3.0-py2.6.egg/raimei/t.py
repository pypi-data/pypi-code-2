# -*- coding: utf-8 -*-

import pkg_resources

for plugin in pkg_resources.iter_entry_points('vim_plugin'):
    print plugin
