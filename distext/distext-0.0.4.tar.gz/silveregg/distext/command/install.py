import os
import sys
import copy
import shutil
import collections
import tempfile

if "setuptools" in sys.modules:
    import setuptools
    from setuptools.command.install \
        import \
            install as old_install
    # Copied from setuptools - we need to modify the function because the
    # original setuptools install_cmd.run change its behavior depending on its
    # stack...
    from distutils.command.install import install as _install
    def _setuptools_run(self):
        # Explicit request for old-style install?  Just do it
        if self.old_and_unmanageable or self.single_version_externally_managed:
            return _install.run(self)

        # Attempt to detect whether we were called from setup() or by another
        # command.  If we were called by setup(), our caller will be the
        # 'run_command' method in 'distutils.dist', and *its* caller will be
        # the 'run_commands' method.  If we were called any other way, our
        # immediate caller *might* be 'run_command', but it won't have been
        # called by 'run_commands'.  This is slightly kludgy, but seems to
        # work.
        #
        caller = sys._getframe(3)
        caller_module = caller.f_globals.get('__name__','')
        caller_name = caller.f_code.co_name

        if caller_module != 'distutils.dist' or caller_name!='run_commands':
            # We weren't called from the command line or setup(), so we
            # should run in backward-compatibility mode to support bdist_*
            # commands.
            _install.run(self)
        else:
            self.do_egg_install()
    old_install.run = _setuptools_run
else:
    from distutils.command.install \
        import \
            install as old_install
from distutils.util \
    import \
        change_root

import jinja2

from silveregg.distext.utils \
    import \
        subst_vars, ensure_directory

_SCHEME = {
        "bindir": "$prefix/bin",
        "libdir": "$prefix/lib",
        "sysconfdir": "$prefix/etc",
        "localstatedir": "$prefix/var",
        "wwwdatadir": "$localstatedir/www",
}

class Install(old_install):
    user_options = old_install.user_options + [
            ("bindir=", None,
              "user executables (default : %s)" % _SCHEME["bindir"]),
            ("libdir=", None,
              "object code library path (default : %s)" % _SCHEME["libdir"]),
            ("sysconfdir=", None,
             "read-only single-machine data (default : %s)" % _SCHEME["sysconfdir"]),
            ("localstatedir=", None,
             "modifiable single-machine data (default : %s)" % _SCHEME["localstatedir"]),
            ("wwwdatadir=", None,
             "www data directory for static website content (default : %s)" % _SCHEME["wwwdatadir"])]

    def initialize_options(self):
        old_install.initialize_options(self)
        self.bindir = None
        self.libdir = None
        self.sysconfdir = None
        self.localstatedir = None
        self.wwwdatadir = None
        self._outputs = []

    def finalize_options(self):
        old_install.finalize_options(self)

        self._raw_scheme = copy.deepcopy(_SCHEME)
        self._raw_scheme["prefix"] = self.prefix

        for attr in _SCHEME.keys():
            value = getattr(self, attr)
            if value is None:
                self._raw_scheme[attr] = _SCHEME[attr]
            else:
                self._raw_scheme[attr] = value

        if self.root is not None:
            for attr in _SCHEME.keys() + ["prefix"]:
                self._raw_scheme[attr] = change_root(self.root, getattr(self, attr))

        scheme = {}
        for k in self._raw_scheme:
            scheme[k] = subst_vars(self._raw_scheme[k], self._raw_scheme)
        self._scheme = scheme

        self._custom_data_files = []
        # XXX: refactor this mess
        for section in self.distribution.custom_data_files:
            if len(section) == 2:
                path, files = section
                target_dir = self.get_expanded_path(path)
                installed_files = []
                for f in files:
                    target = os.path.join(target_dir, os.path.basename(f))
                    installed_files.append((f, target))
            elif len(section) == 3:
                path, files, source_dir = section
                for f in files:
                    if not os.path.commonprefix([source_dir, f]) == source_dir:
                        raise ValueError("Invalid source_dir %s for file %s" % \
                                         (source_dir, f))
                target_dir = self.get_expanded_path(path)
                installed_files = [(f, os.path.join(target_dir,
                                                    os.path.relpath(f, source_dir))) \
                                   for f in files]
            else:
                raise ValueError("Invalid tuple for custom_data_files")
            self._custom_data_files.extend(installed_files)

    def get_expanded_scheme(self):
        assert self.finalized == 1
        return self._scheme

    def get_expanded_path(self, path):
        return subst_vars(path, self._scheme)

    def run(self):
        old_install.run(self)

        for source, target in self._custom_data_files:
            if not os.path.exists(os.path.dirname(target)):
                os.makedirs(os.path.dirname(target))
            shutil.copy(source, target)

        build_command = self.get_finalized_command("build")
        build_init_scripts = build_command.build_init_scripts
        for script in self.distribution.init_scripts:
            target = self.get_expanded_path(script.destination)
            ensure_directory(target)
            source = os.path.join(build_init_scripts, script.encoded_path(target))
            shutil.copy(source, target)

    def get_outputs(self):
        self._outputs += old_install.get_outputs(self)
        self._outputs += [target for source, target in self._custom_data_files]
        return self._outputs
