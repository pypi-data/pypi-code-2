"""
Hexagonal grid cells.
"""

from math import radians, sin, cos

class HexCell(object):
    """
    A single hex cell.
    """

    def __init__(self, grid, hx, hy):
        #: Parent grid.
        self.grid = grid

        #: Hex coordinate.
        self.hpos = (hx, hy)

    @property
    def centre(self):
        "Return scaled centre coordinate of the cell."

        x, y = self.centre_unscaled
        return self.grid.scale(x, y)

    @property
    def centre_unscaled(self):
        "Return unscaled centre coordinate of the cell."

        hx, hy = self.hpos
        angle = radians(60)
        x = hx + cos(angle) * (hy - hx)
        y = sin(angle) * (hy - hx)

        return x, y

    @property
    def outline(self):
        "Return the scaled outline coordinates of the cell."

        coords = []
        for x, y in self.outline_unscaled:
            coords.append(self.grid.scale(x, y))

        return coords

    @property
    def outline_unscaled(self):
        "Return the unscaled outline coordinates of the cell."

        xc, yc = self.centre_unscaled
        dist = self.grid.cellsize * 0.5 / cos(radians(30))
        coords = []

        for angle in xrange(30, 360, 60):
            a = radians(angle)
            x = xc + dist * cos(a)
            y = yc + dist * sin(a)
            coords.append((x, y))

        return coords

    def distance(self, other):
        "Return hex distance twixt this cell and another."

        a = self.hpos
        b = other.hpos

        dx = b[0] - a[0]
        dy = b[1] - a[1]

        return (abs(dx) + abs(dy) + abs(dx - dy)) / 2

    def __cmp__(self, other):
        return cmp(self.hpos, other.hpos)

    def __repr__(self):
        return "<HexCell: %s>" % str(self.hpos)
