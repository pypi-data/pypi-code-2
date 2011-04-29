from blazech.commands import BaseCommand

class ProjectStat(BaseCommand):
    name = 'bar'

    def execute(self, args):
        print 'entry-point bar'

# without a name attribute, this class won't be recognized
class _CustomBase(BaseCommand):
    def donothing(self):
        pass
