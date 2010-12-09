from blazech.commands import BaseCommand

class Command(BaseCommand):
    name = 'hello-world'

    def create_arguments(self):
        #self.parser is the argparse parser for this sub-command
        self.parser.add_argument(
            '-n', '--name',
            help='who do you want to say hello to',
            default='world'
        )

    def execute(self, args):
        print 'hello %s' % args.name
