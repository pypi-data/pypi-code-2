# Copyright (c) 2010 Adam Tauno Williams <awilliam@whitemice.org>
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
from coils.protocol.dav.foundation     import DAVFolder
from coils.protocol.dav.foundation     import EmptyFolder
from routesfolder                      import RoutesFolder
from formatsfolder                     import FormatsFolder
from loadschedule                      import LoadScheduleObject

class WorkflowFolder(DAVFolder):
    def __init__(self, parent, name, **params):
        DAVFolder.__init__(self, parent, name, **params)

    def _load_contents(self):
        self.insert_child('Routes', None)
        self.insert_child('Formats', None)
        self.insert_child('Schedule', None)
        self.insert_child('Maps', None)
        self.insert_child('LoadSchedule.txt', None)
        return True

    def object_for_key(self, name, auto_load_enabled=True, is_webdav=False):
        if (name == 'Routes'):
            return RoutesFolder(self,
                                 name,
                                 parameters=self.parameters,
                                 request=self.request,
                                 context=self.context)
        elif (name == 'LoadSchedule.txt'):
            return LoadScheduleObject(self,
                                       name,
                                       parameters=self.parameters,
                                       request=self.request,
                                       context=self.context)
        elif (name == 'Formats'):
            return FormatsFolder(self,
                                  name,
                                  parameters=self.parameters,
                                  request=self.request,
                                  context=self.context)
        elif (name == 'Schedule'):
            return EmptyFolder(self,
                                name,
                                parameters=self.parameters,
                                request=self.request,
                                context=self.context)
        elif (name == 'Maps'):
            return EmptyFolder(self,
                                name,
                                parameters=self.parameters,
                                request=self.request,
                                context=self.context)
        return self.no_such_path()
