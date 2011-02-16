# takeaction: content as actions
# Copyright (C) 2007 Jarn AS
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
from Products.Five import BrowserView

class ManageTakeAction(BrowserView):
    def has_items(self):
        return bool(self.context._items)
    
    def items(self):
        selected = self.request.get('selected', ())
        for i, item in enumerate(self.context._items):
            yield dict(
                path=item.path,
                category=item.category,
                selected=(i in selected),
                index=i)
            
    def add(self):
        self.context.addAction(self.request['path'], self.request['category'])
        
    def save(self):
        items = self.request['items']
        for i, item in enumerate(self.context._items):
            item.path = items[i].path
            item.category = items[i].category
            
    def delete(self):
        selected = self.request.get('selected', ())
        self.context._items = tuple(
            item for i, item in enumerate(self.context._items)
            if i not in selected)
    
    def up(self):
        selected = list(self.request.get('selected', ()))
        selected.sort()
        items = list(self.context._items)
        
        for idx, i in enumerate(selected):
            i2 = i - 1
            if i2 < 0:
                i2 = len(items) - 1
            items[i2], items[i] = items[i], items[i2]
            selected[idx] = i2
            
        self.context._items = tuple(items)
        self.request['selected'] = selected
        
    def down(self):
        selected = list(self.request.get('selected', ()))
        selected.sort()
        selected.reverse()
        items = list(self.context._items)
        
        for idx, i in enumerate(selected):
            i2 = i + 1
            if i2 >= len(items):
                i2 = 0
            items[i2], items[i] = items[i], items[i2]
            selected[idx] = i2
            
        self.context._items = tuple(items)
        self.request['selected'] = selected
        
    def __call__(self):
        for button in ('add', 'save', 'delete', 'up', 'down'):
            if button in self.request:
                getattr(self, button)()
                break
        return super(ManageTakeAction, self).__call__()
