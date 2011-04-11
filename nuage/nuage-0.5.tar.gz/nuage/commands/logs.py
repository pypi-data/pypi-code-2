from nuage.commands import BaseCommand
import argh


class Command(BaseCommand):

    @argh.alias(__name__.split('.')[-1])
    def run(self, args):
        self.default_run(args)
    pass
