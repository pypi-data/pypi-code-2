#
# Copyright (c) 2009, 2010 Adam Tauno Williams <awilliam@whitemice.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#
import os, re
from datetime            import datetime
from xml.sax.saxutils    import escape, unescape
from tempfile            import mkstemp
from coils.core          import Command, CoilsException
from coils.foundation    import AuditEntry, BLOBManager

class ActionCommand(Command):
    def __init__(self):
        Command.__init__(self)
        self._rfile    = None
        self._wfile    = None
        self._proceed  = True
        self._continue = True

    def encode_text(self, text):
        ''' Wraps xml.sax.saxutils.escape so descendents don't have to do an import . '''
        return unicode(escape(text))

    def decode_text(self, text):
        ''' Wraps xml.sax.saxutils.unescape so descendents don't have to do an import . '''
        return unescape(text)

    def parse_parameters(self, **params):
        self._input         = params.get('input', None)
        self._label         = params.get('label', None)
        self._params        = params.get('parameters', {})
        self._process       = params.get('process')
        self._uuid          = params.get('uuid')
        self._scope         = params.get('scope', [])
        self._state         = params.get('state', None)

    def log_message(self, message):
        log_entry = AuditEntry()
        log_entry.context_id = self._process.object_id
        log_entry.action = '05_changed'
        log_entry.actor_id = self._ctx.account_id
        log_entry.message = message
        self._ctx.db_session().add(log_entry)

    def process_label_substitutions(self, text):
        if (text is None):
            return None
        if (len(text) < 3):
            return text
        # Process special internal labels
        labels = set(re.findall('\$__[A-z0-9]*__;', text))
        for label in labels:
            if (label == '$__DATE__;'):
                text = text.replace(label, datetime.now().strftime('%Y%m%d'))
            elif (label == '$__OMPHALOSDATE__;'):
                text = text.replace(label, datetime.now().strftime('%Y-%m-%d'))
            elif (label == '$__DATETIME__;'):
                text = text.replace(label, datetime.now().strftime('%Y%m%dT%H:%M'))
            elif (label == '$__OMPHALOSDATETIME__;'):
                text = text.replace(label, datetime.now().strftime('%Y-%m-%d %H:%M'))
            elif (label == '$__NOW_Y2__;'):
                text = text.replace(label, datetime.now().strftime('%y'))
            elif (label == '$__NOW_Y4__;'):
                text = text.replace(label, datetime.now().strftime('%Y'))
            elif (label == '$__NOW_M2__;'):
                text = text.replace(label, datetime.now().strftime('%m'))
            elif (label == '$__PID__;'):
                text = text.replace(label, str(self._process.object_id))
            elif (label == '$__EMAIL__;'):
                text = text.replace(label, self._ctx.email)
            elif (label == '$__ROUTE__;'):
                if (self._process.route is not None):
                    text = text.replace(label, self._process.route.name)
                else:
                    text = text.replace(label, u'UNKNOWN')
            elif (label[0:9] == '$__XATTR_'):
                propname = label[9:-3].lower()
                prop = self._ctx.property_manager.get_property(self._process,
                                                               'http://www.opengroupware.us/oie',
                                                               'xattr_{0}'.format(propname))
                if (prop is not None):
                    value = str(prop.get_value())
                    text = text.replace(label, value)
                else:
                    self.log.debug('Encountered unknown xattr reference {0}'.format(propname))
                    text = text.replace(label, '')
            else:
                self.log.debug('Encountered unknown {0} content alias'.format(label))
        # Process message labels
        labels = set(re.findall('\$[A-z0-9]*;', text))
        if (len(labels) == 0):
            return text
        for label in labels:
            self.log.debug('Retrieving text for label {0}'.format(label))
            try:
                data = self._ctx.run_command('message::get-text', process=self._process,
                                                                  scope=self._scope,
                                                                  label=label[:-1][1:])
                #self.log.info('Retrieved text for label "{0}": {1}'.format(label, data))
            except Exception, e:
                self.log.exception(e)
                self.log.error('Exception retrieving text for label {0}'.format(label))
                raise e
            text = text.replace(label, data)
        return text

    def parse_action_parameters(self):
        pass

    def verify_action(self):
        # Make sure an action has the three requisite components for execution
        # 1.) An Input
        # 2.) A process context
        # 3.) A copy of the current Process state
        #if (self._input is None):
        #    raise CoilsException('No input message specified for action.')
        if (self._process is None):
            raise CoilsException('No process associated with action.')
        if (self._state is None):
            raise CoilsException('No process state provided for action.')
        return True

    def audit_action(self):
        # Disable logging!
        pass

    def do_prepare(self):
        if (self._input is None):
            self._rfile = BLOBManager.ScratchFile()
            self._mime  = 'application/octet-stream'
        else:
            self._rfile    = self._ctx.run_command('message::get-handle', object=self._input)
            self._mime     = self._input.mimetype
        self._wfile    = BLOBManager.ScratchFile()

    def do_action(self):
        # Child MUST implement
        pass

    def do_epilogue(self):
        # Child MAY implement
        pass

    def result_mimetype(self):
        # Actions that produce output other than XML MUST override this so that
        # their messages are approprately marked.
        return 'application/xml'

    @property
    def scope_tip(self):
        # Returns the outermost scope id; which is the UUID of the action which
        # created the scope.  Scopes are created by the Workflow Executor's
        # Process workers.  Honoring scope is implemented in the appropriate
        # Workflow bundle's Logic commands.
        if (len(self._scope) > 0):
            return self._scope[-1]
        return None

    def store_in_message(self, label, wfile, mimetype='application/octet-stream'):
        message = None
        if (label is not None):
            message = self._ctx.run_command('message::get', process=self._process,
                                                            scope=self._scope,
                                                            label=label)
        if (message is None):
            self._result = self._ctx.run_command('message::new', process=self._process,
                                                                 handle=wfile,
                                                                 scope=self.scope_tip,
                                                                 mimetype=mimetype,
                                                                 label=label)
        else:
            self._result = self._ctx.run_command('message::set', object=message,
                                                                 handle=wfile,
                                                                 mimetype=mimetype)

    def run(self):
        self.parse_action_parameters()
        if (self.verify_action()):
            self.do_prepare()
            self.do_action()
            # Must close _rfile before _wfile so messages can replace themselves!
            self._rfile.close()
            # Flush the output temp file
            self._wfile.flush()
            self.store_in_message(self._label, self._wfile, self.result_mimetype())
            BLOBManager.Delete(self._wfile)
            self.do_epilogue()
        else:
            raise CoilsException('Action verification failed.')
        self._result = (self._continue, self._proceed)
