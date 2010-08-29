# Trosnoth (UberTweak Platform Game)
# Copyright (C) 2006-2009 Joshua D Bartlett
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

from framework import CompoundElement
from elements import TextElement
from trosnoth.src.gui.fonts.font import Font
from trosnoth.src.gui import colours
import pygame
from trosnoth.src.gui.common import Location, AttachedPoint, addPositions


# Styles work thusly:
# When looking for a particular attribute (say backColour),
# a cell will search first in its own style object, then in
# its row's style object, then it its column's style object,
# then in the table's. As soon as it finds a non-None value,
# it will use that.
class TableStyle(object):

    def __init__(self):
        self.backColour = None
        self.foreColour = None
        self.hasShadow = None
        self.shadowColour = None
        self.font = None
        self.padding = None
        self.textAlign = None



class StyleUser(CompoundElement):
    def __init__(self, app, style):
        super(StyleUser, self).__init__(app)
        self.style = style



class CellAggregator(StyleUser):
    def __init__(self, app, table, index):
        super(CellAggregator, self).__init__(app, TableStyle())
        self._table = table
        self._cells = []
        self.index = index
        self.elements = self._cells

    def _newCell(self, cell, index = None):
        if index is None:
            index = len(self._cells)
        assert index <= len(self._cells)
        self._cells.insert(index, cell)

    def _anotherInsertedBefore(self):
        self.index += 1

    def _anotherDeletedBefore(self):
        self.index -= 1
        assert self.index >= 0

    def _delCell(self, index):
        del self._cells[index]

    def __len__(self):
        return len(self._cells)

    def __getitem__(self, i):
        return self._cells[i]

    def styleUpdate(self):
        '''
        Informs the row or column that the style of some part of the table has
        changed.  This is provided because it is too expensive for every cell to
        check its style every draw() call, so you must manually tell the table,
        row, column or cell that the style has been updated before the update is
        reflected.
        '''
        for cell in self._cells:
            cell.styleUpdate()

class Row(CellAggregator):
    def __init__(self, app, table, index, height):
        super(Row, self).__init__(app, table, index)
        assert hasattr(height, 'getVal')
        self.setHeight(height)

    def setHeight(self, height):
        assert hasattr(height, 'getVal')
        self._height = height

    def _getHeight(self):
        return self._height.getVal(self.app)

    def _getPt(self):
        return self._table._getRowPt(self.index)

class Column(CellAggregator):
    def __init__(self, app, table, index, width):
        super(Column, self).__init__(app, table, index)
        self.setWidth(width)

    def setWidth(self, width):
        self._width = width

    def _getWidth(self):
        if hasattr(self._width, 'getVal'):
            return self._width.getVal(self.app)
        else:
            return self._width

    def _getPt(self):
        return self._table._getColPt(self.index)

