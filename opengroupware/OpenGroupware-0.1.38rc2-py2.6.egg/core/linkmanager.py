#!/usr/bin/python
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
from coils.foundation import ObjectLink

class LinkManager(object):
    __slots__ = ('_ctx')

    def __init__(self, ctx):
        self._ctx = ctx

    def links_to(self, entity):
        db = self._ctx.db_session()
        query = db.query(ObjectLink).filter(ObjectLink.target_id == entity.object_id)
        data = query.all()
        query = None
        return data

    def links_from(self, entity):
        db = self._ctx.db_session()
        query = db.query(ObjectLink).filter(ObjectLink.source_id == entity.object_id)
        data = query.all()
        query = None
        return data

    def links_to_and_from(self, entity):
        db = self._ctx.db_session()
        query = db.query(ObjectLink).filter(or_(ObjectLink.source_id == entity.object_id,
                                                 ObjectLink.target_id == entity.object_id))
        query = query.order_by(ObjectLink.source_id, ObjectLink.target_id, ObjectLink.kind)
        data = query.all()
        query = None
        return data

    def link(self, source, target, kind='generic', label=None):
        #TODO: Give a new link a label if none was provided
        db = self._ctx.db_session()
        if (kind is None):
            query = db.query(ObjectLink).filter(and_(ObjectLink.source_id == source,
                                                      ObjectLink.target == target))
        else:
            query = db.query(ObjectLink).filter(and_(ObjectLink.source_id == source,
                                                      ObjectLink.target == target,
                                                      Object.kind == kind))
        link = query.one()
        if (link is None):
            link = ObjectLink(source, target, kind, label)
            self._ctx.db_session().add(link)
        elif (link.label != label):
            link.label = label

    def unlink(self, source, target, kind='generic'):
        #TODO: Give a new link a label if none was provided
        db = self._ctx.db_session()
        if (kind is None):
            query = db.query(ObjectLink).filter(and_(ObjectLink.source_id == source,
                                                      ObjectLink.target_id == target))
        else:
            query = db.query(ObjectLink).filter(and_(ObjectLink.source_id == source,
                                                      ObjectLink.target_id == target,
                                                      Object.kind == kind))
        link = query.one()
        if (link is not None):
            self._ctx.db_session().delete(link)

    def sync_links(self, entity, links_b):
        db = self._ctx.db_session()
        links_a = self.links_to_and_from(entity)
        for link in links_a:
            removes.append(int(link.object_id))
        for link_b in links_b:
            for link_a in links_a:
                if (link_b == link_a):
                    # (update)
                    link_a.label = link_b.label
                    removes.remove(int(link_a.object_id))
                    break
            else:
                # Link_B was not found in Links_A (add)
                if (isinstance(link_b, 'dict')):
                    link = ObjectLink(link_b.get('source_id', None),
                                      link_b.get('target_id', None),
                                      link_b.get('kind', None),
                                      link_b.get('label', None))
                    db.add(link)
                else:
                    raise CoilsException('Unable to create new link from provided type.')
        # (delete)
        if (len(removes) > 0):
            db.query(ObjectLink).filter(ObjectLink.object_id.in_(removes)).delete()
