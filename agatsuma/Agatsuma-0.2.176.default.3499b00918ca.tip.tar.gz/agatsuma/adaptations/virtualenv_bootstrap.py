#!/usr/bin/python
import subprocess
import json

def cmd_call(*args):
    cmdline = ' '.join(args)
    print "$ %s" % (cmdline, )
    try:
        result = subprocess.call(args)
        if result:
            print "\nError while calling:\n  $ %s\nReturn code is: %d" % (cmdline, result)
            exit(result)
    except Exception, e:
            print "\nError while calling:\n  $ %s\nException: %s" % (cmdline, str(e), )
            exit(1)
    print "Done\n"

def perform_bootstrap(config, create_env = True):
    env_name = config["env_name"]
    dependencies = config["dependencies"]

    if create_env:
        cmd_call('virtualenv', env_name)

    for dep in dependencies:
        args = ['pip', 'install', '-E', env_name]
        if '/' in dep:
            args.extend(['-U', '-e', dep])
        elif dep.startswith('!'):
            args.extend(['-U', dep[1:]])
        else:
            args.append(dep)
        cmd_call(*args)

def bootstrap(create_env = True):
    cfg = open('bootstrap.json', 'r')
    config = json.loads(cfg.read())
    cfg.close()
    perform_bootstrap(config, create_env)

if __name__ == "__main__":
    bootstrap()