"""Interface and management of extensions.

Extensions are Python scripts/modules which are loaded and searched for extension entries.

If an extension wants to register a new command-line sub-command it must define an
entry called `cmds` and initialize it with a cmd.CommandTable instance.

The extension may also define a function for setting up the extension once it is loaded,
`presetup` will be called as soon as the extension has been loaded while `postsetup` is
called after all extensions are loaded.
Both functions is sent the `ui` argument which can be used to access the verison string,
the configuration or outputting data to the user.
Defining the functions with a `**kwarg` argument is a good idea as it allows for
extra arguments to be added in the future.

The help text for the extension is taken from the docstring of the script or module.

If there is a problem using the extension in the setup functions it must raise an
ExtensionError exception, this reports back that the extension should not be used
and displays the problem to the user.
"""

import sys
import os

__all__ = ("ExtensionError", "Extension", "Manager",
           )

class ExtensionError(Exception):
    pass

class Extension(object):
    name = None
    path = None
    doc  = None

    cmds = None
    presetup = None
    postsetup = None

    def __init__(self, name, path, doc, cmds, presetup, postsetup):
        self.name = name
        self.path = path
        self.doc  = doc

        self.cmds = cmds
        self.presetup = presetup
        self.postsetup = postsetup

class Manager(object):
    def __init__(self):
        self._exts = {}

    def __iter__(self):
        return self._exts.itervalues()

    def __getitem__(self, name):
        return self._exts[name]

    def __setitem__(self, name, ext):
        self._exts[name] = ext

    def __contains__(self, name):
        return name in self._exts

    def setup(self, ui, cmds):
        if "extensions" not in ui.config:
            return

        # Put the current directory in the search path for modules
        sys.path.append(os.path.abspath(os.path.curdir))

        for name, path in ui.config["extensions"]:
            path = path.strip()
            g = {}
            l = {}
            # A directory indicates that a python module should be imported
            # and not a script
            if path and os.path.isdir(path):
                path = os.path.abspath(path)
                sys.path.append(path)
                path = None
            if path:
                try:
                    execfile(path, g, l)
                except Exception, e:
                    ui.warnl("WARN: exception while loading %s for extension %s, ignoring extension: %s" % (path, name, e))
                    continue
            else:
                try:
                    m = __import__(name, g, l)
                    if name.find(".") != -1:
                        for subm in name.split(".")[1:]:
                            m = getattr(m, subm)
                    l = m.__dict__
                except ImportError, e:
                    ui.warnl("WARN: could not import extension %s, ignoring extension: %s" % (name, e))
                    continue
                except Exception, e:
                    ui.warnl("WARN: exception while importing extension %s, ignoring extension: %s" % (name, e))
                    continue

            doc = l.get("__doc__", None)
            extcmds = l.get("cmds", None)
            presetup = l.get("presetup", None)
            postsetup = l.get("postsetup", None)
            if presetup and not callable(presetup):
                ui.warnl("WARN: 'presetup' in extension %s is not callable" % name)
                presetup = None
            if postsetup and not callable(postsetup):
                ui.warnl("WARN: 'postsetup' in extension %s is not callable" % name)
                postsetup = None
            if not extcmds and not presetup and not postsetup:
                ui.warnl("WARN: %s is not an extension, ignoring entry" % name)
                continue

            if doc:
                doc = ("".join(doc.splitlines(True)[1:])).lstrip()

            ext = Extension(name, path, doc, extcmds, presetup, postsetup)
            self[name] = ext
            if ext.presetup:
                ext.presetup(ui)
        for ext in self:
            if ext.postsetup:
                ext.postsetup(ui)
            if ext.cmds:
                cmds.update(ext.cmds)
