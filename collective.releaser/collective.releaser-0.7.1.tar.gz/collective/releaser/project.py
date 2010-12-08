# -*- coding: utf-8 -*-
# Copyright (C)2007 Ingeniweb

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING. If not, write to the
# Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
from multiprocessing import Pool
from optparse import OptionParser
import ConfigParser
from itertools import chain
import os
import md5
import re
import sys
import shutil
import distutils
from glob import glob
from fnmatch import fnmatch
from tempfile import mkdtemp

from zc.buildout.buildout import Buildout
from zc.buildout.easy_install import Installer, MissingDistribution
from distutils.errors import DistutilsError

from collective.releaser import base
from collective.releaser import packet
from collective.releaser.base import savewd, display, display_step, runwait

join = os.path.join

extract_path = re.compile(r'^((?:htt(?:p|ps)|svn|file)://)(.*?)/?$')
is_svn = re.compile(r'^((?:htt(?:p|ps)|svn|file)://)(.*?)/?$')

def _extract_url(url):
    extracted = extract_path.findall(url)
    protocol = extracted[0][0]
    path = extracted[0][1].split('/')
    return protocol, path

@savewd
def make_release(version=None, release=None,
                 prod_cfg='prod.cfg', dev_cfg='dev.cfg',
                 verbose=False):
    """this is called when a release is made over a buildout"""
    if not base.has_svn_support():
        raise base.ReleaseError('You need Subversion to create a release tag')

    # first, let's check we are in the buildout folder
    dir = os.getcwd()
    if 'buildout.cfg' not in os.listdir(dir):
        base.ReleaseError('You are not in a buildout folder')

    # next, let's create a branch for the release
    # after we asked the user what is the version to release
    parser = OptionParser()
    parser.add_option("-v", "--version", dest="version",
                      help="Version to release",
                      default=version, metavar="VERSION")
    parser.add_option("-d", "--dev-config", dest="dev_cfg",
            help="A .cfg with develop egg to include in the tarball. Default: %s" % dev_cfg,
                      default=dev_cfg, metavar="DEV_CFG")
    parser.add_option("-t", "--target-config", dest="prod_cfg",
                      help="A .cfg to use for the release. Default: %s" % prod_cfg,
                      default=prod_cfg, metavar="TARGET_CFG")
    parser.add_option("--no-archive", dest="release",
                      help="Only tag the project. Don't create an archive.",
                      default=True, action="store_false")
    parser.add_option("--verbose", dest="verbose",
                      help="More print",
                      action='store_true', default=verbose)
    options, args = parser.parse_args()

    dev_cfg = options.dev_cfg
    prod_cfg = options.prod_cfg

    verbose = options.verbose

    if version is None:
        version = options.version

    if release is None:
        release = options.release

    if version is None:
        version = raw_input('What version you are releasing ? ')

    if release and (not os.path.isfile(dev_cfg) or not os.path.isfile(prod_cfg)):
        parser.error('Bad config files')

    # get full path to develop eggs
    if os.path.isfile(dev_cfg):
        buildout_dev = Buildout(dev_cfg, [])
        develop_eggs = buildout_dev['buildout'].get('develop')
        develop_eggs = [os.path.abspath(e.strip()) for e in develop_eggs.split('\n')]
        develop_eggs = [e for e in develop_eggs if e]
    else:
        develop_eggs = []

    # were are we ?
    url = base.get_svn_url()

    # let's get the releases base folder
    protocol, path = _extract_url(url)
    path[-1] = 'releases'
    releases = '%s%s' % (protocol, '/'.join(path))

    # creates it if not found
    base.svn_mkdir(releases)

    # and the current version
    release = '%s/%s' % (releases, version)

    # if exists, let's drop it
    base.svn_remove(release)

    # now let's create the branch
    base.svn_copy(url, release, 'creating %s release for project' % version)

    # let's get it to add a version.txt file in the buildout root
    rep = mkdtemp('project_release')
    try:
        base.svn_checkout(release, rep)
        os.chdir(rep)
        version_file = join(rep, 'version.txt')
        fd = open(version_file, 'w')
        fd.write(version)
        fd.close()
        base.svn_add(version_file)
        msg = 'Added version file to buildout.'
        display_step(msg, verbose)

        eggs = {}
        if release and develop_eggs:
            # release eggs
            set_option(dev_cfg, 'buildout', 'develop', '\n'.join(develop_eggs))
            eggs = release_eggs(version=version, verbose=verbose,
                                prod_cfg=prod_cfg, dev_cfg=dev_cfg)

            # restore dev.cfg
            os.remove(dev_cfg)
            base.svn_up(dev_cfg)

            # fix buildout.cfg
            if prod_cfg != 'buildout.cfg':
                set_option('buildout.cfg', 'buildout', 'extends', prod_cfg)
            for egg, ver in eggs.items():
                set_option('buildout.cfg', 'versions', egg, ver)
            eggs_versions = ', '.join(sorted(['%s=%s' % egg for egg in eggs.items()]))
            msg += ' Set versions to %s' % eggs_versions

            base.svn_commit(msg)

            if eggs:
                # archive
                py_version = 'py%s.%s' % sys.version_info[0:2]
                archive = join(dir, 'release-eggs-%s-%s.tar.gz' % (version, py_version))
                eggs = project_eggs('buildout.cfg', archive, filter_eggs=eggs.keys(),
                                    verbose=verbose)
                display('Archive created at %s with %s' % (archive, ' '.join(eggs)))
            else:
                display('There is no eggs to release')
        else:
            base.svn_commit(msg)

    finally:
        shutil.rmtree(rep, ignore_errors=True)

