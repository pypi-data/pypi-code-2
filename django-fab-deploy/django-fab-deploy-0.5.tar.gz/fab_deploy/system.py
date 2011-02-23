#coding: utf-8
from __future__ import with_statement
import os.path
from fabric.api import run, settings, env, cd
from fabric.contrib.files import append
from fab_deploy.utils import run_as, detect_os
from fabric.utils import puts, abort

def prepare_server():
    """ Prepares server: installs system packages. """
    setup_backports()
    install_common_software()

@run_as('root')
def install_common_software():
    """ Installs common system packages. """
    common_packages = [
        'python', 'build-essential', 'python-dev', 'python-setuptools',
        'python-profiler', 'libjpeg-dev', 'zlib1g-dev',
        'libssl-dev', 'libcurl3-dev',

        'screen', 'locales-all', 'curl',
        'memcached',
        'subversion',
    ]
    extra_packages = {
        'lenny': ['libmysqlclient15-dev'],
        'squeeze': ['libmysqlclient-dev'],
        'maverick': ['libmysqlclient-dev'],
    }

    os = detect_os()
    if os not in extra_packages:
        abort('Your OS (%s) is unsupported now.' % os)

    aptitude_install(" ".join(common_packages + extra_packages[os]))

    # git and mercurial are outdated in stable Debian Lenny and
    # don't work with some source repositories on github and bitbucket
    vcs_options = {'lenny': '-t lenny-backports'}
    aptitude_install('mercurial git', vcs_options.get(os, ""))
    aptitude_install('bzr', '--without-recommends')

    run('easy_install -U pip')
    run('pip install -U virtualenv')


@run_as('root')
def setup_backports():
    """ Adds backports repo to apt sources. """
    os = detect_os()
    backports = {
        'lenny': 'http://backports.debian.org/debian-backports lenny-backports main contrib non-free',
        'squeeze': 'http://backports.debian.org/debian-backports squeeze-backports main contrib non-free',
    }

    if os not in backports:
        puts("Backports are not available for " + os)
        return

    run("echo 'deb %s' > /etc/apt/sources.list.d/backports.sources.list" % backports[os])
    with settings(warn_only=True):
        run('aptitude update')

@run_as('root')
def create_linux_account(pub_key_file):
    """ Creates linux account and setups ssh access. """
    with open(os.path.normpath(pub_key_file), 'rt') as f:
        ssh_key = f.read()
    username = env.conf['USER']
    with (settings(warn_only=True)):
        run('adduser %s --disabled-password --gecos ""' % username)
        with cd('/home/' + username):
            run('mkdir -p .ssh')
            append('.ssh/authorized_keys', ssh_key)
            run('chown -R %s:%s .ssh' % (username, username))

def ssh_add_key(pub_key_file):
    """ Adds a ssh key from passed file to user's authorized_keys on server. """
    with open(os.path.normpath(pub_key_file), 'rt') as f:
        ssh_key = f.read()
    run('mkdir -p .ssh')
    append('.ssh/authorized_keys', ssh_key)


@run_as('root')
def aptitude_install(packages, options=''):
    """ Installs package via aptitude. """
    run('aptitude install %s -y %s' % (options, packages,))


#@run_as('root')
#def install_backup_system():
#    run('aptitude install -y s3cmd ruby rubygems libxml2-dev libxslt-dev libopenssl-ruby')
#    run('gem install rubygems-update')
#    run('/var/lib/gems/1.8/bin/update_rubygems')
#    run('gem install astrails-safe --source http://gemcutter.org')
