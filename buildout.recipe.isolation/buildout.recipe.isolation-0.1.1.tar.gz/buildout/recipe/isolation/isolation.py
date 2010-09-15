# -*- coding: utf-8 -*-
import os
import shutil
import warnings
import logging

import pkg_resources
import zc.buildout.easy_install

from buildout.recipe.isolation.utils import as_bool

default_logger = logging.getLogger('buildout.recipe.isolation')


class Isolate(object):
    """zc.buildout recipe."""

    buildout = None
    name = None
    options = None
    links = None
    index = None
    created = []

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options
        self.logger = logging.getLogger(name)

        # Init required option dists... O.o
        dists = options['dists']

        # Init find-links & index
        links = options.get('find-links',
            buildout['buildout'].get('find-links'))
        if links:
            links = links.split()
            options['find-links'] = '\n'.join(links)
        else:
            links = ()
        self.links = links
        index = options.get('index', buildout['buildout'].get('index'))
        if index is not None:
            options['index'] = index
        self.index = index

        # Init dist-location & script-location
        parts_dir = self.buildout['buildout']['parts-directory']
        if options.get('dist-location') is None:
            options['dist-location'] = os.path.join(parts_dir, self.name)
        options['dist-location'] = os.path.realpath(options['dist-location'])
        if options.get('script-location') is None:
            dir_name = '%s-scripts' % self.name
            options['script-location'] = os.path.join(parts_dir,dir_name)
        options['script-location'] = os.path.realpath(options['script-location'])

        # Init the .pth file location
        if options.get('pth-file-location') is not None:
            # Ensure the file provided has a .pth extension
            # and that the destination actually exists
            pth_file = options['pth-file-location']
            basedir = os.path.dirname(pth_file)
            if not os.path.exists(basedir):
                raise IOError("The base directory for the pth file defined " \
                    "in %s section of your buildout does not exist. Please " \
                    "ensure that this directory exists prior to running " \
                    "buildout." % self.name)
            if pth_file.split('.')[-1] != 'pth':
                msg = "The defined pth file in %s section " \
                    "of your buildout does not have a .pth file extension. " \
                    % self.name
                warnings.warn(msg, RuntimeWarning)
        else:
            isolation_dir = options['dist-location']
            fname = '%s.pth' % self.name
            options['pth-file-location'] = os.path.join(isolation_dir, fname)

        # Init distribution directories eggs-directory & develop-eggs-directory
        options['eggs-directory'] = buildout['buildout']['eggs-directory']
        options['develop-eggs-directory'] = \
            buildout['buildout']['develop-eggs-directory']

        #assert options.get('unzip') in ('true', 'false', None)

        # Init the executable
        python = options.get('python', buildout['buildout']['python'])
        options['executable'] = buildout[python]['executable']

    def __create_location(self, loc):
        os.makedirs(loc)
        self.created.append(loc)

    def _setup_locs(self):
        opts = self.options
        parts_dir = self.buildout['buildout']['parts-directory']
        parts_dir = os.path.realpath(parts_dir)
        if opts['dist-location'].find(parts_dir) >= 0 \
           and not os.path.exists(opts['dist-location']):
            self.__create_location(opts['dist-location'])
        if opts['script-location'].find(parts_dir) >= 0 \
           and not os.path.exists(opts['script-location']):
            self.__create_location(opts['script-location'])

    def _copy_dist(self, dist, dest_dir):
        target = dist.location
        dest = os.path.join(dest_dir, target.split(os.sep)[-1])
        name = dist.project_name

        if os.path.exists(dest):
            self.logger.info("Distribution %s exists, not updating." % name)
            return dest

        if os.path.isdir(target):
            copy = shutil.copytree
        else:
            copy = shutil.copy2

        self.logger.info("Copying %s to the destination directory." % name)
        copy(target, dest)
        return dest

    def working_set(self, option_value, extra=()):
        """Separate method to just get the working set."""
        options = self.options

        distributions = [
            r.strip()
            for r in option_value.split('\n')
            if r.strip()]
        orig_distributions = distributions[:]
        distributions.extend(extra)

        if self.buildout['buildout'].get('offline') == 'true':
            ws = zc.buildout.easy_install.working_set(
                distributions, options['executable'],
                [options['develop-eggs-directory'], options['eggs-directory']]
                )
        else:
            ws = zc.buildout.easy_install.install(
                distributions, options['eggs-directory'],
                links = self.links,
                index = self.index, 
                executable = options['executable'],
                always_unzip=options.get('unzip') == 'true',
                path=[options['develop-eggs-directory']],
                newest=self.buildout['buildout'].get('newest') == 'true',
                )

        return orig_distributions, ws

    def get_filtered_working_set(self, in_ws, ex_ws):
        ws = pkg_resources.WorkingSet([])
        excluded_dists = ex_ws.by_key.keys()
        for name, dist in in_ws.by_key.iteritems():
            if name not in excluded_dists:
                ws.add(dist)
        return ws

    def isolate(self, working_set):
        """Given the a list of distributions, we will isolate them in a
        separate directory that has been predefined."""
        dists = [dist for dist in working_set.by_key.values()]
        options = self.options
        isolation_dir = options['dist-location']
        pth_list = []

        for dist in dists:
            path = self._copy_dist(dist, isolation_dir)
            pth_list.append(os.path.realpath(path))

        file = open(options['pth-file-location'], 'w')
        file.write('\n'.join(pth_list))
        file.close()

    def gen_scripts(self, reqs, ws):
        opts = self.options
        executable = os.path.realpath(opts['executable'])
        destination = os.path.realpath(opts['script-location'])
        scripts = None # place holder
        extra_pths = []
        if not as_bool(opts.get('exclude-own-pth')):
            extra_pths.append(opts['pth-file-location'])
        if opts.get('extra-pth') is not None:
            extra_pths.extend(opts['extra-pth'].split('\n'))
        return script_installer(reqs, ws, executable,
            destination, scripts, extra_pths, logger=self.logger)

    def install(self):
        options = self.options
        self._setup_locs()

        inclusion_reqs, inclusion_ws = self.working_set(
            self.options.get('dists', self.name))
        exclusion_reqs, exclusion_ws = self.working_set(
            self.options.get('exclude-dists', ''))

        ws = self.get_filtered_working_set(inclusion_ws, exclusion_ws)
        self.isolate(ws)
        generated_scripts = self.gen_scripts(inclusion_reqs, ws)

        record = self.created + generated_scripts
        return tuple(set(record))

    update = install