def parse_url(url):
    """return base_url, cfg::

        >>> from collective.releaser.project import parse_url
        >>> parse_url('file:///svn.sf.net/')
        ('file:///svn.sf.net', 'buildout.cfg')
        >>> parse_url('file:///svn.sf.net/sample.cfg')
        ('file:///svn.sf.net', 'sample.cfg')
    """
    if not url.endswith('.cfg'):
        if url.endswith('/'):
            url = url[:-1]
        return url, 'buildout.cfg'
    url = url.split('/')
    filename = url.pop()
    return '/'.join(url), filename

def diff_releases(old=None, new=None, result=None):
    """takes two tarballs, and generates a diff one"""
    if old is None:
        if len(sys.argv) < 3:
            print 'Usage %s old_tarball new_tarball [diff_tarball]' % \
                sys.argv[0]
            sys.exit(0)
        old = sys.argv[1]
        new = sys.argv[2]
        if len(sys.argv) > 3:
            result = sys.argv[3]

    old_tarball = base.TarFile.open(old)
    new_tarball = base.TarFile.open(new)
    old_name = os.path.split(old)[-1]
    new_name = os.path.split(new)[-1]
    root_old_name = '.'.join(old_name.split('.')[:-1])
    root_new_name = '.'.join(new_name.split('.')[:-1])

    if result is None:
        result = '%s-to-%s.tgz' % (root_old_name, root_new_name)
        working_dir = os.path.realpath(os.getcwd())
    else:
        working_dir, result = os.path.split(result)
        working_dir = os.path.realpath(working_dir)

    old_files = {}
    for f in old_tarball.getmembers():
        old_files[f.name] = f

    tmp = mkdtemp()

    display('Selecting files')
    for f in new_tarball.getmembers():
        if f.name in old_files:
            if f.isfile():
                # if its a file checking the diff
                old_file = old_files[f.name]
                old_content = old_tarball.extractfile(old_file)
                old_content = old_content.read()
                new_content = new_tarball.extractfile(f).read()
                if old_content == new_content:
                    continue
        new_tarball.extract(f, tmp)

    # now writing the diff tarball
    display('Writing archive')
    archive_contents(result, tmp)
    # the tarball is create in the folder up `tmp`, let's move it
    topdir = os.path.split(tmp)[0]
    shutil.move(join(topdir, result), join(working_dir, result))
    display('Diff done.')

@savewd
def archive_contents(archive, location, exclude=None, source=True):
    """generates the tarball"""
    location = os.path.realpath(location)
    # we want a relative storage
    os.chdir(location)
    dirname, name = os.path.split(location)
    tar = base.TarFile.open(join(dirname, archive), 'w:gz')
    if exclude is None:
        exclude = []
    else:
        exclude = [os.path.realpath(join(location, sub))
                   for sub in exclude]
    try:
        for root, dirs, filenames in os.walk('.'):
            if '.svn' in root.split(os.path.sep):
                continue
            skip = False
            for excluded in exclude:
                if os.path.realpath(root).startswith(excluded):
                    skip = True
                    break
            if skip:
                continue
            # archiving empty dirs too
            for dir_ in dirs:
                if '.svn' in dir_.split(os.path.sep):
                    continue
                fullpath = join(root, dir_)
                if os.listdir(fullpath) == []:
                    arcname = fullpath.replace(location, '.')
                    tar.add(fullpath, arcname, False)
            for filename in filenames:
                if filename in ('.installed.cfg', '.Python'):
                    continue
                if source and filename.split('.')[-1] in ('pyc', 'pyo'):
                    continue
                path = join(root, filename)
                arcname = path.replace(location, '.')
                tar.add(path, arcname, False)
    finally:
        tar.close()

