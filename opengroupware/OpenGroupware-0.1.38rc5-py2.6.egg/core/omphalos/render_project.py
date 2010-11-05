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
from render_object import *
from render_task   import render_task

def render_project(entity, detail, ctx):
    '''
            'comment': 'Update project comment',
            'endDate': <DateTime '20321231T18:59:00' at b796b34c>,
            'entityName': 'Project',
            'folderObjectId': 479360,
            'kind': '',
            'name': 'Updated project name',
            'number': 'P479340',
            'objectId': 479340,
            'ownerObjectId': 10160,
            'placeHolder': 0,
            'startDate': <DateTime '20070213T05:00:00' at b7964e0c>,
            'status': '',
            'version': ''}
    '''
    p = {
         'comment':         as_string(entity.comment),
         'endDate':         as_datetime(entity.end),
         'entityName':      'Project',
         'folderObjectId':  as_integer(entity.folder.object_id),
         'kind':            as_string(entity.kind),
         'name':            as_string(entity.name),
         'number':          as_string(entity.number),
         'objectId':        as_integer(entity.object_id),
         'ownerObjectId':   as_integer(entity.owner_id),
         'placeHolder':     as_integer(entity.is_fake),
         'startDate':       as_datetime(entity.start),
         'status':          as_string(entity.status),
         'version':         as_integer(entity.version)
        }
    if (detail & 4096):
        p['_TASKS'] = [ ]
        for task in entity.tasks:
            p['_TASKS'].append(render_task(task, 0, ctx))
    return render_object(p, entity, detail, ctx)