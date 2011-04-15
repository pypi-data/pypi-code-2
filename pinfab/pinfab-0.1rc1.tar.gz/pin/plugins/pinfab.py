import os, sys
from argparse import ArgumentParser

from fabric.main import main, load_fabfile

from pin import *
from pin.util import *
from pin import command, registry

class PinFabCommand(command.PinBaseCommandDelegator):
    '''
    Commands inside your fabfile.
    '''
    command = 'fab'

    @classmethod
    def get_subcommands(cls):
        cwd = os.getcwd()
        root = get_project_root(cwd)
        if root:
            doc, tasks = load_fabfile(os.path.join(root, 'fabfile.py'))
            return tasks
        return dict()

    def execute(self, cwd, root):
        if root:
            os.chdir(root)
            sys.argv[1:] = sys.argv[2:]
            main()
            return True

command.register(PinFabCommand)