def set_option(filename, section, option, value):
    """Setting option."""
    config = ConfigParser.ConfigParser()
    config.read([filename])
    if section not in config.sections():
        config.add_section(section)
    config.set(section, option, value)
    fd = open(filename, 'w')
    try:
        config.write(fd)
    finally:
        fd.close()

def get_option(filename, section, option):
    """Reading option."""
    config = ConfigParser.ConfigParser()
    config.read([filename])
    return config.get(section, option)

def _easy_install():
    """return easy_install binary"""
    if sys.platform == 'win32':
        found = glob(join('Scripts', 'easy_install*'))
        target = join('Scripts', 'easy_install.exe')
    else:
        found = glob(join('bin', 'easy_install*'))
        target = join('bin', 'easy_install')

    if target in found:
        return target
    for binary in found:
        if os.path.exists(binary):
            return binary
    return 'easy_install'

def _python(home_dir=""):
    """returns python bin"""
    if sys.platform == 'win32':
        found = glob(join(home_dir, 'Scripts', 'python*'))
        target = join(home_dir, 'Scripts', 'python.exe')
    elif sys.platform == 'darwin':
        found = glob(join(home_dir, 'bin', 'Python*'))
        found.extend(glob(join(home_dir, 'bin', 'python*')))
        target = join(home_dir, 'bin', 'python')
    else:
        found = glob(join(home_dir, 'bin', 'python*'))
        target = join(home_dir, 'bin', 'python')

    if target in found:
        return target
    for binary in found:
        if os.path.exists(binary):
            return binary
    return 'python'

def _set_dynlibs(root):
    """win32: Makes sure libpython*.a is copied beside the Python executable"""
    main_dir = os.path.dirname(sys.executable)
    lib_dir = join(main_dir, 'libs')
    name = 'libpython*.a'
    libs = glob(join(lib_dir, name))
    libs_dir = join(root, 'libs')
    if not os.path.exists(libs_dir):
        os.mkdir(libs_dir)
    for lib in libs:
        libfilename = os.path.split(lib)[-1]
        shutil.copy(lib, join(libs_dir, libfilename))

def _make_python(location='.'):
    # let's generate a virtualenv python
    # to make sure we don't loose eggs
    old = sys.argv
    try:
        sys.argv = ['project_deploy', '--no-site-packages', location, '--quiet']
        from virtualenv import main
        try:
            def after_install(options, home_dir):
                """Creates a `python` script"""
                installed = _python(home_dir)
                if sys.platform == 'win32':
                    wanted = 'python.exe'
                else:
                    wanted = 'python'
                if os.path.split(installed)[-1] != wanted:
                    dirname = os.path.dirname(installed)
                    shutil.copyfile(installed, join(dirname,
                                                            wanted))
                    #make it executable
                    try:
                        os.chmod(join(dirname, wanted), 755)
                    except OSError:
                        pass # win32 error, or rights error

                # Make sure to also copy distutils.cfg, if existing
                # This allows mingw32 to work inside the virtualenv too
                distutils_path = distutils.__path__[0]
                distutils_cfg = os.path.join(distutils_path, 'distutils.cfg')
                if os.path.exists(distutils_cfg):
                    distutils_dir = os.path.join(home_dir, 'lib', 'distutils')
                    dest = os.path.join(distutils_dir, 'distutils.cfg')
                    shutil.copyfile(distutils_cfg, dest)

            main()
            #XXX: this is a hack: the after_install is never called in
            # the main(). This should be fixed otherway
            after_install(None, location)
        except OSError:
            # file must exist
            pass
    finally:
        sys.argv = old
    if sys.platform == 'win32':
        return join(location, 'Scripts', 'python.exe')
    else:
        return join(location, 'bin', 'python')

