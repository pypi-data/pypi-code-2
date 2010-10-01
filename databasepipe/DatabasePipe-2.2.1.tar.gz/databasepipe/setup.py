import getopt
import logging
from commandtool import Cmd
from pipestack.ensure import ensure_method_bag
from bn import AttributeDict

log = logging.getLogger(__name__)

class BaseSetupCmd(Cmd):
    # The derived class must specify this. It is used in the 
    # warning message to describe what will be removed
    # table_names_string = u"XXX tables"

    arg_spec = [
        ('ACTION', 'Can be DROP to remove tables, CREATE to create them')
    ]
    option_spec = Cmd.option_spec.copy()
    option_spec.update({
        'noinput': dict(
            options = ['-y', '--no-input'],
            help = 'Don\'t prompt on potentially dangerous commands',
        ),
        'dropFirst': dict(
            ptions = ['--drop-first'],
            help = 'Drop all the tables before creating them again',
        ),
    })
    help = dict(summary='Set up the table the warning database requires')
    def on_run(self, app, args, opts):
         if not hasattr(self, 'table_names_string'):
             raise Exception('The derived class does not have \'self.table_names_string\' specified')
         # ... convert opts and args if needed
         bag = AttributeDict(
             cmd=AttributeDict(
                 opts=opts,
                 args=args,
             )
         )
         app.start_flow(bag=bag, run=self.handle)

    @ensure_method_bag('database')
    def handle(self, bag):
        if not bag.app.config[self.aliases['database']].plugin == 'sqlite3':
            raise Exception(
                'Only SQLite3 is supported as a database for the WarningPipe'
            )
        if bag.cmd.args[0] == 'CREATE':
            if bag.cmd.opts.dropFirst:
                if bag.cmd.opts.noinput or raw_input(
                    'Are you sure you want to permantly remove the %s '
                    'and all their data? [N/y] ' % (
                        self.table_names_string,
                    )
                ).lower() == 'y':
                    print "Dropping the database tables"
                    self.drop_tables(bag)
                else:
                    print "Aborting, no changed made"
                    return 
            print "Creating the database tables"
            self.create_tables(bag)
            print "All done!."
        elif bag.cmd.args[0] == 'DROP':
            if bag.cmd.opts.dropFirst:
                raise getopt.GetoptError(
                    'You cannot use --drop-first for the DROP action'
                )
            if bag.cmd.opts.noinput or raw_input(
                'Are you sure you want to permantly remove the %s '
                'and all their data? [N/y] ' % (
                    self.table_names_string,
                )
            ).lower() == 'y':
                print "Dropping the database tables"
                self.drop_tables(bag)
                print "All done!."
            else:
                print "Aborting, no changed made"
          
        else:
            raise getopt.GetoptError(
                'Unknown action %r, expected \'CREATE\' or \'DROP\''%(
                    bag.cmd.args[0],
                )
            )

    @ensure_method_bag('database')
    def create_tables(self, bag):
        raise NotImplementedError('Please implement in the derived class')
        
    @ensure_method_bag('database')
    def drop_tables(self, bag):
        raise NotImplementedError('Please implement in the derived class')

