#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import glob

from fabric.api import env, local, prompt, put, run, sudo
from fabric.contrib.files import exists
from fabric.context_managers import cd

env.hosts = ['lipus.fubar.si:30000']
env.user = 'www'
env.dist = 'dist/*' # python dist folder for setuptools
env.pylons_config = 'deploy.ini'
env.develop = True
env.docs_dir = 'docs'
env.python = 'python%s' % sys.version[:3]
env.location = '~'


def upload_docs():
    """Generate Sphinx documentation and upload it to server"""
    _check_project_name()
    if env.develop:
        local('python setup.py develop')
    else:
        local('python setup.py install')
    os.chdir(env.docs_dir)
    local('make html')

    env.deploy_location = 'docs/%(project_name)s' % env

    # update to upload_project
    local('rsync -e "ssh -p 30000" --delete -pthrvz  build/html/ www@lipus.fubar.si:%(deploy_location)s' % env)

def make_release():
    """Make a distribution and upload it to PyPi"""
    local('python setup.py egg_info -RDb "" sdist register upload')

def validate_long_description():
    """Generate REST description from setup.py and view it in firefox"""
    # TODO: deprecate with collective.checkdocs
    local('python setup.py --long-description | rst2html.py > 1.html && gnome-open 1.html && sleep 2 && rm 1.html')

def pylons_init():
    """Create basic structure for Pylons application"""
    _check_project_name()

    # create project dir
    if not exists(env.location):
        run('mkdir %s' % env.location)

    # create virtualenv
    #sudo('easy_install -U virtualenv')
    run('virtualenv --no-site-packages -p %(python)s %(location)s' % env)

    # install egg
    _install_pylons_egg()

        # make .ini
        # TODO: interactive mode
    with cd(env.location):
        run('%(project_name)s/bin/paster make-config %(project_name)s %(pylons_config)s --no-interactive' % env)

    print 'After configuration run bin/paster setup-app'
    print 'and after that run supervisor'

def pylons_deploy():
    """Deploy Pylons application with eggs/ini"""
    _check_project_name()

    _install_pylons_egg()

    # TODO: make backup

    # update DB
    run('bin/paster setup-app %(pylons_config)s' % env)

    # restart supervisor
    run('bin/supervisorctl restart %(project_name)s' % env)


def _install_pylons_egg():
    local('%s setup.py sdist' % sys.executable)
    env.egg = glob.glob(env.dist)[0].split('/')[-1]

    # upload egg
    put(env.dist, env.location)

    # make the egg
    with cd(env.location):
        run('bin/pip install %(egg)s' % env)

    # cleanup
    local('rm ' + env.dist)
    #run('rm %(project_name)s/%(egg)s' % env)

def start_collective_project():
    """Create project in collective svn and check it out to current folder"""
    _check_project_name()

    local("svn mkdir https://svn.plone.org/svn/collective/%(project_name)s -m 'Created new project %(project_name)s'" % env)
    local("svn mkdir https://svn.plone.org/svn/collective/%(project_name)s/trunk -m 'Adding base files'" % env)
    local("svn mkdir https://svn.plone.org/svn/collective/%(project_name)s/branches -m 'Adding base files'" % env)
    local("svn mkdir https://svn.plone.org/svn/collective/%(project_name)s/tags -m 'Adding base files'" % env)
    local("svn checkout https://svn.plone.org/svn/collective/%(project_name)s/trunk ." % env)

#utils
def _check_project_name():
    """check if project name is defined or ask for it"""
    if not env.get('project_name', None):
        prompt('What is the name of the project (will be used in pathname)?', 'project_name')
