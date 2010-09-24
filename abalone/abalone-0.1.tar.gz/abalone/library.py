#Copyright (C) 2010 Unai Zalakain De Graeve
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

'Helper classes and functions.'

from math import sqrt, cos, sin

class NoNegIndexList(list):
    '''NoNegIndexList(iter) -> list that raises IndexError on
    negative indexes.'''

    def __getitem__(self, key):
        if key < 0:
            raise IndexError
        return super(NoNegIndexList, self).__getitem__(key)

class Reductors:
    @staticmethod
    def equal(items):
        '''equal(items) -> return True if all the items are equal,
        False otherways.'''
        def equal(a, b):
            if all((a, b)) and a == b:
                return a
            return False
        return reduce(equal, items)

    @staticmethod
    def consec(items):
        '''consec(items) -> return True if items are a, a+1, a+2, ...'''
        def consec(a, b):
            if all((a, b)) and a + 1 == b:
                return b
            return False
        return reduce(consec, items)

class C(list):
    '''C(x, y) -> list with x and y attributes set to the two arguments,
    ideal for coordinates.'''
    def __init__(self, x, y):
        super(C, self).__init__((x,y))
        self.x = x
        self.y = y 

def circle(coord, diameter):
    '''circle(coordinate, diameter) -> calculate the top left
    and the bottom right coordinates of an circle.

    coordinate -> center of the circle, C instance.
    diameter -> diameter of the circle.'''

    r = diameter / 2
    a = C(coord.x - r, coord.y + r)
    b = C(coord.x + r, coord.y - r)
    return a,b

def get_coord(center, edge, pos, radian):
    '''get_coord(center, edge, pos, radian) -> get the coordinate
    of pos in an abalone table.

    center -> center of the table, C instance.
    edge -> longitude of the edges of the board.
    pos -> position, a (row, column) tuple.
    radian -> spinning radian.'''
    def pc(row, column):
        y = (row - 1)
        x = (column - 1) - y * 1/2.0
        #get the separation between column and rows
        column_sep = edge / 5.0
        row_sep = sqrt(3/4.0 * column_sep ** 2)
        return c.x + (x - 2.0) * column_sep, c.y - (y - 4.0) * row_sep

    c = center
    p = C(*pc(*pos))
    a = radian

    x = cos(a) * (p.x - c.x) - sin(a) * (p.y - c.y) + c.x
    y = sin(a) * (p.x - c.x) + cos(a) * (p.y - c.y) + c.y
    return C(x, y)
