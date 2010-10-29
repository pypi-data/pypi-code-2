"""\
Pipe for displaying HTML tracebacks or emailing error reports
"""

import logging
import cgitb
import sys
import traceback
import StringIO
import datetime

from bn import AttributeDict, str_dict
from configconvert import stringToObject
from pipestack.pipe import Marble, MarblePipe
from conversionkit import chainPostConverters, Conversion, set_error, Field
from stringconvert import unicodeToUnicode, unicodeToBoolean
from stringconvert.email import listOfEmails, unicodeToEmail
from recordconvert import toRecord
from databasepipe.setup import BaseSetupCmd
from pipestack.ensure import ensure_method_bag, ensure_self_marble

to_unicode = unicodeToUnicode()

log = logging.getLogger(__name__)

class ErrorReportMarble(Marble):
    def report(marble, exc_info=None):
        if not hasattr(marble.bag, marble.aliases.mail):
            marble.bag.add(marble.aliases.mail)
        # Use the mail marble to send a report
        data = dict(
            to=marble.config.to,
            from_email=marble.config.from_email,
            from_name=marble.config.from_name,
            subject=marble.config.subject,
            type='html',
        )
        msg = display_html(exc_info)
        log.debug('Sending error report with these options: %r', options)
        marble.bag.mail.send(
            msg,
            **options
        )

    def display_html(marble, exc_info=None):
        log.debug('Preparing HTML error report for %r', exc_info[1])
        if exc_info is None:
            exc_info = sys.exc_info()
        # Get the traceback information
        return cgitb.html(exc_info)

    def display_text(marble, exc_info=None):
        log.debug('Preparing text error report for %r', exc_info[1])
        if exc_info is None:
            exc_info = sys.exc_info()
        fp = StringIO.StringIO()
        traceback.print_tb(exc_info[2], file=fp)
        tb = fp.getvalue()
        fp.close()
        return tb

    def error_document(marble):
        errordocument_available = False
        try:
            # Try to use the error document pipe
            if not hasattr(marble.bag, marble.aliases.errordocument):
                log.debug('Trying to add the %s bag to report an error', marble.aliases.errordocument)
                marble.bag.add(marble.aliases.errordocument)
            log.debug('Using the %s bag to report an error', marble.aliases.errordocument)
            marble.bag[marble.aliases.errordocument].render(status='500 An error occurred')
            errordocument_available = True
        except:
            pass
        if not errordocument_available:
            # Otherwise fall back to a simple message.
            marble.bag.http_response.status = '500 Internal Server Error'
            marble.bag.http_response.header_list = [
                dict(name='Content-type', value='text/plain; charset=utf-8')
            ]
            marble.bag.http_response.body = ['An error occurred']


    #def on_set_flow_state(marble, flow_state):
    #    marble.__dict__['exceptions'] = []

    @ensure_self_marble('database', 'ticket')
    def add(marble, exc_info):
        # Try to assemble the current URL:
        import urlconvert
        url = urlconvert.extract_url(marble.bag)
        database = marble.bag[marble.aliases['database']]
        ticket = marble.bag[marble.aliases['ticket']]
        #marble.excpetions.append(AttributeDict(type=type, message=message))
        type=repr(exc_info[0])
        message=str(exc_info[1])
        try:
            html = marble.display_html(exc_info)
        except:
            html = 'Failed to generate an HTML report'
        database.insert_record(
            'errorreport_exception',
            dict(
                user=ticket.get('username'),
                url=url,
                date=datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
                type=type,
                message=message,
                html=html,
            ),
            'uid',
        )
        # Make sure this change is commiteed
        database._connection.commit()
        log.debug('ErrorReport pipe added an exception type %s: %s', type, message)

    @ensure_self_marble('database')
    def get(marble, uid):
        database = marble.bag[marble.aliases['database']]
        rows = database.query(
            '''
            SELECT 
                html
            FROM errorreport_exception
            where uid = ?
            ''',
            (uid,),
            format='list'
        )
        if not rows:
            return None
        else:
            return rows[0][0]

    @ensure_self_marble('database')
    def hide(marble, uid):
        database = marble.bag[marble.aliases['database']]
        rows = database.query(
            '''
            UPDATE errorreport_exception
            SET new = 0
            WHERE
              uid = ?
            ''',
            (uid,),
            fetch=False,
        )

    @ensure_self_marble('database')
    def show(marble, uid):
        database = marble.bag[marble.aliases['database']]
        rows = database.query(
            '''
            UPDATE errorreport_exception
            SET new = 1
            WHERE
              uid = ?
            ''',
            (uid,),
            fetch=False,
        )

    @ensure_self_marble('database')
    def all(marble, hide_old=True):
        database = marble.bag[marble.aliases['database']]
        values=[]
        sql = '''
            SELECT 
              uid     
            , date    
            , message 
            , type    
            , user    
            , url     
            , new
            FROM errorreport_exception
        '''
        if not hide_old:
            sql += '''
            WHERE new=1
            '''
        sql += '''
            ORDER BY url DESC, type DESC, message DESC, user DESC
        '''
        rows = database.query(
            sql,
            tuple(values),
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
                'uid': row['uid'], 'date': row['date'], 'new': row['new']
            }
            if warning_records.has_key(key):
                warning_records[key].append(value)
            else:
                warning_records[key] = [value]
        data = warning_records.items()
        data.sort()
        return data


