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
from coils.net              import *
from foundation             import DAVFolder, DAVObject, EmptyFolder
# DAV content providers
from groupware              import ContactsFolder, CalendarFolder, AccountsFolder, \
                                    TeamsFolder, TasksFolder, FavoritesFolder, \
                                    ProjectsFolder, CabinetsFolder
from files                  import FilesFolder
from workflow               import WorkflowFolder

DAV_ROOT_FOLDERS = { 'Contacts'     : 'ContactsFolder',
                     'Projects'     : 'ProjectsFolder',
                     'Calendar'     : 'CalendarFolder',
                     'Journal'      : 'EmptyFolder',
                     'Collections'  : 'EmptyFolder',
                     'Files'        : 'FilesFolder',
                     'Cabinets'     : 'CabinetsFolder',
                     'Users'        : 'AccountsFolder',
                     'Tasks'        : 'TasksFolder',
                     'Teams'        : 'TeamsFolder',
                     'Favorites'    : 'FavoritesFolder',
                     'Workflow'     : 'WorkflowFolder' }

class DAVRoot(DAVFolder, Protocol):
    '''The root of the DAV hierarchy.'''
    __pattern__   = 'dav'
    __namespace__ = None
    __xmlrpc__    = False

    def __init__(self, parent, **params):
        DAVFolder.__init__(self, parent, 'dav', **params)
        DAVFolder.Root = self
        #print self.user_agent

    def get_name(self):
        return 'dav'

    def _load_contents(self):
        self.init_context()
        for key in DAV_ROOT_FOLDERS.keys():
            classname = DAV_ROOT_FOLDERS[key]
            classclass = eval(classname)
            self.insert_child(key,
                              classclass(self, key, parameters=self.parameters,
                                                    request=self.request,
                                                    context=self.context))
        return True
