"""\
Pipe for logging warning messages to a database and displaying a
message in the browser

WARNING: You always want a differnt database connection for warnings so
that saving the database doesn't commit changes that would otherwise be
rolled back. SQLite3 is the only database supported at the moment.
"""

import logging
import sys
import datetime
import databasepipe.setup

from bn import AttributeDict
from pipestack.pipe import Marble, MarblePipe
from pipestack.ensure import ensure_self_marble as ensure, ensure_method_bag

log = logging.getLogger(__name__)

class WarningMarble(Marble):
    def on_set_flow_state(marble, flow_state):
        marble.__dict__['messages'] = []

    @ensure('database', 'ticket')
    def add(marble, message, type=None):
        import urlconvert
        url = urlconvert.extract_url(marble.bag)
        database = marble.bag[marble.aliases['database']]
        ticket = marble.bag[marble.aliases['ticket']]
        marble.messages.append(AttributeDict(type=type, message=message))
        uid = database.insert_record(
            'warningpipe_warning',
            dict(
                user=ticket.get('username'),
                date=datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
                type=type,
                url=url,
                message=message,
            ),
            'uid'
        )
        # Make sure this change is commiteed
        database._connection.commit()
        log.debug('Warning pipe logged warning message %s type %s: %s', uid, type, message)

    @ensure('database')
    def all(marble):
        database = marble.bag[marble.aliases['database']]
        rows = database.query(
            '''
            SELECT 
              uid     
            , date    
            , message 
            , type    
            , user    
            , url     
            FROM warningpipe_warning
            ORDER BY url DESC, type DESC, message DESC, user DESC
            '''
        )
        warning_records = {}
        for row in rows:
            key = (
                row['url'],
                row['message'],
                row['type'],
                row['user'], 
            )
            value = {
                'uid': row['uid'], 'date': row['date']
            }
            if warning_records.has_key(key):
                warning_records[key].append(value)
            else:
                warning_records[key] = [value]
        data = warning_records.items()
        data.sort()
        return data




class WarningPipe(MarblePipe):
    marble_class = WarningMarble
    default_aliases = AttributeDict(database='database', ticket='ticket')

class SetupCmd(databasepipe.setup.BaseSetupCmd):

    table_names_string = 'warning tables'

    @ensure_method_bag('database')
    def create_tables(self, bag):
        bag[self.aliases['database']].query(
            '''
            CREATE TABLE warningpipe_warning (
                uid INTEGER PRIMARY KEY
              , date TEXT NOT NULL
              , message TEXT NOT NULL
              , type TEXT
              , user TEXT
              , url TEXT
            );
            ''',
            fetch=False
        )
        
    @ensure_method_bag('database')
    def drop_tables(self, bag):
        bag[self.aliases['database']].query(
            '''
            DROP TABLE IF EXISTS warningpipe_warning;
            ''',
            fetch=False,
        )

