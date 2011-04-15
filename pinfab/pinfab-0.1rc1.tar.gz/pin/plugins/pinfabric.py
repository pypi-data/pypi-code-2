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
        doc, tasks = load_fabfile(os.path.join(self.root, 'fabfile.py'))
        return tasks

    def execute(self):
        os.chdir(self.root)
        sys.argv[1:] = sys.argv[2:]
        main()

command.register(PinFabCommand)
