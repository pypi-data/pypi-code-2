import sys
import os
import datetime
import pkg_resources
import posixpath
import tempfile
import random

import yaml
from fabric.api import *
from fabric.contrib.files import exists, upload_template

import silk.lib

SRV_ROOT = '/srv'
DEFAULT_ROLLBACK_CAP = 3

def _get_silk_deps():
    silk_deps_file = pkg_resources.resource_filename('silk', 'deps.yaml')
    return yaml.safe_load(open(silk_deps_file).read())

def _get_site_deps(local_root):
    site_deps_file = os.path.join(local_root, 'deps.yaml')
    return yaml.safe_load(open(site_deps_file).read())

def _set_vars():
    """
    Loads deployment settings into Fabric's global 'env' dict
    """
    env.local_root = silk.lib.get_site_root(os.getcwd())
    env.config = silk.lib.get_site_config(env.local_root)
    if len(env.roles) == 0:
        sys.exit("ERROR: you must define a role with -R <rolename>")
    elif len(env.roles) > 1:
        sys.exit("ERROR: Silk only permits passing in one role at a time")
    else:
        env.config.update(silk.lib.get_role_config(env.roles[0]))
    env.site = env.config['site']
    env.remote_root = '/'.join([SRV_ROOT, env.site])
    env.envdir = '/'.join([env.remote_root, 'env'])
    env.workdir = '/'.join(['/tmp', env.site])
    env.rollbackdir = '/'.join([SRV_ROOT, 'rollbacks'])
    env.deploytime = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
    env.config['bind'] = env.config['gunicorn'].get('bind', 'unix:/tmp/%s.sock'
                                                    % env.site)
    env.config['silk_deps'] = _get_silk_deps()
    env.config['site_deps'] = _get_site_deps(env.local_root)

_set_vars()

# UGLY MAGIC
# Here we're (ab)using Fabric's built in 'role' feature to work with the way 
# we're loading context-specific config.  Could possibly use a refactor to 
# avoid Fabric roles altogether.
def _get_hosts():
    """Return list of hosts to push to"""
    return env.config['push_hosts']

for role in silk.lib.get_role_list(env.local_root):
    env.roledefs[role] = _get_hosts
# END UGLY MAGIC

def _put_dir(local_dir, remote_dir):
    """
    Copies a local directory to a remote one, using tar and put. Silently
    overwrites remote directory if it exists, creates it if it does not
    exist.
    """
    local_tgz = "/tmp/fabtemp.tgz"
    remote_tgz = os.path.basename(local_dir) + ".tgz"
    local('tar -C "{0}" -czf "{1}" .'.format(local_dir, local_tgz))
    put(local_tgz, remote_tgz)
    local('rm -f "{0}"'.format(local_tgz))
    run('rm -Rf "{0}"; mkdir -p "{0}"; tar -C "{0}" -xzf "{1}" && rm -f "{1}"'\
        .format(remote_dir, remote_tgz))

def _get_blame():
    """
    Returns a yaml file that contains the site config, plus some deployment
    info.  The actual blame.yaml file will be written from this data.
    """
    blame = [
        {'deployed_by': env.user,
        'deployed_from': os.uname()[1],
        'deployed_at': datetime.datetime.now(),
         'deployed_role': env.roles[0]},
        {'config':env.config}
    ]
    return yaml.safe_dump(blame, default_flow_style=False)

def _write_blame():
    """
    Writes blame file on remote host.
    """
    blamefile = tempfile.NamedTemporaryFile()
    blamefile.write(_get_blame())
    blamefile.seek(0) # Rewind the file so that the putter can read it.
    remote_blame = '/'.join([env.workdir, 'blame.yaml'])
    put(blamefile.name, remote_blame)
    blamefile.close()

    # Fix the permissions on the remote blame file
    sudo('chmod +r %s' % remote_blame)

def reload():
    """
    Reloads supervisord and nginx configs.
    """
    print "RELOADING CONFIGS"
    sudo('supervisorctl reload')
    sudo('/etc/init.d/nginx reload')

def restart():
    """
    Restarts nginx and supervisord.  Normally not needed (reload() is enough)
    """
    print "RESTARTING SERVICES"
    sudo('/etc/init.d/supervisor stop; /etc/init.d/supervisor start')
    sudo('/etc/init.d/nginx restart')

