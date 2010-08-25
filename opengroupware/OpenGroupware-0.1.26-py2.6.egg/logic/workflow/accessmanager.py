#
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
#
from coils.core import EntityAccessManager

class MessageAccessManager(EntityAccessManager):
    __entity__ = 'Message'

    def __init__(self, ctx):
        EntityAccessManager.__init__(self, ctx)

    def implied_rights(self, objects):
        rights = { }
        for entity in objects:
            rights[entity] = set()
            rights[entity].add('w') # Modify
            rights[entity].add('d') # Delete
            rights[entity].add('t') # Delete member
            rights[entity].add('l') # List
            rights[entity].add('r') # Read
            rights[entity].add('v') # View
        return rights


class RouteAccessManager(EntityAccessManager):
    __entity__ = 'Route'

    def __init__(self, ctx):
        EntityAccessManager.__init__(self, ctx)

    def implied_rights(self, objects):
        rights = { }
        for entity in objects:
            rights[entity] = set()
            rights[entity].add('w') # Modify
            rights[entity].add('d') # Delete
            rights[entity].add('t') # Delete member
            rights[entity].add('l') # List
            rights[entity].add('r') # Read
            rights[entity].add('v') # View
        return rights


class ProcessAccessManager(EntityAccessManager):
    __entity__ = 'Process'

    def __init__(self, ctx):
        EntityAccessManager.__init__(self, ctx)

    def implied_rights(self, objects):
        rights = { }
        for entity in objects:
            rights[entity] = set()
            rights[entity].add('w') # Modify
            rights[entity].add('d') # Delete
            rights[entity].add('t') # Delete member
            rights[entity].add('l') # List
            rights[entity].add('r') # Read
            rights[entity].add('v') # View
        return rights