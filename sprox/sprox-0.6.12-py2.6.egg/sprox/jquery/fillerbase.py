"""
fillerbase Module

Classes to help fill widgets with data

Copyright (c) 2008 Christopher Perkins
Original Version by Christopher Perkins 2008
Released under MIT license.
"""

from sprox.fillerbase import TableFiller

class JQueryTableFiller(TableFiller):

    def get_value(self, value=None, **kw):
        page = int(kw.get('page', 1))
        rp = int(kw.get('rp', 25))
        order_by = kw.get('sortname', None) or None
        if order_by == '__actions__':
            order_by = None
        desc = not(kw.get('sortorder', None) == 'desc')

        offset = (page -1)*rp
        limit = rp
        items = super(JQueryTableFiller, self).get_value(value, limit=limit, offset=offset, order_by=order_by, desc=desc, **kw)
        count = self.get_count()
        identifier = self.__provider__.get_primary_field(self.__entity__)

        rows = [{'id': item[identifier],
                    'cell': [item[key] for key in self.__fields__]} for item in items]
        return dict(page=page, total=count, rows=rows)
