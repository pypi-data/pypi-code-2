#coding: utf-8
from __future__ import with_statement
from fabric.api import run, settings
from fabric.contrib.files import append
from fab_deploy.utils import run_as

@run_as('root')
def install_system_packages():
    with settings(warn_only=True):
        run('aptitude update')

    to_install = [
        'apache2', 'python2.5', 'memcached', 'mutt', 'nginx',
        'libjpeg-dev', 'libmysqlclient15-dev', 'zlib1g-dev',
        'build-essential', 'python-dev', 'python-setuptools',
        'libapache2-mod-wsgi', 'python-profiler', 'libapache2-mod-rpaf',
        'screen', 'locales-all', 'curl',
    ] # + mysql-server

    run('aptitude install -y %s' % " ".join(to_install))
    run('easy_install -U pip')
    run('pip install -U virtualenv')


@run_as('root')
def setup_backports():
    run("echo 'deb http://backports.debian.org/debian-backports lenny-backports main contrib non-free' > /etc/apt/sources.list.d/backports.sources.list")
#    run('wget -O - http://backports.org/debian/archive.key | apt-key add -')
    with settings(warn_only=True):
        run('aptitude update')

@run_as('root')
def install_vcs():
    run("aptitude -t lenny-backports install -y mercurial git-core")
    run("aptitude install -y subversion bzr")


@run_as('root')
def setup_locale():
    append('/etc/apache2/envvars', ['export LANG="en_US.UTF-8"', 'export LC_ALL="en_US.UTF-8"'])
    run('/etc/init.d/apache2 stop')
    run('/etc/init.d/apache2 start')


#@run_as('root')
#def install_backup_system():
#    run('aptitude install -y s3cmd ruby rubygems libxml2-dev libxslt-dev libopenssl-ruby')
#    run('gem install rubygems-update')
#    run('/var/lib/gems/1.8/bin/update_rubygems')
#    run('gem install astrails-safe --source http://gemcutter.org')

#def prepare_backups():
#    run('mkdir -p backups/before-migrate')
#
#    gen_dir = '%s/hosting/backup/generated/' % env.conf['SRC_DIR']
#    tpl_dir = 'hosting/backup/tpl/'
#
#    def gen_template(name):
#        upload_template(tpl_dir+name, gen_dir+name, env.conf, True)
#
#    gen_template('crontab')
#    gen_template('db.rb')
#    gen_template('files.rb')
#    run('crontab -u %s %s' % (env.user, gen_dir+'crontab'))


