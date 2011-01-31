#!/usr/bin/env python
import subprocess
import sys
import time
import os
import pkg_resources
import shutil
import tempfile
from signal import SIGTERM, SIGINT

import yaml

import silk.lib

def run_til_you_die(args, kill_signal, cwd=os.getcwd(), env={}):
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

def run_devserver(config, root):
    # Overwrite the wsgi_app config var to point to our internal app that will
    # also mount the static dirs.
    config['wsgi_app'] = 'silk.devserver:app'
    
    cmd = silk.lib.get_gunicorn_cmd(config)
    
    subproc_env = {
        'SILK_ROOT': root,
        'SILK_ROLE': silk.lib.get_role(),
    }

    # By adding our current subproc_environment to that used for the subprocess, we
    # ensure that the same paths will be used (such as those set by virtualsubproc_env)
    subproc_env.update(os.environ)

    run_til_you_die(cmd.split(), SIGINT, cwd=root, env=subproc_env)

    # This 1 second sleep lets the gunicorn workers exit before we show the
    # prompt again.
    time.sleep(1)

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

def local_python_deps(config, root):
    """Write a requirements.txt from deps.yaml file for pip, then run pip on it."""
    depfile = os.path.join(silk.lib.get_site_root(os.getcwd()), 'deps.yaml')
    txt = open(depfile).read()
    deps = yaml.safe_load(txt)
    reqs = '\n'.join(deps['python_packages'])

    tmpfile = tempfile.NamedTemporaryFile()
    tmpfile.write(reqs)
    tmpfile.seek(0)

    pip_cmd = silk.lib.get_pip_cmd(config) 
    cmd = '%s -r %s' % (pip_cmd, tmpfile.name)
    run_til_you_die(cmd.split(), SIGTERM)
    tmpfile.close()

cmd_map = {
    'run': run_devserver,
    'skel': install_skel,
    'deps': local_python_deps
}

config_required = (
    run_devserver,
    local_python_deps,
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
