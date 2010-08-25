# Copyright (c) 2009 Adam Tauno Williams <awilliam@whitemice.org>
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
# THE SOFTWARE.
#
import sys, logging
#from coils.core.context import Context

class Command(object):
    _ctx       = None
    _result    = None
    _manager   = None
    __domain__ = None
    __operation__ = None

    def __init__(self):
        if (Command._manager is None):
            from bundlemanager import BundleManager
            Command._manager = BundleManager
        self.access_check = True
        self._result = None
        self._extra  = None
        self.log = logging.getLogger('%s::%s' % (self.__domain__, self.__operation__))
        if (self.log.isEnabledFor(logging.DEBUG)):
            self.debug = True
        else:
            self.debug = False
        pass

    @property
    def extra(self):
        return self._extra

    @extra.setter
    def extra(self, value):
        self._extra = value

    def notify(self):
        if (hasattr(self, 'obj')):
            object_id = self.obj.object_id
        else:
            object_id = None
        self._ctx.queue_for_commit('coils.master/__null',
                                   'coils.pubsub/publish:__coils__.event.{0}'.format(self.__domain__),
                                   { 'domain':     self.__domain__,
                                     'operation':  self.__operation__,
                                     'context':    self._ctx.account_id,
                                     'utctime':    self._ctx.get_utctime(),
                                     'object_id':  object_id,
                                     'extra_data': self.extra } )

    def parse_parameters(self, **params):
        if (params.has_key('access_check')):
            self.access_check = params['access_check']
        if ((params.get('debug', None) is not None) and (params['debug'] == True)):
            self.debug = True

    def command_name(self):
        return '{0}::{1}'.format(self.__domain__, self.__operation__)            

    def get_result(self):
        return self._result

    def audit_action(self):
        pass

    def prepare(self, ctx, **params):
        self._ctx = ctx
        self.parse_parameters(**params)
        return

    def run(self, **params):
        return

    def epilogue(self):
        self.audit_action()

    def run(self):
        self.run({})