class Cell(StyleUser):
    def __init__(self, app, row, column):
        super(Cell, self).__init__(app, TableStyle())
        self._row = row
        self._column = column
        textAlign = self.styleGet('textAlign')
        self.textElement = TextElement(self.app, "", self.styleGet('font'), Location(CellAttachedPoint((0,0), self, textAlign), textAlign), colour=self.styleGet('foreColour'))
        self.elements = [self.textElement]
        self._changed = True
        self._oldText = ''

    @property
    def row(self):
        return self._row.index

    @property
    def column(self):
        return self._column.index

    def styleUpdate(self):
        '''
        Informs the cell that the style of some part of the table has changed.
        This is provided because it is too expensive for every cell to check its
        style every draw() call, so you must manually tell the table, row,
        column or cell that the style has been updated before the update is
        reflected.
        '''
        self._changed = True

    def styleGet(self, field):
        toSearch = [self, self._row, self._column, self._row._table]
        for s in toSearch:
            val = getattr(s.style, field)
            if val is not None:
                return val

        return None

    def setText(self, text):
        if text != self._oldText:
            self.textElement.setText(text)
            self._changed = True
            self._oldText = text

    def _getPt(self):
        rowPt = self._row._getPt()
        colPt = self._column._getPt()
        return (colPt[0], rowPt[1])

    def _getSize(self):
        rowHeight = self._row._getHeight()
        colWidth = self._column._getWidth()
        return (colWidth, rowHeight)

    def _getRect(self):
        return pygame.Rect(self._getPt(), self._getSize())

    def _getUsableRect(self):
        pt = self._getPt()
        padding = self.styleGet('padding')
        usablePt = addPositions(pt, padding)
        size = self._getSize()
        usableSize = tuple([size[i] - padding[i]*2 for i in 0,1])
        return pygame.Rect(usablePt, usableSize)

    def draw(self, surface):
        if self._changed:
            self._changed = False
            self.textElement.setFont(self.styleGet('font'))
            self.textElement.setColour(self.styleGet('foreColour'))
            textAlign = self.styleGet('textAlign')
            self.textElement.pos.anchor = textAlign
            self.textElement.pos.point.attachedAt = textAlign
            bgColour = self.styleGet('backColour')
            if bgColour is not None:
                surface.fill(bgColour, self._getRect())
            self.textElement.setShadow(self.styleGet('hasShadow'))
            self.textElement.setShadowColour(self.styleGet('shadowColour'))

        clipRect = surface.get_clip()
        newClipRect = clipRect.clip(self._getUsableRect())
        surface.set_clip(newClipRect)
        try:
            super(Cell, self).draw(surface)
        finally:
            surface.set_clip(clipRect)


class CellAttachedPoint(AttachedPoint):
    def __init__(self, val, cell, attachedAt = 'topleft'):
        super(CellAttachedPoint, self).__init__(val, cell._getUsableRect, attachedAt)


defaultStyle = TableStyle()
defaultStyle.backColour = (255,255,255)
defaultStyle.padding = (5,5)
defaultStyle.foreColour = (0,0,0)
defaultStyle.font = Font('FreeSans.ttf', 36)
defaultStyle.textAlign = 'topleft'
defaultStyle.hasShadow = False
defaultStyle.shadowColour = colours.shadowDefault

class Value(object):
    def __init__(self, value):
        self._value = value
    def getVal(self):
        return self._value

