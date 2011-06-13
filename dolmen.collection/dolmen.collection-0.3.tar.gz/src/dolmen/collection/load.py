# -*- coding: utf-8 -*-

from pkg_resources import iter_entry_points

_marker = object()
_loaded = False


def loadComponents():
    """Goes through all available components loaders and call them.
    """
    global _loaded
    if _loaded:
        return
    for loader_entry in iter_entry_points('dolmen.collection.components'):
        loader = loader_entry.load()
        if not callable(loader):
            raise TypeError(
                'Entry point %r should be a callable to register  components'
                % loader_entry.name)
        loader()
    _loaded = True


def reloadComponents():
    """Reload all components.

    Mainly used by testing layers.
    """
    global _loaded
    _loaded = False
    loadComponents()
