from blazech.application import Application
from blazech.commands import BaseCommand
from ...tests.cmdapp import commands

def app_factory(initial_args=None):
    app = Application('cmdapp')
    #app.load_commands(commands)
    #app.load_commands(globals())
    app.run_cmd(initial_args)

class Baz(BaseCommand):
    name = 'baz'

    def execute(self, args):
        print 'local baz'

