import os
import subprocess
import sys


def run(args):
    cmd, cmdargs, env = args

    fullargs = [cmd]
    fullargs.extend(cmdargs)
    fullargs.extend(sys.argv[1:])

    newenv = dict(os.environ)
    for x in env:
        k, v = [y.strip() for y in x.split('=')]
        newenv[k] = v

    return subprocess.call(fullargs, env=newenv)
