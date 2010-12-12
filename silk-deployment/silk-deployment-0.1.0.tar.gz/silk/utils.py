#!/usr/bin/env python
import subprocess
import sys
import time
import os
import pkg_resources
import shutil
import random
from signal import SIGTERM, SIGINT

import cherrypy
import yaml

import silk.lib

def run_til_you_die(args, kill_signal, cwd=os.getcwd(), env={}):
    print 'Running %s in dir %s with env %s' % (' '.join(args), cwd, str(env))
    env.update(os.environ)
    proc = subprocess.Popen(args, cwd=cwd, env=env)
    try:
        proc.wait()
    except KeyboardInterrupt as e:
        print "KeyboardInterrupt"
        proc.send_signal(kill_signal)
    except Exception as e:
        print e
        proc.send_signal(kill_signal)

def run_fab(args):
    args[0] = 'fab'
    run_til_you_die(args, SIGTERM)

def run_gunicorn(config, root):
    cmd = silk.lib.get_gunicorn_cmd(config)
    print 'config', config
    run_til_you_die(cmd.split(), SIGINT, cwd=root, env=config['env'])
    #give the child processes some time to end before returning the shell
    #there must be a more elegant way to do that, but I don't know it
    time.sleep(1)

def run_cherrypy(config, root):
    """Mount each of the static dirs in site.yaml as its own app
    in the cherrypy tree.  Then mount the wsgi app as the root, and run."""
    if config['static_dirs']:
        for static_dir in config['static_dirs']:
            #mount each of our static dirs as its own app in the cherrypy tree
            url_path = static_dir['url_path'].rstrip('/')
            sys_path = os.path.join(root, static_dir['system_path'])
            cherry_conf = {'/': {'tools.staticdir.on': True,
                                 'tools.staticdir.dir': sys_path,}}
            cherrypy.tree.mount(None, script_name=url_path, config=cherry_conf)
    #mount the wsgi app
    sys.path.append(root)
    os.chdir(root)
    wsgi_app = cherrypy.lib.attributes(config['wsgi_app'].replace(':', '.'))
    cherrypy.tree.graft(wsgi_app, '')
    #update the env vars with the ones from the deployment role
    os.environ.update(config['env'])
    #run cherrypy
    cherrypy.config.update({
        'server.socket_host': '127.0.0.1',
        'server.socket_port': 8000
    })
    cherrypy.engine.start()
    cherrypy.engine.block()

def install_skel(sitename):
    """Copies the contents of site_templates into the named directory (within cwd)"""
    #get the dir from pkg_resources
    src = pkg_resources.resource_filename('silk', 'site_templates')
    try:
        shutil.copytree(src, os.path.join(os.getcwd(), sitename))
    except OSError, e:
        print e
    
def freeze_2_yaml():
    """Read lines of text from stdin and print a python_packages yaml list"""
    lines = sys.stdin.read().split('\n')#split only on newlines, not spaces
    lines = [line for line in lines if line]#remove empty lines
    print yaml.safe_dump({'python_packages':lines}, default_flow_style=False)

def yaml_2_freeze():
    """Read lines of deps.yaml from stdin and print requirements.txt contents"""
    txt = sys.stdin.read()
    deps = yaml.safe_load(txt)
    print '\n'.join(deps['python_packages'])

def local_python_deps():
    """Write a requirements.txt from deps.yaml file for pip, then run pip on it."""
    depfile = os.path.join(silk.lib.get_site_root(os.getcwd()), 'deps.yaml')
    txt = open(depfile).read()
    deps = yaml.safe_load(txt)
    print deps
    reqs = '\n'.join(deps['python_packages'])
    print reqs
    tmpfile = ''.join([random.choice('abcdefg') for x in xrange(5)]) + '-reqs.txt'
    #OH NOE, LINUX-SPECIFIC
    tmpfile = os.path.join('/tmp', tmpfile)
    f = open(tmpfile, 'w')
    f.write(reqs)
    f.close()
    cmd = 'pip install -r %s' % tmpfile
    run_til_you_die(cmd.split(), SIGTERM)
    os.remove(tmpfile)

cmd_map = {
    'grun': run_gunicorn,
    'run': run_cherrypy,
    'skel': install_skel,
    'deps': local_python_deps
}

config_required = (
    run_gunicorn,
    run_cherrypy,
)

def cmd_dispatcher():
    """wraps 'fab', handles 'silk run'"""
    args = sys.argv
    try:
        cmd = args[1]
    except IndexError:
        run_fab(*args)

    if cmd in cmd_map:
        cmd_func = cmd_map[cmd]
        if cmd_func in config_required:
            role = silk.lib.get_role()
            root = silk.lib.get_site_root(os.getcwd())
            config = silk.lib.get_config(root, role)
            cmd_func(config, root)
        else:
            cmd_func(*args[2:])
    else:
        run_fab(args)
