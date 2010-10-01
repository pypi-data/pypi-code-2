# -*- coding: utf-8 -*-

from inspect import isclass
import logging
import os
from pkg_resources import parse_version
import sys

from django.dispatch import Signal


log = logging.getLogger(__name__)

# Signals

SIG_PLUGINLIST_CHANGED = Signal()
SIG_DIRECTORIES_CHANGED = Signal()
SIG_PLUGIN_ADDED = Signal(providing_args=["plugin"])
SIG_PLUGIN_REMOVED = Signal()

# Error objects

class PluginLoadError(StandardError):
    pass


class PluginImportError(StandardError):
    pass


class Plugin(object):

    id = None
    description = None
    name = None
    version = "0.0.1"

    def load(self):
        raise NotImplementedError

    def unload(self):
        raise NotImplementedError


class PluginManager(object):

    def __init__(self):
        self._active_plugins = []
        self._directories = []
        self._plugins = []

    def add_directory(self, path):
        if path in self.list_directories():
            log.warning("")
            return False
        if not os.path.isdir(path):
            log.warning("")
            return False
        if not os.access(path, os.R_OK):
            log.warning("")
            return False
        if path not in self.list_directories():
            self._directories.append(path)
        self._directories.sort()
        self.rescan_directories()
        SIG_DIRECTORIES_CHANGED.send(sender=self)
        return True

    def clear_directories(self):
        while self.list_directories():
            self.remove_directory(self.list_directories()[0])

    def list_directories(self):
        return tuple(self._directories)

    def list_plugins(self):
        return self._plugins

    def plugin_is_active(self, plugin):
        for item in self._active_plugins:
            if item.id == plugin.id:
                return True
        return False

    def remove_directory(self, path):
        if path in self.list_directories():
            self._directories.pop(self._directories.index(path))
        if path in sys.path:
            sys.path.remove(path)
        SIG_DIRECTORIES_CHANGED.send(sender=self)

    def rescan_directories(self):
        def in_list(item, l):
            for x in l:
                if x.id == item.id \
                and x.version == item.version:
                    return True
            return False
        new = dict()
        for path in self._directories:
            for plugin in self.scan_directory(path):
                if not new.has_key(plugin.id) \
                or parse_version(new[plugin.id].version) < parse_version(plugin.version):
                    new[plugin.id] = plugin
                else:
                    if new.has_key(plugin.id):
                        raise PluginImportError, \
                              "Cannot import plugin %r, duplicate id found." % plugin
        old = self._plugins
        new = new.values()
        changed = False
        for plugin in old:
            if not in_list(plugin, new):
                changed = True
                if self.plugin_is_active(plugin):
                    self.deactivate_plugin(plugin)
                SIG_PLUGIN_REMOVED.send(sender=self)
        for plugin in new:
            if not in_list(plugin, old):
                changed = True
                #if plugin.id in self.app.config.get("plugin.active_ids"):
                    #self.activate_plugin(plugin)
                # FIXME: Plugins werden aktuell automatisch aktiviert
                self.activate_plugin(plugin)
                SIG_PLUGIN_ADDED.send(sender=self, plugin=plugin)
        #if changed:
            #dispatcher.send(SIG_PLUGINLIST_CHANGED, self)
        self._plugins = new
        if changed:
            SIG_PLUGINLIST_CHANGED.send(sender=self)

    def scan_directory(self, path):
        if path not in sys.path:
            sys.path.append(path)
        plugins = []
        for item in os.listdir(path):
            if not item.endswith(".py") \
               or item.startswith(".") \
               or item.endswith(".pyc") \
               or item.startswith("__"):
                continue
            full_path = os.path.join(path, item)
            if not os.path.isfile(full_path):
                continue
            # Let's try to import it
            try:
                mod = __import__(os.path.splitext(item)[0])
            except ImportError:
                import traceback; traceback.print_exc()
                log.warning("Failed to import %r from %r", item, path)
                continue
            # Search for Plugin classes
            for name in dir(mod):
                if name.startswith("_"):
                    continue
                obj = getattr(mod, name)
                if isclass(obj) \
                and issubclass(obj, Plugin) \
                and obj != Plugin \
                and obj not in plugins \
                and obj.id != None:
                    plugins.append(obj)
        return plugins

    def activate_plugin(self, plugin):
        if not isclass(plugin) \
        or not issubclass(plugin, Plugin):
            return
        for item in self._active_plugins:
            if item.id == plugin.id:
                return
        i = plugin()
        self._active_plugins.append(i)
        i.load()

    def deactivate_plugin(self, plugin):
        if not isclass(plugin) \
        or not issubclass(plugin, Plugin):
            return
        for i in range(len(self._active_plugins)):
            item = self._active_plugins[i]
            if item.id == plugin.id:
                item.unload()
                self._active_plugins.pop(i)
                return

    def by_id(self, id, active_only=True):
        if active_only:
            plugins = self._active_plugins
        else:
            plugins = self._plugins
        if not plugins:
            raise PluginLoadError, "No active plugins found"
        for pl in plugins:
            if pl.id == id:
                return pl
        raise PluginLoadError, "Failed to load plugin with id %r" % id

    def has_active_plugins(self):
        return len(self._active_plugins) > 0