@savewd
def deploy_release(path=None, target=None, archiving='full'):
    """deploy a release in-place"""
    buildout_args = '-v'
    force_upgrade = False
    if path is None:
        usage = '%prog [options] [http://to/your/buildout/]config.cfg]'
        parser = OptionParser(usage=usage)
        parser.add_option("-v", "--verbose", dest="verbose",
                          help="increase verbosity",
                          default=False, action="store_true")
        parser.add_option("-D", "--debug", dest="debug",
                          help="enable debug mode",
                          default=False, action="store_true")
        parser.add_option("-U", "--upgrade", dest="upgrade",
                          help="Force the setuptools/zc.buildout upgrade",
                          default=False, action="store_true")
        options, args = parser.parse_args()
        if len(args) != 1:
            parser.parse_args(['-h'])
        path = args[0]
        if options.verbose:
            buildout_args += 'vv'
        if options.debug:
            buildout_args += ' -D'
        if options.upgrade:
            force_upgrade = True

    if os.path.isfile(path):
        path = os.path.abspath(path)
        target, filename = os.path.split(path)
        display("Using local configuration file %s" % filename)
        release_name = filename.split('.')[0]
    else:
        location, filename = parse_url(path)
        folder = location.split('/')[-1]
        display("Using network file %s with url %s" % (filename, location))
        release_name = '%s-%s' % (folder, filename.split('.')[0])

    if not target:
        target = release_name

    if os.path.isdir(path):
        root = path
    else:
        root = os.path.realpath(target)

    if not os.path.isdir(root):
        os.makedirs(root)
    os.chdir(root)

    # XXX at this time we are rebuilding everything
    # a pre-built release will have these subdirectories
    # included to avoid compiling again
    exclude = [join(root, subfolder) for subfolder in
               ['parts', 'var', 'develop-eggs', 'bin', 'lib',
                'Lib', 'Scripts', join('downloads', 'dist')]]

    # changes all paths
    if not os.path.isfile(path) and not os.path.isdir(path):
        # let's get the buildout
        if is_svn.search(path) is None:
            raise base.ReleaseError('%s is not a svn url' % path)
        output = base.system('svn co %s .' % location)
        display(output)

    if not os.path.isfile(filename):
        dirname = os.path.dirname(os.path.abspath(filename))
        raise base.ReleaseError('%r not found in %r %r (%s)' % (
            filename, os.getcwd(), root, ', '.join(os.listdir(root))))

    display('Using local directory %s with %s' % (target, filename))

    # let's generate a virtualenv python
    # to make sure we don't loose eggs
    _make_python()

    # create the libs folder if needed
    if sys.platform == 'win32':
        _set_dynlibs(root)

    # now we can run bootstrap.py
    python = _python()

    display(base.system('%s bootstrap.py -c %s' % (python, filename)))

    # Force the setuptools / zc.buildout upgrade if requested
    if force_upgrade:
        display(base.system('%s -U setuptools' % _easy_install()))
        display(base.system('%s -U zc.buildout' % _easy_install()))

    # Run bin/buildout -v
    binary = join('bin', 'buildout')
    buildout = 'buildout.cfg'

    # XXX need to parse extended as well
    # see if download-cache was present
    #try:
    #    cache = get_option(filename, 'buildout', 'download-cache')
    #except ConfigParser.NoOptionError:
    #    raise base.ReleaseError(("You need to add 'download-cache = downloads'"
    #                             "' in the [buildout] section"))

    display('Checking binary.')
    buildout_cmd = '%s %s -c %s' % (binary, buildout_args, filename)

    display('Calling %s' % buildout_cmd)

    try:
        exit_code, output, errors = runwait(buildout_cmd)
        if exit_code != 0:
            display(errors)
            raise
        else:
            sys.stdout.write(output)
            sys.stdout.flush()
    except:
        # second chance (re-runned buildouts)
        exit_code, output, errors = runwait(buildout_cmd)
        if exit_code != 0:
            display(errors)
            raise base.ReleaseError('Error while running %r. Fix your buildout.' % (buildout_cmd,))
        else:
            sys.stdout.write(output)
            sys.stdout.flush()

    display('%s ok.' % binary)

    # archiving process: changes buildout.cfg and create a tarball
    old_content = open(filename).read()
    try:
        if filename != 'buildout.cfg':
            set_option(buildout, 'buildout', 'extends', filename)
        set_option(buildout, 'buildout', 'install-from-cache', 'true')
        set_option(buildout, 'buildout', 'offline', 'true')
        # let's generate the MD5 stamp that will go in the archive
        display('Generating MD5...')
        fd = open(join(root, 'MD5'), 'w')
        try:
            fd.write(build_md5(root))
        finally:
            fd.close()

        # archiving:
        #  - a full archive
        #  - an diffed archived
        display('Archiving %s.' % target)
        if archiving == 'none':
            return
        version_txt = join(root, 'version.txt')
        if os.path.exists(version_txt):
            version = open(version_txt).read().strip()
            archive_name = 'release-%s-%s.tgz' % (version, release_name)
        else:
            archive_name = 'release-%s.tgz' % release_name
        archive_contents(archive_name, '.', exclude)
        display('%s ok.' % archive_name)
    finally:
        # setting back the original buildout.cfg file
        fd = open(filename, 'w')
        fd.write(old_content)
        fd.close()
        # removing MD5
        os.remove(join(root, 'MD5'))

