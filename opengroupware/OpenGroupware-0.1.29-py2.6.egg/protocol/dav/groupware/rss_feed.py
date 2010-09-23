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
from coils.core import *
from datetime import datetime
from coils.protocol.dav.foundation import RSSFeed

class TasksRSSFeed(RSSFeed):

    def __init__(self, parent, name, **params):
        RSSFeed.__init__(self, parent, name, **params)
        self.metadata = { 'feedUrl':            self.get_path(),
                          'channelUrl':         self.get_path(),
                          'channelTitle':       'Tasks',
                          'channelDescription': 'Tasks Feed Description' }

    def actions_query(self, limit=150):
        db = self.context.db_session()
        return []

    def get_items(self):
        # self.context.run_command('task::get-delegated')
        query = getattr(self, '{0}_query'.format(self.name[:-4]))()
        for action in query.all():

            if action.task.project is None:
                project_name = 'n/a'
            else:
                project_name = action.task.project.name



            yield { 'description': self.transcode_text(action.comment),
                     'title':       'title',
                     'date':        action.date,
                     'author':      action.actor_id,
                     'link':        None,
                     'guid':         'xyz',
                     'object_id':   action.object_id }