pth_init = """
import sys
def pth_injector(pth_file):
    path_file = open(pth_file, 'r')
    sys.path[0:0] = [line
        for line in path_file.read().split('\\n')
        if line is not None]

pth_files = %(pth_file_list)s
for pth in pth_files:
    pth_injector(pth)
"""

def script_installer(reqs, working_set, executable, dest,
            scripts=None,
            extra_pths=(),
            logger=default_logger,
            ):
    generated = []
    entry_points = []
    requirements = [x[1][0] for x in working_set.entry_keys.items()]

    if isinstance(reqs, str):
        raise TypeError('Expected iterable of requirements or entry points,'
                        ' got string.')

    for req in reqs:
        if req not in requirements:
            requirements.append(req)
    for req in requirements:
        if isinstance(req, str):
            req = pkg_resources.Requirement.parse(req)
            dist = working_set.find(req)
            for name in pkg_resources.get_entry_map(dist, 'console_scripts'):
                entry_point = dist.get_entry_info('console_scripts', name)
                entry_points.append(
                    (name, entry_point.module_name,
                     '.'.join(entry_point.attrs))
                    )
        else:
            entry_points.append(req)

    if extra_pths:
        initialization = pth_init % dict(pth_file_list=str(extra_pths))
    else:
        initialization = '\n'

    for name, module_name, attrs in entry_points:
        if name.startswith('easy_install'):
            continue
        if scripts is not None:
            sname = scripts.get(name)
            if sname is None:
                continue
        else:
            sname = name

        sname = os.path.join(dest, sname)
        generated.extend(
            _script(module_name, attrs,
                sname, executable, '',
                initialization, logger=logger)
            )

    return generated


def _script(module_name, attrs, dest, executable, arguments,
            initialization, logger=default_logger):
    generated = []
    script = dest
    if zc.buildout.easy_install.is_win32:
        dest += '-script.py'

    contents = script_template % dict(
        python = zc.buildout.easy_install._safe_arg(executable),
        module_name = module_name,
        attrs = attrs,
        arguments = arguments,
        initialization = initialization,
        )
    changed = not (os.path.exists(dest) and open(dest).read() == contents)

    if zc.buildout.easy_install.is_win32:
        # generate exe file and give the script a magic name:
        exe = script+'.exe'
        new_data = pkg_resources.resource_string('setuptools', 'cli.exe')
        if not os.path.exists(exe) or (open(exe, 'rb').read() != new_data):
            # Only write it if it's different.
            open(exe, 'wb').write(new_data)
        generated.append(exe)

    if changed:
        open(dest, 'w').write(contents)
        logger.info("Generated script %r.", script)

        try:
            os.chmod(dest, 0755)
        except (AttributeError, os.error):
            pass

    generated.append(dest)
    return generated

script_template = zc.buildout.easy_install.script_header + """\

%(initialization)s
import %(module_name)s

if __name__ == '__main__':
    %(module_name)s.%(attrs)s(%(arguments)s)
"""