def copy_archives(from_, tarball, filter_eggs=['*'], clean=True):
    """Will copy downloads and eggs folders
    from a buildout to another.

    This will speed up creation time.
    """
    if from_ is None and tarball is None:
        display("Need both source and dest")
        sys.exit(-1)

    to = mkdtemp(prefix='releaser')

    buildout = Buildout(from_, [])

    buildout_directory = buildout['buildout']['directory']

    for filename in glob(join(buildout_directory, '*.cfg')) + [join(buildout_directory, 'version.txt')]:
        if os.path.isfile(filename):
            shutil.copyfile(filename, filename.replace(buildout_directory, to))
        else:
            display('Warning: %s dos not exist' % filename)

    downloads = buildout['buildout']['download-cache']
    downloads_target = join(to, 'downloads')
    eggs = buildout['buildout']['eggs-directory']
    eggs_target = join(to, 'eggs')

    egg_version = 'py' + '.'.join([str(v) for v in sys.version_info[:2]])

    matches = set()

    def match(path):
        if '*' in filter_eggs:
            return True
        # check egg name. need (filter)-py(python-version)
        egg_name = [p for p in path.split(os.sep) if p.endswith('.egg')]
        if egg_name:
            egg_name = egg_name[0]
            for pattern in filter_eggs:
                if fnmatch(egg_name, pattern) and egg_version in egg_name:
                    if egg_name not in matches:
                        matches.add(egg_name)
                    return True
        # check egg name. need (filter)-(gz|tar|zip)
        if path.endswith('gz') or path.endswith('.zip') or path.endswith('tar'):
            egg_name = os.path.basename(path)
            for pattern in filter_eggs:
                if fnmatch(egg_name, pattern):
                    if egg_name not in matches:
                        matches.add(egg_name)
                    return True
        return False

    for source, target in ((downloads, downloads_target),
                           (eggs, eggs_target)):
        if not os.path.exists(source):
            continue
        if os.path.exists(target):
            root_name = name = '%s_old' % target
            i = 0
            while os.path.exists(name):
                name = '%s-%d' % (name, i)
                i += 1
            shutil.move(target, name)

        display('Copying %s to %s' % (source, target))
        os.mkdir(target)

        for root, dirs, filenames in os.walk(source):
            root_target = root.replace(source, target)
            if '.svn' in root:
                continue
            for filename in filenames:
                filename_source = join(root, filename)
                filename_target = join(root_target, filename)
                if os.path.exists(filename_target):
                    continue
                if match(filename_source):
                    dirname = os.path.dirname(filename_target)
                    if not os.path.isdir(dirname):
                        os.makedirs(dirname)
                    shutil.copyfile(filename_source, filename_target)

    buildout = join(to, 'buildout.cfg')
    if from_ != 'buildout.cfg':
        set_option(buildout, 'buildout', 'extends', from_)
    set_option(buildout, 'buildout', 'install-from-cache', 'true')
    set_option(buildout, 'buildout', 'offline', 'true')
    set_option(buildout, 'buildout', 'newest', 'false')

    archive_contents(tarball, to)
    if clean:
        shutil.rmtree(to)
        return matches
    else:
        return to

def console_build_md5(folder=None):
    display(build_md5(folder))

def build_md5(folder=None):
    """generate an MD5 stamp, by recursively reading
    the files (just .py, .txt, .cfg, .pt, .zpt,)"""
    exts = ('.py', '.txt', '.cfg', '.pt', '.zpt', '.html', 'htm')
    if folder is None:
        if len(sys.argv) > 1:
            folder = sys.argv[1]
        else:
            sys.exit(1)
    files = {}
    for root, dirs, filenames in os.walk(folder):
        for filename in filenames:
            if os.path.splitext(filename)[-1] not in exts:
                continue
            file_ = join(root, filename)
            content = open(file_).read()
            files[file_] = md5.md5(content).hexdigest()
    files = files.items()
    files.sort()
    general_md5 = ''.join([key for file, key in files])
    return md5.md5(general_md5).hexdigest()

if sys.platform == 'win32':
    def _safe_arg(arg):
        return '"%s"' % arg
else:
    _safe_arg = str

_easy_install_cmd = _safe_arg(
    'from setuptools.command.easy_install import main; main()'
    )

