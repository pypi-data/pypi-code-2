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
import vobject, datetime, pytz
from coils.foundation       import Task

def chunk_string(string, delimiter):
    words = []
    for word in string.split(delimiter):
        if (len(word.strip()) > 0):
            words.append(word.strip())
    return words

def as_delimited_string(words, delimiter):
    result = ''
    for word in words:
        if (len(result) > 0):
            result = '{0},{1}'.format(result, word.strip())
        else:
            result = word.strip()
    return result

def render_tasks(tasks, ctx, **params):
    print 'render_tasks'
    cal = vobject.iCalendar()
    for task in tasks:
        if (isinstance(task, Task)):
            print 'rendering task'
            todo = cal.add('vtodo')
            render_task(task, todo, ctx, **params)
    return (str(cal.serialize()))

def render_task(task, todo, ctx, **params):
    todo.add('uid').value = 'coils://Task/{0}'.format(task.object_id)

    '''      ; the following are optional,
             ; but MUST NOT occur more than once

             class / completed / created / description / dtstamp /
             dtstart / geo / last-mod / location / organizer /
             percent / priority / recurid / seq / status /
             summary / uid / url /

             ; either 'due' or 'duration' may appear in
             ; a 'todoprop', but 'due' and 'duration'
             ; MUST NOT occur in the same 'todoprop'

             due / duration /

             ; the following are optional,
             ; and MAY occur more than once
             attach / attendee / categories / comment / contact /
             exdate / exrule / rstatus / related / resources /
             rdate / rrule / x-prop
    '''

    # Description / Comment
    if (task.comment is not None):
        # TODO: Sanitize comment
        todo.add('description').value =        task.comment
    else:
        todo.add('description').value =        ''

    todo.add('summary').value = task.name
    todo.add('dtstart').value                  = task.start
    todo.add('due').value                    = task.end
    if (task.completed is not None):
        todo.add('completed').value = task.completed
    # Organizer
    # Percent
    # Priority
    # URL ?
    # Attendee
    # Categories ?

    # STATUS
    ''' statvalue  =/ "NEEDS-ACTION"       ;Indicates to-do needs action.
                    / "COMPLETED"           ;Indicates to-do completed.
                    / "IN-PROCESS"          ;Indicates to-do in process of
                    / "CANCELLED"           ;Indicates to-do was cancelled.
        ;Status values for "VTODO".'''
    if (task.state == '00_created'):
        todo.add('status').value    = 'NEEDS-ACTION'
    elif (task.state == '30_archived' or task.state == '25_done'):
        todo.add('status').value    = 'COMPLETED'
    elif (task.state == '20_processing'):
        todo.add('status').value    = 'IN-PROCESS'
    else:
        todo.add('status').value    = 'CANCELLED'

    # Project (X-COILS-PROJECT)
    if (task.project is not None):
        project = todo.add('x-coils-project')
        project.value = task.project.name
        project.x_coils_project_id_param = unicode(task.project.object_id)
        if (task.project.kind is not None):
            project.x_coils_project_kind_param = task.project.kind

    # Kind (X-COILS-KIND)
    if (task.kind is not None):
        todo.add('x-coils-kind').value = task.kind

    return todo