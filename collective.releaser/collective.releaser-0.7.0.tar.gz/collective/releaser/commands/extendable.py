"""Extendable command"""
import os
import pkg_resources
from distutils.cmd import Command

class Extensible(object):

    def __init__(self, cmd, *options):
        self.cmd = cmd
        self.options = options
        self._ext = {}

    def load(self):
        for opt in self.cmd.extensible_options:
            ep = ExtensionPoint(self.cmd, opt)
            ep.load()
            self._ext[opt] = ep

    def run(self, name):
        self._ext[name].run()

class ExtensionPoint(object):

    def __init__(self, cmd, name):
        self.name = name.replace('-', '_')
        self.cmd = cmd
        self._entries = []

    def load(self, name=None):
        if name is None:
            name = self.cmd.get_command_name()
            entry_point = 'distutils.%s.%s' % (name, self.name)
        else:
            entry_point = name
        for ep in pkg_resources.iter_entry_points(entry_point):
            ep = self._load(ep)
            if ep is None or ep in self._entries:
                continue
            self._entries.append(ep)

    def _load(self, entry_point):
        values = getattr(self.cmd, self.name)
        if not isinstance(values, (list, tuple)):
            values = [values]
        if entry_point.name not in values:
            return None
        return entry_point.load()

    def run(self):
        for ep in self._entries:
            ep(self.cmd, self.name)

    def apply(self, name=None):
        self.load(name)
        self.run()

class ExtensibleCommand(Command):

    def __init__(self, dist):
        Command.__init__(self, dist)
        # this manages all extensions
        self._extensions = Extensible(self)

    def ensure_finalized(self):
        Command.ensure_finalized(self)
        # this loads all extensions in memory
        self._extensions.load()

    def run_extension(self, name):
        # this will build the filelist by running the plugins
        self._extensions.run(name)

