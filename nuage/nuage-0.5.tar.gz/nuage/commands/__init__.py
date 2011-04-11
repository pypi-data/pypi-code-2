import os
import sys
import argh
from nuage.client import NuageClient

COMMANDS_PATH = 'nuage.commands'


def get_commands():
    command_dir = os.listdir(os.path.dirname(__file__))
    command_names = map(
        lambda x: x.strip('.py'),
        filter(lambda x: x.endswith('py'),
               filter(lambda x: not x.startswith('_'), command_dir)
               )
        )
    commands = []
    for name in command_names:
        command_name = '%s.%s' % (COMMANDS_PATH, name)
        __import__(command_name)
        try:
            run = sys.modules[command_name].Command().run
            commands.append(run)
        except AttributeError, e:
            print e

    return commands


class BaseCommand(object):
    def __init__(self):
        self.client = NuageClient()

    def default_run(self, args):
        print 'Enter your authentication credentials'
        raw_input('API key:')
        raise argh.CommandError('Invalid API-key. See: http://nuagehq.com/faq/api-key')
