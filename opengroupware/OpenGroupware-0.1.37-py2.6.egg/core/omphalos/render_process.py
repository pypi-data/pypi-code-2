#
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
#
from render_object import *

def render_process(entity, detail, ctx):
    '''
        '_OBJECTLINKS': [],
         '_PROPERTIES': [],
         'objectId':
         'entityName': 'Route',
         'name':       'XrefrType4DuplicateErrorReport',
         'created':    ,
         'modified':   ,
         'version':    ,
         'ownerObjectId': 10100
         'routeObjectId':
         'priority'


        '''
    p = {
         'entityName':             'Process',
         'objectId':               entity.object_id,
         'GUID':                   as_string(entity.uuid),
         'ownerObjectId':          as_integer(entity.owner_id),
         'routeObjectId':          as_integer(entity.route_id),
         'created':                as_datetime(entity.created),
         'modified':               as_datetime(entity.modified),
         'completed':              as_datetime(entity.completed),
         'parked':                 as_datetime(entity.parked),
         'started':                as_datetime(entity.started),
         'version':                as_integer(entity.version),
         'inputMessageUUID':       as_string(entity.input_message),
         'outputMessageUUID':      as_string(entity.output_message),
         #'state':                  as_string(entity.state),
         'taskObjectId':           as_integer(entity.task_id),
         'priority':               as_integer(entity.priority),
        }
    if (entity.state == 'Q'):   p['state'] = 'queued'
    elif (entity.state == 'R'): p['state'] = 'running'
    elif (entity.state == 'F'): p['state'] = 'failed'
    elif (entity.state == 'C'): p['state'] = 'completed'
    elif (entity.state == 'P'): p['state'] = 'parked'
    elif (entity.state == 'I'): p['state'] = 'initialized'
    elif (entity.state == 'Z'): p['state'] = 'zombie'
    if entity.route is None:
        p['routeName'] = ''
    else:
        p['routeName'] = as_string(entity.route.name)
    # FLAGS
    flags = []
    if (entity.owner_id == ctx.account_id): flags.append('SELF')
    # TODO: Provide zOGI access flags: WRITE / READONLY, DELETE
    rights = ctx.access_manager.access_rights(ctx, entity)
    p['FLAGS'] = flags
    return render_object(p, entity, detail, ctx)