def console_project_eggs(args=None):
    """for console calls"""
    usage = '%prog [options] [archive_name]'
    parser = OptionParser(usage=usage)
    parser.add_option("-c", "--config", dest="cfg",
                      help="Config file. Default: buildout.cfg",
                      default="buildout.cfg", metavar="CFG")
    parser.add_option("--force", dest="force",
                      help="Force to build archive without checking. Use it at your own risk !",
                      default=False, action="store_true")
    parser.add_option("--copy", dest="copy",
                      help="Only copy eggs from the existing eggs-directory",
                      default=False, action="store_true")
    parser.add_option("-e", "--egg", dest="filter_eggs",
                      help="Eggs name or pattern. more than one is allowed",
                      default=[], action='append',
                      metavar='EGG_FILTER')
    options, args = parser.parse_args(args or sys.argv)

    if not options.cfg or not os.path.isfile(options.cfg):
        parser.parse_args(['-h'])
    else:
        cfg = options.cfg

    filter_eggs = options.filter_eggs

    if len(args) != 2:
        name = os.path.splitext(cfg)[0]
        if os.path.isfile('version.txt'):
            version = open('version.txt').read().strip()
            tarball = '%s-%s-eggs.tar.gz' % (name, version)
        else:
            tarball = '%s-eggs.tar.gz' % name
    else:
        tarball = args[1]

    buildout = Buildout(cfg, [])

    if not options.force:
        if not os.path.isfile('version.txt'):
            parser.error('Seems you try to run this command from a non released buildout. version.txt not found')

        if  buildout['buildout'].get('develop'):
            parser.error("You can't use this command with a develop option")

    display('Generating %s...' % tarball)
    display('Scanning for %s...' % ', '.join(filter_eggs))
    if options.copy:
        eggs = copy_archives(cfg, tarball, filter_eggs, clean=True)
    else:
        eggs = project_eggs(cfg, tarball, filter_eggs)

    display('\n\nEggs collected:')
    display('\n'.join(['    - %s' % egg for egg in eggs]))

class EggInstaller(Installer):

    def __init__(self, eggs_directory, links,
                 index, versions, filter_eggs=None, get_dependencies=False):
        Installer.__init__(self, dest=eggs_directory, links=links,
                           index=index, versions=versions)
        self.get_dependencies = get_dependencies
        if filter_eggs is None:
            filter_eggs = []
        self.filter_eggs = filter_eggs
        self.tarballs = []

    def _get_dist(self, requirement, ws, always_unzip):
        dists = Installer._get_dist(self, requirement, ws, always_unzip)
        for dist in dists:
            location = dist.location
            project_name = dist.project_name
            # not getting dependencies
            if self.get_dependencies:
                self.tarballs.append(location)
            else:
                for pattern in self.filter_eggs:
                    if fnmatch(project_name, pattern):
                        if location not in self.tarballs:
                            self.tarballs.append(location)
        return dists

