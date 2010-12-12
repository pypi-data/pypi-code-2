# -*- coding: utf-8 -*-

"""The application's Globals object"""

__all__ = ['Globals']
from libacr.views.manager import ViewsManager
from libacr.plugins.manager import PluginsManager
from libacr.mediaWorker import start_media_worker


class Globals(object):
    """Container for objects available throughout the life of the application.

    One instance of Globals is created during application initialization and
    is available during requests via the 'app_globals' variable.

    """

    def __init__(self):
        self.acr_viewmanager = ViewsManager()
        self.plugins = PluginsManager()
        """Do nothing, by default."""
        from turbomail.adapters import tm_pylons
        tm_pylons.start_extension()
