import ConfigParser
import collections
import datetime
import json
import optparse
import os
import re
import subprocess
import sys
import tarfile
import tempfile

import describepython


CmdOutput = collections.namedtuple('CmdOutput', 'stdout stderr')

def clone_config(config):
    newconfig = ConfigParser.RawConfigParser()
    for section in config.sections():
        newconfig.add_section(section)
        for opt in config.options(section):
            newconfig.set(section, opt, config.get(section, opt))
    return newconfig

def find_python_execs():
    '''Look at the OS path and find anything that looks like
    a python executable.
    '''

    python_execs = []
    exec_re = re.compile('^python[0-9.]*$')
    for x in os.environ['PATH'].split(os.pathsep):
        for f in os.listdir(x):
            if exec_re.search(f) is not None:
                full = os.path.join(x, f)
                if full not in python_execs:
                    python_execs.append(full)
    return tuple(python_execs)

def indent(s, spaces=2):
    res = []
    for x in s.split('\n'):
        res.append(' '*spaces+x)
    return '\n'.join(res)

def chdir(path):
    print '=== Changing directory: %s' % path
    os.chdir(path)

def run(s, capture=False):
    if isinstance(s, basestring):
        cmd = s.split(' ')
    else:
        cmd = list(s)

    if capture:
        stdout = tempfile.NamedTemporaryFile()
        stderr = tempfile.NamedTemporaryFile()
        print '=== Running: %s' % cmd
        ret = subprocess.call(cmd, stdout=stdout, stderr=stderr)
        stdout.seek(0)
        stderr.seek(0)
        data = CmdOutput(stdout.read(), stderr.read())
        stdout.close()
        stderr.close()

        if ret > 0:
            print
            print 'Received error'
            print
            print '== stdout =='
            print data.stdout
            print '== stderr =='
            print data.stderr
            raise OSError('Error while running command')
        return data
    else:
        print '=== Running: %s' % cmd
        if subprocess.call(cmd) > 0:
            print 'Received error'
            raise OSError('Error while running command')

OSInfo = collections.namedtuple('OSInfo', ('sysname nodename release version machine '
                                           'distrib_id distrib_release distrib_codename '
                                           'distrib_description'))

def get_osinfo():
    full = list(os.uname())
    s = run('cat /etc/lsb-release', True).stdout.strip()
    distrib = {}
    for x in s.split('\n'):
        k, v = x.split('=', 1)
        distrib[k] = v
    full += [distrib['DISTRIB_ID'],
             distrib['DISTRIB_RELEASE'],
             distrib['DISTRIB_CODENAME'],
             distrib['DISTRIB_DESCRIPTION']]

    return OSInfo(*full)


class VirtualEnv(object):

    def __init__(self, path):
        self.path = path

    @classmethod
    def create_temp(cls, virtualenvpath, python_exec):
        tempdir = tempfile.mkdtemp('-tmp', 'scripts-')
        return cls.create(virtualenvpath, python_exec, tempdir+'/ve')

    @classmethod
    def create(cls, virtualenvpath, python_exec, path):
        ve = cls(path)
        if virtualenvpath is None:
            raise OSError('Please declare path to virtualenv.py in ~/.distchecker')
        run('%s %s --no-site-packages %s' % (python_exec, virtualenvpath, ve.path))
        return ve

    @property
    def python_exec(self):
        return self.path + '/bin/python'

    def python(self, cmd, *args, **kwargs):
        return run(self.python_exec+' '+cmd, *args, **kwargs)

    def pip(self, cmd, *args, **kwargs):
        extra = 'file://'+os.path.join(os.environ['HOME'], '.distchecker-extras')
        return run(self.path+'/bin/pip ' + cmd + ' -f '+extra, *args, **kwargs)
    

    def run(self, cmd, *args, **kwargs):
        return run(self.path+'/bin/'+cmd, *args, **kwargs)

    def get_eggs(self):
        return self.pip('freeze', True).stdout.strip()

    def get_info(self):
        pe = describepython.PythonEnvironment(self.python_exec)
        pe.prefetch()
        s = ''
        for k in pe._fields:
            v = getattr(pe, k)
            s += '%s: %s\n' % (k, v)

        return s

class Dist(object):
    DEFAULT_PYTHON_EXEC = None

    def __init__(self, path, python_exec):
        self.path = path
        self.python_exec = python_exec

    def _setuppy(self, cmd):
        cwd = os.getcwd()
        chdir(self.path)
        res = run(self.python_exec + ' setup.py ' + cmd, True).stdout.strip()
        chdir(cwd)
        return res

    @property
    def name(self):
        if not hasattr(self, '_name'):
            self._name = self._setuppy('--name')
        return self._name

    @property
    def version(self):
        if not hasattr(self, '_version'):
            self._version = self._setuppy('--version')
        return self._version

    def create_sdist(self):
        self._setuppy('sdist --formats=gztar')
        return '%s/dist/%s-%s.tar.gz' % (self.path, self.name, self.version)

    @property
    def packages(self):
        if not hasattr(self, '_packages'):
            cwd = os.getcwd()
            chdir(self.path)
            location = '.'
            if os.path.exists('src'):
                location = 'src'
            s = run([self.python_exec, '-c', "from setuptools import find_packages; print find_packages('%s')" % location], capture=True).stdout.strip()
            s = s.replace("'", '"')  # json doesn't like single quotes
            self._packages = json.loads(s)
            chdir(cwd)
        return self._packages

matches = [re.compile('~$'),
           re.compile('.pyc$'),
           re.compile('^[.]'),
           re.compile('^PKG-INFO$'),
           re.compile('^dist/')]