def archive():
    """
    Creates rollback archive of already-deployed site.  Rotates old rollback files.
    """
    ROLLBACK_CAP = env.config.get('rollback_cap', DEFAULT_ROLLBACK_CAP)
    if ROLLBACK_CAP > 0:
      print "CREATING ROLLBACK"
      if not exists(env.rollbackdir, use_sudo=True):
          sudo('mkdir -p %s' % env.rollbackdir)

      template_vars = {
          'rollback_cap': ROLLBACK_CAP,
          'srv_root': SRV_ROOT,
      }

      template_vars.update(env)

      oldest_rollback = '%(rollbackdir)s/%(site)s-rollback_%(rollback_cap)s.tar.bz2' % template_vars
      #first delete the oldest rollback if present
      if exists(oldest_rollback):
          sudo('rm %s' % oldest_rollback) 

      #then increment the numbers on the existing rollbacks
      for i in xrange(ROLLBACK_CAP - 1, 0, -1):
          rollback_file = '%s/%s-rollback_%s.tar.bz2' % (env.rollbackdir, env.site, i)
          if exists(rollback_file):
              newname = '%s/%s-rollback_%s.tar.bz2' % (env.rollbackdir, env.site, i + 1)
              sudo('mv %s %s' % (rollback_file, newname))

      #now archive env.remote_root if it exists
      if exists(env.remote_root):
          sudo('tar -cjf %(rollbackdir)s/%(site)s-rollback_1.tar.bz2 --exclude "*.log" -C %(srv_root)s %(site)s' % template_vars)

def rollback():
    """
    Untars most recent rollback archive and sets it running.
    """
    print "ROLLING BACK"
    rollback_file = '%s/%s-rollback_1.tar.bz2' % (env.rollbackdir, env.site)
    if exists(rollback_file): 
        #unzip in a tmp dir
        tmpdir = os.path.join('/tmp', 'rollback-%s' % env.site)
        if exists(tmpdir, use_sudo=True):
            sudo('rm %s -rf' % tmpdir)
        sudo('mkdir %s' % tmpdir)
        sudo('tar -xjf %s -C %s' % (rollback_file, tmpdir))

        #move current code into oldddir
        olddir = os.path.join('/tmp', 'old-%s' % env.site)
        if exists(env.remote_root, use_sudo=True):
            sudo('mv %s %s' % (env.remote_root, olddir))

        #move new code into srvdir
        sudo('mv %s/%s %s' % (tmpdir, env.site, env.remote_root))

        #remove olddir
        if exists(olddir, use_sudo=True):
            sudo('rm %s -rf' % olddir)

        #clean out the rollback file we just unzipped
        sudo('rm -rf %s' % rollback_file)

        #decrement the other rollback files
        for i in xrange(2, ROLLBACK_CAP + 1, 1):
            oldname = '%s/%s-rollback_%s.tar.bz2' % (env.rollbackdir, env.site, i)
            newname = '%s/%s-rollback_%s.tar.bz2' % (env.rollbackdir, env.site, i - 1)
            if exists(oldname):
                sudo('mv %s %s' % (oldname, newname))
        reload()
    else:
        sys.exit('Error: %s not found' % rollback_file)


def install_apt_deps():
    """
    Installs system packages and build dependencies with apt.
    """
    for deps_dict in (env.config['silk_deps'], env.config['site_deps']):
        print deps_dict
        if deps_dict['apt_build_deps']:
            sudo('apt-get build-dep %s -y' % ' '.join(deps_dict['apt_build_deps']))
        if deps_dict['apt_packages']:
            sudo('apt-get install %s -y' % ' '.join(deps_dict['apt_packages']))

#TODO: rebuild virtualenv if it exists but the python version is wrong
def create_virtualenv():
    """
    Creates a virtualenv for the site.  Automatically builds egenix-mx-tools in it, since
    pip doesn't seem able to install that.
    """
    print "CREATING VIRTUALENV"
    if not exists(env.remote_root, use_sudo=True):
        sudo('mkdir -p %s' % env.remote_root)
    sudo('virtualenv --no-site-packages --python=%s %s' % (env.config['runtime'], env.envdir))
    build_mx_tools()

def _pip_install_deps(dep_list):
    # Write it out
    file_contents = '\n'.join(dep_list)
    tmpfile = tempfile.NamedTemporaryFile()
    tmpfile.write(file_contents)
    tmpfile.seek(0) # Rewind the file so that the putter can read it.

    # Upload it to the remote host
    tmp_remote = '/tmp/%s-reqs.txt' % ''.join([random.choice('abcdefghijklmnopqrstuvwxyz') for x in xrange(5)])
    put(tmpfile.name, tmp_remote)

    # Closing a tempfile will clean it up automatically.
    tmpfile.close()

    # Run pip install remotely
    pip_cmd = silk.lib.get_pip_cmd(env.config) 
    sudo('%s/bin/%s -r %s' % (env.envdir, pip_cmd, tmp_remote))
         
    # Clean up remote reqs file
    sudo('rm %s' % tmp_remote)

def install_python_deps():
    """
    Runs pip install inside the remote virtualenv.  First for silk's dependencies and
    then for the site's.
    """
    for dep_dict in (env.config['silk_deps'], env.config['site_deps']):
        if dep_dict['python_packages']:
            _pip_install_deps(dep_dict['python_packages'])

def install_deps():
    """
    Wraps the apt deps, virtualenv creation, and python deps functions to ensure
    that things are done in the right order.
    """
    print "INSTALLING DEPENDENCIES"
    install_apt_deps()
    if not exists(env.envdir, use_sudo=True):
        create_virtualenv()
    install_python_deps()