def productionTo():
    def productionTo_post_converter(conversion, state=None):
        if conversion.successful and conversion.result.get('enable_email_report') and not conversion.result.has_key('to'):
            set_error(conversion, "You must specify at least one email address in '%(name)s.to' if '%(name)senable_email_report' is True"%(dict(name=name),))
    return productionTo_post_converter

class ErrorReportPipe(MarblePipe):
    marble_class = ErrorReportMarble
    default_aliases = AttributeDict(mail='mail', errordocument='errordocument', database='database', ticket='ticket')
    options = dict(
        subject = Field(to_unicode),
        to = Field(
            listOfEmails(),
        ),
        from_email = Field(unicodeToEmail()),
        from_name = Field(to_unicode),
        enable_traceback = Field(
            unicodeToBoolean(),
            missing_or_empty_default = False,
        ),
        enable_database_report = Field(
            unicodeToBoolean(),
            missing_or_empty_default = False,
        ),
        enable_email_report = Field(
            unicodeToBoolean(),
            missing_or_empty_default = False,
        ),
        enable_email_report_fallback = Field(
            unicodeToBoolean(),
            missing_or_empty_default = False,
        ),
        enable_traceback_fallback = Field(
            unicodeToBoolean(),
            missing_or_empty_default=False,
        ),
    )
    post_converters = [
        productionTo(),
    ]

    def leave(self, bag, error=False):
        if not error:
            return
        marble = bag[self.name]
        original_error = sys.exc_info()
        if not marble.config.enable_traceback and not marble.config.enable_email_report:
            log.info('Error occurred, showing a 500 error document but not reporting it. Error: %r', original_error[1])
            return marble.error_document() 
        log.info('Error occurred, reporting it. Error: %r', original_error[1])
        # Try to generate an error report:
        if marble.config.enable_database_report:
            marble.add(original_error)
        try: 
            msg = marble.display_html(original_error)
            type = 'html'
        except Exception, e:
            if marble.config.enable_traceback_fallback:
                log.error('Failed to generate an HTML error report, trying text version. Error was: %r', e)
                try: 
                    msg = marble.display_text(original_error)
                    type = 'text'
                except Exception, e:
                    log.error('Failed to generate a text error report. Trying to just show the error, and time. Error was: %r', e)
                    try:
                        msg = 'An error occurred but the traceback could not be displayed. Please check the logs for the %r pipe at time %r for details. The error was: %r'%(
                            self.name, 
                            datetime.datetime.now().isoformat(),
                            original_error[1]
                        )
                        type = 'text'
                    except Exception, e:
                        log.error('Failed to show the simplified error output too, falling back to a plain text message. Error was: %r', e)
                        msg = 'An error occurred'
                        type = 'text'
            else:
                raise
        # Now either display that report or a 500 error document
        if marble.config.enable_traceback:
            bag.http_response.status = '500 Internal Server Error'
            bag.http_response.header_list = [
                dict(
                    name='Content-type', 
                    value='text/%s; charset=utf-8'%(type == 'html' and 'html' or 'plain')
                )
            ]
            bag.http_response.body = [msg]
        else:
            marble.error_document()
        # Now email that report if requested to do so
        if marble.config.enable_email_report:
            try:
                marble.report()
            except Exception, e:
                log.error('Error in %s pipe trying to send an email error report. Original error: %r, New error: %r', self.aliases.errordocument, original_error[1], e)
                if not bag[self.name].config.enable_email_report_fallback:
                    raise
        bag.interrupt_flow(error_handled = True)

class SetupCmd(BaseSetupCmd):
    table_names_string = 'error report tables'

    @ensure_method_bag('database')
    def create_tables(self, bag):
        bag[self.aliases['database']].query(
            '''
            CREATE TABLE errorreport_exception (
                uid INTEGER PRIMARY KEY
              , date TEXT NOT NULL
              , message TEXT NOT NULL
              , type TEXT
              , user TEXT
              , url TEXT
              , html TEXT
              , new BOOLEAN DEFAULT 1
            );
            ''',
            fetch=False
        )
        
    @ensure_method_bag('database')
    def drop_tables(self, bag):
        bag[self.aliases['database']].query(
            '''
            DROP TABLE IF EXISTS errorreport_exception;
            ''',
            fetch=False,
        )