class Table(StyleUser):
    def __init__(self, app, pos, rows=None, columns=None):
        super(Table, self).__init__(app, defaultStyle)
        self.pos = pos

        self._columns = []
        self._rows = []
        # Bind self.elements to self._rows (arbitrarily chosen,
        # rather than self._columns)
        self.elements = self._rows

        # Style Settings:
        self._borderColour = (192,192,192)
        self._borderWidth = 10
        self._defaultWidth = 200
        self._defaultHeight = Value(60)

        if rows is not None:
            self.addRows(rows)

        if columns is not None:
            self.addColumns(columns)

        self._sizes = {}
        self._appSize = None

    def styleUpdate(self):
        '''
        Informs the table that the style of some part of the table has changed.
        This is provided because it is too expensive for every cell to check its
        style every draw() call, so you must manually tell the table, row,
        column or cell that the style has been updated before the update is
        reflected.
        '''
        for row in self._rows:
            row.styleUpdate()

    def setBorderWidth(self, width):
        if width != self._borderWidth:
            self._borderWidth = width
            self._sizes = {}

    def setBorderColour(self, colour):
        self._borderColour = colour

    def addRow(self, index=None):
        if index is None:
            index = len(self._rows)
        assert index <= len(self._rows)
        # Create and Insert
        newRow = Row(self.app, self, index, self._defaultHeight)
        self._rows.insert(index, newRow)
        for x in range(0, len(self._columns)):
            newCell = Cell(self.app, newRow, self._columns[x])
            newRow._newCell(newCell, x)
            self._columns[x]._newCell(newCell, index)

        for x in range(index+1, len(self._rows)):
            self._rows[x]._anotherInsertedBefore()
        self._sizes = {}

    def addColumn(self, index = None):
        if index is None:
            index = len(self._columns)
        assert index <= len(self._columns)
        # Create and Insert
        newColumn = Column(self.app, self, index, self._defaultWidth)
        self._columns.insert(index, newColumn)
        for x in range(0, len(self._rows)):
            newCell = Cell(self.app, self._rows[x], newColumn)
            newColumn._newCell(newCell, x)
            self._rows[x]._newCell(newCell, index)

        for x in range(index+1, len(self._columns)):
            self._columns[x]._anotherInsertedBefore()
        self._sizes = {}

    def addRows(self, count, firstIndex = None):
        if count < 1:
            return

        index = firstIndex

        for i in range(count):
            self.addRow(index)
            if index is not None:
                index += 1

    def addColumns(self, count, firstIndex = None):
        if count < 1:
            return

        index = firstIndex

        for i in range(count):
            self.addColumn(index)
            if index is not None:
                index += 1


    def delRow(self, index):
        del self._rows[index]
        for col in self._columns:
            col._delCell(index)
        for x in range(index, len(self._rows)):
            self._rows[x]._anotherDeletedBefore()
        self._sizes = {}

    def delColumn(self, index):
        del self._columns[index]
        for row in self._rows:
            row._delCell(index)
        for x in range(index, len(self._columns)):
            self._columns[x]._anotherDeletedBefore()
        self._sizes = {}


    def rowCount(self):
        return len(self._rows)

    def columnCount(self):
        return len(self._columns)

    def _getRect(self):
        r = pygame.Rect((0,0), self._getSize())
        self.pos.apply(self.app, r)
        return r

    def _getPt(self):
        return self._getRect().topleft

    def _getSize(self, rowStart=0, rowEnd=None, colStart=0, colEnd=None):
        if rowEnd is None:
            rowEnd = len(self._rows)
        if colEnd is None:
            colEnd = len(self._columns)

        appSize = self.app.screenManager.size
        if appSize != self._appSize:
            self._sizes = {}
            self._appSize = appSize
        else:
            try:
                return self._sizes[rowStart, rowEnd, colStart, colEnd]
            except KeyError:
                pass

        y = self._borderWidth
        for j in range(rowStart, rowEnd):
            y += self._rows[j]._getHeight()
            y += self._borderWidth

        x = self._borderWidth
        for i in range(colStart, colEnd):
            x += self._columns[i]._getWidth()
            x += self._borderWidth

        self._sizes[rowStart, rowEnd, colStart, colEnd] = (x, y)
        return (x, y)

    def _getRowPt(self, index):
        pt = self._getPt()
        offset = self._getSize(0, index)
        return (pt[0], pt[1]+offset[1])

    def _getColPt(self, index):
        pt = self._getPt()
        offset = self._getSize(colStart=0,colEnd=index)
        return (pt[0]+offset[0], pt[1])

    def draw(self, surface):
        super(Table, self).draw(surface)
        if self._borderColour is not None:
            self._drawBorders(surface)

    def _getBorderWidth(self):
        if hasattr(self._borderWidth, 'getVal'):
            return self._borderWidth.getVal(self.app)
        else:
            return self._borderWidth

    def _drawBorders(self, surface):
        width = self._getBorderWidth()
        if width == 0:
            return
        if self.rowCount() == 0 or self.columnCount() == 0:
            return
        # Draw Horizontals:
        # Use rect filling, because drawing lines usually round the ends
        horRect = pygame.Rect((0,0), (self._getSize(rowStart=0, rowEnd=1)[0], width))
        for row in self._rows:
            horRect.bottomleft = row._getPt()
            surface.fill(self._borderColour, horRect)
        horRect.top += row._getHeight() + width
        surface.fill(self._borderColour, horRect)

        # Draw Verticals:
        # Use rect filling, because drawing lines usually round the ends
        verRect = pygame.Rect((0,0), (width, self._getSize(colStart=0, colEnd = 1)[1]))
        for col in self._columns:
            verRect.topright = col._getPt()
            surface.fill(self._borderColour, verRect)
        verRect.left += col._getWidth() + width
        surface.fill(self._borderColour, verRect)


    def __getitem__(self, index):
        return self.getColumn(index)

    def getRow(self, index):
        return self._rows[index]

    def getColumn(self, index):
        return self._columns[index]