class DistChecker(object):

    actions = {}

    def __init__(self):
        self.config = ConfigParser.RawConfigParser()
        self.homedir = os.environ.get('HOME', '/')
        if os.path.exists(os.path.join(self.homedir, '.distchecker')):
            self.config.read(os.path.join(self.homedir, '.distchecker'))

        if self.config.has_option('pythons', 'default'):
            self.DEFAULT_PYTHON_EXEC = self.python_exec = self.config.get_option('pythons', 'default')
        else:
            execs = find_python_execs()
            if len(execs) == 0:
                raise OSError('Could not find any python executables on the path')
            self.DEFAULT_PYTHON_EXEC = self.python_exec = execs[0]

    def action_test_sdist(self, args):
        ve = VirtualEnv.create_temp(self.config.get('general', 'virtualenv'),
                                    self.python_exec)

        # args[0] should be the path to a project
        chdir(args[0])

        dist = Dist('.', ve.python_exec)

        if len(dist.packages) < 1:
            raise ValueError('packages is empty')

        sdist = dist.create_sdist()

        ve.pip('install %s' % sdist)
        freeze = ve.get_eggs()
        ve.pip('install nose coverage')

        cmd = 'nosetests --with-coverage --cover-inclusive'
        for x in dist.packages:
            cmd += ' --cover-package='+x
        coverage = ve.run(cmd, True).stderr.strip()

        osinfo = get_osinfo()._asdict()
        osinfo_s = ''
        for k, v in osinfo.items():
            osinfo_s += '%s: %s\n' % (k, v)
        describe = ve.get_info()

        print
        print '''; -*-rst-*-
**Date:**  %(now)s

Test Coverage
=============

::
%(coverage)s

Python Info
===========

::
%(describe)s

OS Info
=======

::
%(osinfo)s

Installed Eggs
==============

::
%(freeze)s
''' % {'coverage': indent(coverage),
       'describe': indent(describe),
       'osinfo': indent(str(osinfo_s)),
       'now': datetime.datetime.now(),
       'freeze': indent(freeze)}

        return ve

    actions['test_sdist'] = action_test_sdist

    def action_test_paster_template(self, args):
        ve = self.action_test_sdist([args[0]])
        chdir(ve.path)
        ve.run('paster create -t %s Something' % args[1])
        chdir('Something')
        ve.pip('install -e .')
        ve.python('setup.py test')

    actions['test_paster_template'] = action_test_paster_template

    def action_compare_sdist(self, args):
        local = {}
        path = os.getcwd()
        if len(args) > 0:
            path = args[0]
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                full = os.path.join(dirpath, filename)
                partial = full[len(path)+1:]

                exclude = False
                for r in matches:
                    if r.search(partial) is not None:
                        exclude = True
                        break
                if not exclude:
                    local[partial] = os.path.getsize(full)

        working = dict(local)
        distro = Dist(path, self.python_exec)
        f = distro.create_sdist()
        tarball = tarfile.open(f, 'r:gz')
        bad = []
        for x in tarball:
            if x.isfile():
                partial = x.name[len('%s-%s' % (distro.name, distro.version))+1:]
                exclude = False
                for r in matches:
                    if r.search(partial) is not None:
                        exclude = True
                        break
                if exclude:
                    continue
                sz = working.get(partial, None)
                if sz is None:
                    bad.append(('extra', partial))
                    continue
                del working[partial]
                if sz != x.size:
                    bad.append(('diff', partial))

        for partial, sz in working.items():
            bad.append(('missing', partial))

        tarball.close()

        print f
        for x in bad:
            print '  ' + str(x)

    actions['compare_sdist'] = action_compare_sdist

    def main(self, cmdargs=sys.argv[1:]):
        parser = optparse.OptionParser()
        parser.add_option('', '--setup-config', dest='setup_config',
                          default=False,
                          action='store_true',
                          help='Generate a default configuration for %s/.distchecker' % self.homedir)
        parser.add_option('', '--with-python', dest='with_python',
                          default=self.DEFAULT_PYTHON_EXEC,
                          action='store',
                          help='Which Python interpreter to run command with')
        (options, args) = parser.parse_args(cmdargs)

        self.python_exec = options.with_python

        if options.setup_config:
            newconfig = clone_config(self.config)
            if not newconfig.has_section('general'):
                newconfig.add_section('general')
            if not newconfig.has_section('pythons'):
                newconfig.add_section('pythons')
                execs = find_python_execs()
                for x in execs:
                    newconfig.set('pythons', os.path.basename(x), x)
                if len(execs):
                    raise OSError('Could not find any python executables on the path')
                newconfig.set('pythons', 'default', execs[0])
            if not newconfig.has_option('general', 'pip_download_cache'):
                newconfig.set('general', 'pip_download_cache', os.path.join(self.homedir, '.pip_download_cache'))
            if not newconfig.has_option('general', 'virtualenv'):
                newconfig.set('general', 'virtualenv', '')
            print 'Please save the following in: %s' % os.path.join(self.homedir, '.distchecker')
            print
            newconfig.write(sys.stdout)
            return

        if self.config.has_option('general', 'pip_download_cache'):
            os.environ['PIP_DOWNLOAD_CACHE'] = self.config.get('general', 'pip_download_cache')

        if len(args) > 0 and args[0] in self.actions:
            action = self.actions[args[0]]
            return action(self, args[1:])
        else:
            print
            print 'Commands:'
            print
            for k in self.actions:
                print '  ', k
            print

def main():
    helper = DistChecker()
    helper.main()

if __name__ == '__main__':
    main()
