from blazech.commands import BaseCommand

class Foo(BaseCommand):
    name = 'foo'

    def execute(self, args):
        print 'entry-point foo'
