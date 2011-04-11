from nuage.commands import BaseCommand
import argh


class Command(BaseCommand):
    _CMD_ALIAS = 'create'
    
    @argh.alias(_CMD_ALIAS)
    @argh.arg('app_name')
    def run(self, args):
        raw_input('API key:')
        raise argh.CommandError('Invalid API-key.')
