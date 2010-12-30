# Copyright (c) 2008-2010 Thomas Lotze
# See also LICENSE.txt

import ConfigParser
import logging
import os
import os.path
import sys
import pkg_resources


py_version = sys.version[:3]

config_file = pkg_resources.resource_stream(__name__, "defaults.cfg")
config = ConfigParser.ConfigParser()
config.readfp(config_file)


class InstallPyGTK(object):
    """A zc.buildout recipe for installing pygtk & friends.

    Assumes the cairo, gobject and gtk+ C libraries to be installed
    system-wide.

    """

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options

        for key, value in config.defaults().items():
            options.setdefault(key, value)

        self.location = options.setdefault("location", os.path.join(
            buildout["buildout"]["parts-directory"], name))

        # normalise options for enabling and disabling projects, apply
        # dependencies between projects and build the python path
        path = []
        need = False
        for project in ('pywebkitgtk', 'pygtk', 'pygobject', 'pycairo'):
            if options[project] not in ('', 'false', '0', 'False', 'no'):
                need = True
                py_path = os.path.join(
                    self.location, project,
                    'lib', 'python%s' % py_version, 'site-packages')
                path.append(py_path)
                # XXX evaluate pygtk.pth
                if project in ('pygobject', 'pygtk'):
                    path.append(os.path.join(py_path, 'gtk-2.0'))
            options[project] = str(need)

        options['path'] = '\n'.join(path)

    def install(self):
        # set up things
        logger = logging.getLogger(self.name)

        cmmi = self.egg = pkg_resources.load_entry_point(
            "zc.recipe.cmmi", "zc.buildout", "default")

        # Parametrise each build with the paths to preceding builds in order
        # to rebuild dependent components as needed.
        # Put the target python in front of the cmmi recipes' binary path
        # since the projects to be built don't have a --with-python option.
        # Be careful not to put any random information in the parameters to
        # keep the shared builds intact.
        path = [os.path.dirname(sys.executable), os.environ["PATH"]]
        pkg_config_path = []

        # build python bindings
        build_locations = {}
        for project in ("pycairo", "pygobject", "pygtk", "pywebkitgtk"):
            if self.options[project] == 'False':
                continue
            environment = ('PATH=%s\n'
                           'PYTHON=%s\n'
                           'PKG_CONFIG_PATH=%s'
                           % (':'.join(path),
                              sys.executable,
                              ':'.join(pkg_config_path)))
            options = dict(url=self.options[project+'-url'],
                           md5sum=self.options[project+'-md5sum'],
                           environment=environment,
                           shared=self.options.get('shared', 'True'))
            logger.info('Building %s.' % project)
            dest = cmmi(self.buildout, self.name, options).install()

            build_locations[project] = dest

            # update parameters for building the next project
            pkg_config_path.append(os.path.join(dest, 'lib', 'pkgconfig'))
            path.append(os.path.join(dest, 'bin'))

        # create part directory
        if not os.path.isdir(self.location):
            os.mkdir(self.location)

        for project, dest in build_locations.iteritems():
            link_path = os.path.join(self.location, project)
            if os.path.islink(link_path):
                os.unlink(link_path)
            os.symlink(dest, link_path)

        return [self.location] + build_locations.values()

    def update(self):
        pass
