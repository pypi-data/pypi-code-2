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

to_unicode = unicodeToUnicode()

log = logging.getLogger(__name__)

class ErrorReportMarble(Marble):
    def report(marble, exc_info=None):
        if not hasattr(marble.bag, marble.aliases.mail):
            marble.bag.add(marble.aliases.mail)
        # Use the mail bag to send a report
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
            marble.bag.http.response.status = '500 Internal Server Error'
            marble.bag.http.response.headers = [
                ('Content-type', 'text/plain; charset=utf-8')
            ]
            marble.bag.http.response.body = ['An error occurred']

def productionTo():
    def productionTo_post_converter(conversion, state=None):
        if conversion.successful and conversion.result.get('enable_email_report') and not conversion.result.has_key('to'):
            set_error(conversion, "You must specify at least one email address in '%(name)s.to' if '%(name)senable_email_report' is True"%(dict(name=name),))
    return productionTo_post_converter

class ErrorReportPipe(MarblePipe):
    marble_class = ErrorReportMarble
    #required_section_error_message = "'%(name)s.to', '%(name)s.from_email' and '%(name)s.subject'"
    default_aliases = AttributeDict(mail='mail', errordocument='errordocument')
    options = dict(
        subject = Field(to_unicode),
        to = Field(
            listOfEmails(),
            #"The option '%(name)s.to' cannot be empty",
        ),
        from_email = Field(unicodeToEmail()),
        from_name = Field(to_unicode),
        enable_traceback = Field(
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
            bag.http.response.status = '500 Internal Server Error'
            bag.http.response.headers = [
                ('Content-type', 'text/%s; charset=utf-8'%(type == 'html' and 'html' or 'plain'))
            ]
            bag.http.response.body = [msg]
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

