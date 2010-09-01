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
import logging
from coils.core         import *
from coils.foundation   import Appointment, Resource, Task
from render_appointment import render_appointments
from render_task        import render_tasks


class Render(object):
# TODO: This is a mess of hacks, and needs to be refactored.  But it works.
    @staticmethod
    def render(entity, ctx):
        Render.render(entity, ctx, {})

    #TODO: Shouldn't this method be named Render, static method names are usually upper-cased
    @staticmethod
    def render(entity, ctx, **params):
        log = logging.getLogger('render')
        #TODO: log duration of render at debug level
        if (entity is None):
            raise CoilsException('Attempt to render a None')
        elif (isinstance(entity, list)):
            # WARN: This is broken, we need to support a list of mixed types
            #try:
            #    if (isinstance(entity[0], Appointment)):
            return render_appointments(entity, ctx, **params)
            #    else:
            #        return render_tasks(entity, ctx, **params)
            #except Exception, e:
            ##    log.error('exception rendering appointments', exc_info=1)
            #   raise e
        elif (isinstance(entity, Appointment)):
            try:
                return render_appointments([entity], ctx, **params)
            except Exception, e:
                log.error('exception rendering Appointment objectId#%d' % entity.object_id, exc_info=1)
                raise e
        elif (isinstance(entity, Task)):
            try:
                return render_tasks([entity], ctx, **params)
            except Exception, e:
                log.error('exception rendering Task objectId#%d' % entity.object_id, exc_info=1)
                raise e
        else:
            raise CoilsException('Entity %s cannot be rendered as an iCalendar' % entity.__entityName__)