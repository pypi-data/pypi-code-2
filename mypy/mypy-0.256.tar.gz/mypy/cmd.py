import sys
from shutil import copytree
from os.path import join, dirname

PREFIX = dirname(__file__)


def ignore_new(dirname, filelist):
    ignore = []
    for i in filelist:
        if i == ".svn" or i.endswith(".pyc"):
            ignore.append(i)
    return ignore

def runcmd(argv):
    len_argv = len(argv)
    if not argv:
        return
    cmd = argv[0]
    if cmd == "new":
        if len_argv >= 2:
            name = argv[1]
            t = join(PREFIX, "project_template")
            copytree(t, name, ignore=ignore_new)

runcmd(sys.argv[1:])