@savewd
def project_eggs(cfg, tarball=None, filter_eggs=None, verbose=False):
    """Scans for all eggs used by a buildout in eggs, and return their names.

    If install_folder is given, the eggs scanned are fetched and installed
    with their dependencies there.

    If ignore is given, it is a list of glob-like values
    the egg names are tested against them and if they match
    they are excluded from installation.
    """
    def _install(egg):
        if filter_eggs is None:
            return True

        for pattern in filter_eggs:
            if fnmatch(egg, pattern):
                return True
        return False

    buildout_dir, buildout_file = os.path.split(cfg)
    if buildout_dir == '':
        buildout_dir = os.path.realpath(os.curdir)

    os.chdir(buildout_dir)

    def _(lines):
        return [l.strip()
                for l in lines.split('\n') if l.strip() != '']

    tmp = mkdtemp()
    display_step('Working in %s' % tmp, verbose)

    eggs_directory = join(tmp, 'eggs')
    os.mkdir(eggs_directory)

    install_folder = tmp
    if tarball is None:
        tarball = cfg.split('.')[0]

    downloads_directory = join(tmp, 'downloads')
    os.mkdir(downloads_directory)
    develop_eggs_directory = join(tmp, 'develop-eggs')
    os.mkdir(develop_eggs_directory)

    # forcing a few values
    config = ConfigParser.ConfigParser()
    config.read([cfg])

    old_buildout_values = {}
    for name, value in (('eggs-directory', eggs_directory),
                        ('develop-eggs-directory', develop_eggs_directory),
                        ('download-cache', downloads_directory)):
        if config.has_option('buildout', name):
            old_buildout_values[name] = config.get('buildout', name)
        else:
            old_buildout_values[name] = None
        config.set('buildout', name, value)

    cfg_file = join(tmp, buildout_file)
    fd = open(cfg_file, 'w')
    config.write(fd)
    fd.close()

    # copying dependencies
    def _copy_extends(config, buildout_dir, tmp):
        if not 'buildout' in config.sections():
            return
        if not 'extends' in config.options('buildout'):
            return
        extends = chain(*[el.split() for el in _(config.get('buildout', 'extends'))])
        for extend in extends:
            shutil.copyfile(join(buildout_dir, extend), join(tmp, extend))
            subconfig = ConfigParser.ConfigParser()
            subconfig.read([join(buildout_dir, extend)])
            _copy_extends(subconfig, buildout_dir, tmp)

    _copy_extends(config, buildout_dir, tmp)

    buildout = Buildout(cfg_file, [], user_defaults=False)
    buildout._load_extensions()

    # let's get the find-links
    if 'find-links' in buildout['buildout']:
        find_links = _(buildout['buildout']['find-links'])
    else:
        find_links = []

    if 'index' in buildout['buildout']:
        index = buildout['buildout']['index']
    else:
        index = None

    # let's catch the versions
    versions = {}
    if 'versions' in  buildout['buildout']:
        versions = buildout['buildout']['versions']
        if 'versions' in buildout:
            versions = buildout['versions']

    # let's collect the used eggs
    _eggs = []
    sections = buildout.keys()
    for section in sections:
        if section == 'versions':
            continue
        if 'eggs' in buildout[section]:
            _eggs.extend(_(buildout[section]['eggs']))
        if 'recipe' in buildout[section]:
            _eggs.append(buildout[section]['recipe'].strip())


    eggs = []
    for egg in _eggs:
        egg.strip()
        if egg not in eggs:
            eggs.append(egg)

    # installing the eggs
    display_step('Installing eggs in %s.' % install_folder, verbose)
    installer = EggInstaller(eggs_directory, links=find_links,
                             index=index, versions=versions,
                             filter_eggs=filter_eggs)

    target = join(install_folder, 'eggs')
    if not os.path.exists(target):
        os.mkdir(target)

    for egg in eggs:
        if not _install(egg):
            continue
        try:
            display_step('Installing %s' % egg, verbose)
            installer.install((egg,))
        except (MissingDistribution, DistutilsError):
            display_step('Could not install %s' % egg, verbose)

    def _check(egg):
        egg = egg.strip()
        if '==' in egg:
            egg, version = egg.split('==')
            if not _install(egg.strip()):
                return None, egg
            return '%s (%s)' % (egg.strip(), version.strip()), egg
        if not _install(egg):
            return None, egg
        if egg in versions:
            return '%s (%s)' % (egg, versions[egg]), egg
        return egg, egg

    # copying the final selection
    def _remove(element):
        if os.path.isdir(element):
            shutil.rmtree(element, ignore_errors=True)
        else:
            os.remove(element)

    def _copy(element, target):
        if os.path.exists(target):
            return
        if os.path.isdir(element):
            shutil.copytree(element, target)
        else:
            shutil.copyfile(element, target)

    if target != eggs_directory:
        for egg in os.listdir(eggs_directory):
            if egg == 'eggs':
                continue
            eggname = egg.split('-')[0]
            if not _install(eggname):
                _remove(join(eggs_directory, egg))
                continue
            if os.path.exists(join(target, egg)):
                continue
            _copy(join(eggs_directory, egg), join(target, egg))
            _remove(join(eggs_directory, egg))
    else:
        for egg in os.listdir(eggs_directory):
            eggname = egg.split('-')[0]
            if not _install(eggname):
                _remove(join(eggs_directory, egg))

    # let's keep the dists
    for el in os.listdir(downloads_directory):
        if el == 'dist':
            continue
        _remove(join(downloads_directory, el))

    dist_directory = os.path.join(downloads_directory, 'dist')
    for tarball_file in os.listdir(dist_directory):

        if tarball_file not in installer.tarballs:
            _remove(join(dist_directory, tarball_file))

    # we have now a nice downloads_directory
    _copy(downloads_directory, join(install_folder, 'downloads'))

    # let's copy the .cfg files as well
    display_step('Copying all cfg files', verbose)
    for file_ in os.listdir(buildout_dir):
        if not os.path.splitext(file_)[-1] in ('.txt', '.cfg'):
            continue
        if file_ == os.path.split(cfg)[-1]:
            # we need to restore old values from the [buildout]
            # section
            config = ConfigParser.ConfigParser()
            config.read([file_])
            for key, value in old_buildout_values.items():
                if value is None and config.has_option('buildout', key):
                    config.remove_option('buildout', key)
                if value is not None:
                    config.set('buildout', key, value)
            fd = open(file_, 'w')
            config.write(fd)
            fd.close()

        to_ = join(install_folder, file_)
        if os.path.exists(to_):
            os.remove(to_)
        shutil.copyfile(join(buildout_dir, file_), to_)

    # archiving
    display_step('Archiving to %s' % tarball, verbose)
    exclude = ['downloads', 'develop-eggs']
    archive_contents(tarball, install_folder, exclude=exclude)
    installed = ['%s (%s)' % (egg.split('-')[0], egg.split('-')[1])
                 for egg in os.listdir(target)]
    _remove(tmp)
    return installed

