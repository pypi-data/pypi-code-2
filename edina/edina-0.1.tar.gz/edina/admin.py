from fabric.api import cd, env, local, put, run, settings
from fabric.contrib.files import exists

import os
import sys

# stop and start apache decorator
def apache(f):
    def deco(self, *args):
        self._stop_apache()
        d = f(self, *args)
        self._start_apache()
        return d
    return deco

class Fabric(object):

    def __init__(self, project, target='local', source_path=None, apache_dir=None):
        self.project = project
        self.host = env.host

        self.source_root = local('pwd').strip()
        if source_path:
            self.source_dir = os.sep.join((self.source_root, source_path))
        else:
            self.source_dir = self.source_root

        if self.host:
            # note: use echo $HOME instead of '~'
            # as tilde doesn't work with remote exists
            self.target_dir = os.sep.join((run('echo $HOME'), target))
        else:
            self.target_dir = os.sep.join((os.environ['HOME'], target))

        self.proj_dir = os.sep.join((self.target_dir, project))

        if apache_dir:
            self.apache_dir = apache_dir
        else:
            self.apache_dir =  os.sep.join((self.target_dir, 'www'))

    def install(self, app):
        """
        Install a project from scratch, for DEV, BETA or LIVE

        app - the application to be run (currently only single app supported
              but multiple should be supported)
        """

        if self.host:
            self._install_remote(app)
        else:
            # no host defined, install locally
            self._install_local(app)

    @apache
    def deploy(self, app):
        """
        Deploy an application to BETA. This simpy rsync the application to
        machine.

        app - the application to be run (currently only single app supported
              but multiple should be supported)
        """

        local('rsync -av %s %s@%s:%s ' % (os.sep.join((self.source_dir, app)),
                                          env.user,
                                          self.host,
                                          self.proj_dir))

    def release(self, app, skip_code_check=False):
        """
        Release new version of a single application.
        """

        #str = 'from %s import get_version' % app
        str = 'import %s' % app

        try:
            # get version of app
            # later versions of fab can use 'lcd'
            if self.source_dir not in sys.path:
                sys.path.append(self.source_dir)

            exec str
            version = steev.get_version()
        except ImportError as e:
            print ("\n*** Error: A function named get_version() must be defined in "
                   "%s%c__init__.py" % (app, os.sep))
            print e
            return False

        # check code style
        if not skip_code_check:
            self.code_check(app)

        # run unit tests
        self.run_tests(app)

        link = os.sep.join((self.proj_dir, app))
        app_dir = '%s-%s' % (link, version)
        if exists(app_dir):
            msg = "\n*** Error: A version of the application %s (%s) " \
            "has already been released\n"
            print msg % (app, version)
            return False

        # remove current link if it exists
        if exists(link):
            run('rm %s' % link)

        # create new release
        # note: using scp could use fabric.contrib.project.upload_project
        # in future
        run('mkdir %s' % app_dir)
        local('scp -r %s/* %s:%s' % (
                os.sep.join((self.source_dir, app)),
                env.host_string,
                app_dir))

        with cd(self.proj_dir):
            # create link to latest version
            new_app_dir = '%s-%s' % (app, version)
            run('ln -s %s %s' % (new_app_dir, app))

        # create tag
        msg = "%s release v%d" % (app, version)
        local('git tag -a v%s -m "%s"' % (version, msg))

    def run_tests(self, app):
        """Run tests locally"""
        local('cd %s && python -m unittest %s.tests' % (
                self.source_dir, app), capture=False)

    def code_check(self, app):
        """Run code style checker"""
        source_dir = os.sep.join((self.source_dir, app))
        local('find %s -name "*.py" | xargs pep8 --ignore=E221' % source_dir,
              capture=False)

    def _install_local(self, app):
        self.proj_dir = os.path.expanduser(self.proj_dir)
        if os.path.exists(self.proj_dir):

            # check if they want to delete existing installation
            msg = 'Directory %s exists.\nDo you wish to delete it(y/n)? > '
            msg = msg % self.proj_dir
            answer = raw_input(msg).strip()

            if answer != 'y':
                print 'Choosing not continue. Nothing installed.'
                return

            local('rm -rf %s' % self.proj_dir)

        with cd(self.target_dir):
            # create virtual environment
            local('virtualenv --no-site-packages %s' % self.project)

            # install dependencies
            req_file = os.sep.join((self.source_root,
                                    'etc',
                                    'requirements.txt'))
            if os.path.isfile(req_file):
                self._virtualenv('pip install -r %s' % req_file)
            else:
                print '*** WARN: No dependencies found at %s' % req_file

            with cd(self.project):
                # create link to app
                local('ln -s %s' % os.sep.join((self.source_dir, app)))

    def _install_remote(self, app):
        """
        with settings(warn_only=True):
            output = run('ls %s' % self.proj_dir)
            if output:
                print "There already exists an installation %s on %s" % (
                    self.proj_dir,
                    self.host)
                return
                """

        if exists(self.proj_dir):
            print "There already exists an installation %s on %s" % (
                self.proj_dir,
                self.host)
            return

        with cd(self.target_dir):
            run('virtualenv --no-site-packages %s' % self.project)
            with cd(self.project):
                req_file = os.sep.join((self.source_root,
                                        'etc',
                                        'requirements.txt'))
                if os.path.isfile(req_file):
                    run('mkdir etc')
                    remote_etc_dir = os.sep.join((self.target_dir, self.project, 'etc'))
                    put(req_file, remote_etc_dir)
                    self._venvremote('pip install -r %s' %
                                     os.sep.join((remote_etc_dir,
                                                  'requirements.txt')))
                else:
                    print '*** WARN: No dependencies found at %s' % req_file

    def _virtualenv(self, command):
        # run command using virtual environment
        # and the current runtime directory
        local('. %s/bin/activate && %s' % (self.proj_dir, command))

    def _venvremote(self, command):
        # run command using virtual environment
        run('. %s/bin/activate && %s' % (self.proj_dir, command))

    def _stop_apache(self):
        run('%s/bin/apachectl stop' % self.apache_dir)

    def _start_apache(self):
        run('%s/bin/apachectl start' % self.apache_dir)
