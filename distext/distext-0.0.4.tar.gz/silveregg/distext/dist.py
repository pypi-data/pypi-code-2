import os
import sys
import collections
try:
    from hashlib import md5
except ImportError:
    from md5 import md5

import jinja2

from silveregg.distext.utils import monkey_patch_mode
MONKEYPATCH_MODE = monkey_patch_mode()
if MONKEYPATCH_MODE == "setuptools":
    import setuptools
    from setuptools.dist \
        import \
            Distribution as OldDistribution
else:
    from distutils.dist \
        import \
            Distribution as OldDistribution
from distutils import errors

from silveregg.distext.command.sdist import Sdist
from silveregg.distext.command.install import Install
from silveregg.distext.command.build_py import BuildPy
from silveregg.distext.command.build import Build
from silveregg.distext.command.build_init_scripts import BuildInitScripts
DISTEXT_COMMANDS = {"sdist": Sdist, "install": Install, "build_py": BuildPy,
                    "build": Build, "build_init_scripts": BuildInitScripts}

if MONKEYPATCH_MODE in ["setuptools"]:
    from silveregg.distext.command.bdist_egg import BdistEgg
    DISTEXT_COMMANDS["bdist_egg"] = BdistEgg

class Distribution(OldDistribution):
    def __init__(self, attrs=None):
        self.custom_data_files = attrs.get("custom_data_files", [])

        self.init_scripts = attrs.get("init_scripts", [])
        self._check_init_scripts()

        self.scheme_module_path = attrs.get("scheme_module_path", None)
        if self.scheme_module_path is not None:
            if os.path.isabs(self.scheme_module_path):
                raise ValueError(
                    "scheme_module_path should be a relative path ( was %s)" \
                    % self.scheme_module_path)
        self._check_custom_data_files()

        OldDistribution.__init__(self, attrs)

    def _check_custom_data_files(self):
        for section in self.custom_data_files:
            files = section[1]
            for f in files:
                if isinstance(f, basestring):
                    if not os.path.exists(f):
                        raise errors.DistutilsSetupError(
                                "custom_data_files misconfiguration: file %s not found" % f)

    def _check_init_scripts(self):
        for script in self.init_scripts:
            if not isinstance(script, InitFile):
                raise errors.DistutilsSetupError("init_scripts misconfiguration: expects list of InitFile instances.")

    def get_command_class(self, command):
        if command in self.cmdclass:
            return self.cmdclass[command]
        elif command in  DISTEXT_COMMANDS:
            return DISTEXT_COMMANDS[command]
        else:
            return OldDistribution.get_command_class(self, command)

    def has_pure_modules(self):
        if self.scheme_module_path is not None:
            return True
        else:
            return OldDistribution.has_pure_modules(self)

    def has_init_scripts(self):
        return len(self.init_scripts) > 0

    def get_custom_data_files_sources(self):
        sources = []
        for section in self.custom_data_files:
            sources.extend(section[1])
        return sources

    def get_init_scripts(self):
        return [section.source for section in self.init_scripts]

if MONKEYPATCH_MODE == "setuptools":
    import distutils.dist, distutils.core, distutils.cmd
    for module in setuptools.dist, distutils.dist, distutils.core, distutils.cmd:
        module.Distribution = Distribution
else:
    import distutils.dist, distutils.core, distutils.cmd
    for module in distutils.dist, distutils.core, distutils.cmd:
        module.Distribution = Distribution

class InitFile(object):
    def __init__(self, source, destination, mode=0755, renderer=None):
        self.destination = destination

        if not isinstance(source, basestring):
            raise ValueError("InitFile source should be a string")
        if not os.path.exists(source):
            raise IOError("Init script source file %s not found" % source)

        self.source =  source
        self.is_finalized = False

        self.mode = mode

        if renderer is None or isinstance(renderer, collections.Callable):
            self.renderer = renderer
        else:
            raise ValueError("renderer source should be None or a callable")

    @property
    def content(self):
        if not self.is_finalized:
            raise ValueError("This instance need to be finalized before accessing the source attribute!")
        else:
            return self._content
        
    def encoded_path(self, path):
        return os.path.join(md5(path).hexdigest(),
                            os.path.basename(self.destination))

    def finalize(self, scheme):
        if self.renderer is None:
            fid = open(self.source)
            try:
                self._content = fid.read()
            finally:
                fid.close()
        else:
            ctx = RenderContext(scheme)
            fid = open(self.source)
            try:
                self._content = self.renderer(ctx, fid.read())
            finally:
                fid.close()
        self.is_finalized = True

class RenderContext(object):
    def __init__(self, env):
        self.env = env

    def render(self, content):
        template = jinja2.Template(content)
        return template.render(**self.env)