def console_make_svn_structure_for_package(package_directory=None):
    """does 3 things:
    1. restructure a new created package in trunk, tags and branches
    2. svn add it to the current working copy if so
    3. svn ci it to the remote svn server as initial import
    """
    if package_directory is None:
        if len(sys.argv) != 2:
            display('Usage: %s package_directory' % sys.argv[0])
            sys.exit(1)
        package_directory = sys.argv[1]

    if not os.path.exists(package_directory):
        base.ReleaseError('%s does not exists' % package_directory)

    tmp_name = "%s_%s" % (package_directory, md5.md5(package_directory).hexdigest())

    shutil.move(package_directory, tmp_name)

    #make the svn structure
    display("creating %s/tags" % package_directory)
    os.makedirs("%s/tags" % package_directory)

    display("creating %s/branches" % package_directory)
    os.mkdir("%s/branches" % package_directory)

    display("creating %s/trunk" % package_directory)
    shutil.move(tmp_name, "%s/trunk" % package_directory)

    #svn add and ci it, if the parent directory is a working copy
    if base.has_svn_support():
        try:
            base.svn_add(package_directory)
            base.svn_commit('initial import of %s' % package_directory)
            display("added %s to svn" % package_directory)
        except:
            display("Current directory is not a working copy. Skip adding %s to svn" % package_directory)

    display('Done...')

def run_setup_release(args):
    # run setup release at version

    # this is ugly but multiprocessing seems to fail with the first Popen
    try:
        runwait('echo')
    except:
        pass

    setup, ver = args
    env = os.environ.copy()
    env['PYTHONPATH'] = os.pathsep.join(sys.path)

    dirname = os.path.dirname(setup)
    os.chdir(dirname)
    name = packet.get_name()
    current_version = packet.get_version()
    if ver != current_version:
        command = '%s setup.py release -a --version=%s' % (sys.executable, ver)
        exit_code, output, errors = runwait(command, env)
    else:
        exit_code = 0
        output = '%s is already at version %s. skipping' % (name, ver)
        errors = ''
    return name, ver, setup, exit_code, output, errors

@savewd
def release_eggs(version=None, filter_eggs=[], prod_cfg='prod.cfg', dev_cfg='dev.cfg',
                 interactive=True, verbose=False):
    """release all eggs to a specific version
    """
    root = os.getcwd()

    released = {}
    release_eggs = []

    if version is None:
        # try to get a default version from the buildout version
        if os.path.isfile('version.txt'):
            default_version = open('version.txt').read().strip()
        else:
            default_version = None
        parser = OptionParser()
        parser.add_option("-v", "--version", dest="version",
                          help="Version",
                          default=default_version)
        parser.add_option("-e", "--egg", dest="filter_eggs",
                          help="Eggs name or pattern. more than one is allowed",
                          default=[], action='append',
                          metavar='EGG_FILTER')
        parser.add_option("--verbose", dest="verbose",
                          help="More print",
                          action='store_true', default=verbose)
        options, args = parser.parse_args()
        version = options.version
        verbose = options.verbose
        if not version:
            parser.error('Version is required')
        filter_eggs = options.filter_eggs
    else:
        default_version = version

    if os.path.isfile(dev_cfg) and os.path.isfile(prod_cfg):
        # we are in a buildout project
        buildout_dev = Buildout(dev_cfg, [])
        buildout_prod = Buildout(prod_cfg, [])

        fixed_versions = buildout_prod['versions']
        versions = {}

        develop_eggs = buildout_dev['buildout'].get('develop')
        develop_eggs = [e.strip() for e in develop_eggs.split('\n')]
        develop_eggs = [e for e in develop_eggs if e]
        for develop in sorted(develop_eggs):
            develop = os.path.abspath(develop)
            if os.path.isfile(join(develop, 'setup.py')):
                package = os.path.basename(develop)
                ver = fixed_versions.get(package, default_version)
                versions[develop] = ver

        for dirname, ver in sorted(versions.items()):
            display('- %s=%s' % (os.path.basename(dirname), ver))

        if interactive:
            reply = raw_input('Is your %s up to date ? [y/N] ' % prod_cfg)
        else:
            display('Is your %s up to date ? [Y/n] ' % prod_cfg)
            reply = 'y'
        if reply.lower() == 'y':
            for dirname, ver in versions.items():
                setup = join(dirname, 'setup.py')
                if os.path.isfile(setup):
                    release_eggs.append([setup, ver])
                else:
                    raise base.ReleaseError('No such file %s' % setup)

    elif filter_eggs:
        # we are in a develop directory
        for pattern in filter_eggs:
            for setup in glob(join(root, pattern, 'setup.py')):
                release_eggs.append([setup, version])

    if os.environ.get('DEBUG', 'false') == True:
        results = [run_setup_release((setup, ver)) for setup, ver in release_eggs]
    else:
        pool = Pool(3)
        results = pool.map(run_setup_release, release_eggs)


    for result in results:
        name, ver, setup, exit_code, output, errors = result
        if exit_code != 0:
            display(errors)
            raise base.ReleaseError('Your release fail')
        else:
            display_step(output, verbose)
            released[name] = ver

    return released