def build_mx_tools():
    """
    Builds and install egenix-mx-tools into virtualenv
    """
    #egenix-mx-tools includes the mxdatetime module, which is
    #a psycopg2 dependency.  Unfortunately it's not packaged in 
    #a way that pip can install.  So we build it here instead
    print "INSTALLING MX TOOLS"
    build_dir = "/tmp/egenix_build"
    if not exists(build_dir, use_sudo=True):
        sudo('mkdir -p %s' % build_dir)
    with cd(build_dir):
        #download the tools
        sudo('wget http://downloads.egenix.com/python/egenix-mx-base-3.1.3.tar.gz')
        #unpack
        sudo('tar xvf egenix-mx-base-3.1.3.tar.gz')
    with cd(os.path.join(build_dir, 'egenix-mx-base-3.1.3')):
        #install into the virtualenv
        sudo('%s setup.py install' % os.path.join(env.envdir, 'bin', 'python'))
    sudo('rm -rf %s' % build_dir)

def push_code():    
    """
    Pushes site to remote host
    """
    print "PUSHING CODE TO HOST"
    if exists(env.workdir):
        sudo('rm %s -rf' % env.workdir)
    _put_dir(env.local_root, env.workdir)

def _upload_config_template(template, dest, context):
    #first try to load the template from the local cfg_templates dir.
    #if it's not there then try loading from pkg_resources
    path = silk.lib.get_template_path(template)
    upload_template(path, dest, context=context, use_sudo=True)

def _get_nginx_static_snippet(url_path, local_path):
    return """
    location %(url_path)s {
        alias %(local_path)s;
    }
    """ % locals()

def _write_templates(template_list, template_vars):
    for pair in template_list:
        src, dest = pair
        _upload_config_template(
            src,
            dest,
            context = template_vars
        )

def _ensure_dir(remote_path):
    if not exists(remote_path, use_sudo=True):
        sudo('mkdir %s' % remote_path)

def _format_supervisord_env(env_dict):
    """Takes a dictionary and returns a string in form
    'key=val,key2=val2'"""
    try:
      return ','.join(['%s="%s"' % (key, env_dict[key]) for key in env_dict.keys()])
    except AttributeError:
      #env_dict isn't a dictionary, so they must not have included any env vars for us.
      #return empty string
      return ''

def write_config():
    """
    Creates and upload config files for nginx, supervisord, and blame.yaml
    """
    print "WRITING CONFIG"
    nginx_static = ''
    static_dirs = env.config.get('static_dirs', None)
    if static_dirs:
      for item in static_dirs:
          nginx_static += _get_nginx_static_snippet(
              item['url_path'],
              #system_path may be a full path, or relative to remote_root
              posixpath.join(env.remote_root, item['system_path'])
          )
    template_vars = {
        'cmd': silk.lib.get_gunicorn_cmd(env.config, bin_dir='%s/bin' % (env.envdir)),
        'nginx_static': nginx_static,
        'nginx_hosts': ' '.join(env.config['listen_hosts']),
        'process_env': _format_supervisord_env(env.config['env']),
        'srv_root': SRV_ROOT,
    }
    template_vars.update(env)
    template_vars.update(env.config)
    config_dir = '/'.join([env.workdir, 'conf'])
    #make sure the conf and logs dirs are created
    _ensure_dir(config_dir)
    _ensure_dir('/'.join([env.workdir, 'logs']))

    template_list = (
        ('supervisord.conf','/'.join([config_dir, 'supervisord.conf'])),
        ('nginx.conf','/'.join([config_dir, 'nginx.conf'])),
    )
    _write_templates(template_list, template_vars)
    _write_blame()

def switch():
    """
    Does a little dance to move the old project dir out of the way and put
    the new one in its place.
    """
    print "MOVING NEW CODE INTO PLACE"
    #copy the virtualenv into env.workdir
    sudo('cp %s %s/ -r' % (env.envdir, env.workdir))
    #move old env.remote_root
    olddir = '/'.join(['/tmp', 'old-%s' % env.site])
    sudo('mv %s %s' % (env.remote_root, olddir))
    #move code into place
    sudo('mv %s %s' % (env.workdir, env.remote_root))

def cleanup():
    """
    Removes the old project dir.  (But you still have a rollback!)
    """
    print "CLEANING UP"
    #do this last to minimize time between taking down old site and setting up new one
    #since "mv" is faster than "cp -r" or "rm -rf"
    olddir = '/'.join(['/tmp', 'old-%s' % env.site])
    sudo('rm %s -rf' % olddir)

def server_setup():
    """
    Installs nginx and supervisord on remote host.  Sets up nginx and
    supervisord global config files.
    """
    install_apt_deps()
    template_list = (
        ('supervisord_root.conf', '/etc/supervisor/supervisord.conf'),
        ('nginx_root.conf','/etc/nginx/nginx.conf'),
    )
    _write_templates(template_list, env)
    restart()

def push():
    """
    The main function.  Assuming you have nginx and supervisord installed and
    configured, this function will put your site on the remote host and get it
    running.
    """
    archive()
    install_deps()
    push_code()
    write_config()
    switch()
    reload()
    cleanup()

def dump_config():
    """
    Just loads up the config and prints it out. For testing.
    """
    print env.config
