"""
Hexagonal grids.
"""

from math import radians, sin, cos
from cell import HexCell

class HexGrid(object):
    """
    A hexagonal grid.
    """

    def __init__(self, radius):
        #: Radius of the grid, in cells.
        self.radius = radius

        #: Width of the hex canvas.
        self.width = 100.0

        #: Height of the hex canvas.
        self.height = 100.0

        #: Margin between edge of canvas and the grid.
        self.margin = 10.0

        #: Relative size of hex cell (0 to 1).
        self.cellsize = 1.0

        self.cells = {}
        for hx in xrange(-radius, radius + 1):
            for hy in xrange(-radius, radius + 1):
                if self._valid(hx, hy):
                    cell = HexCell(self, hx, hy)
                    self.cells[hx, hy] = cell

        self._update()

    def set_size(self, width, height):
        "Set the grid canvas size."

        self.width = width
        self.height = height
        self._update()

    def set_margin(self, margin):
        "Set the canvas margin."

        self.margin = margin
        self._update()

    def set_cellsize(self, size):
        "Set the relative cell size."

        self.cellsize = size
        self._update()

    def scale(self, x, y):
        "Scale a canvas point."

        x = self.width / 2 + x * self._scalefactor
        y = self.height / 2 + y * self._scalefactor

        return x, y

    def _update(self):
        "Update the canvas scale factor."

        # Calculate X/Y extents.
        coords = []
        for cell in self:
            coords.extend(cell.outline_unscaled)

        x = [c[0] for c in coords]
        y = [c[1] for c in coords]

        xsize = max(x) - min(x)
        ysize = max(y) - min(y)

        # Calculate scale factor.
        xscale = (self.width - 2 * self.margin) / xsize
        yscale = (self.height - 2 * self.margin) / ysize

        self._scalefactor = min(xscale, yscale)

    def _valid(self, hx, hy):
        "Return whether a hex coordinate is valid."

        width = 2 * self.radius - abs(hx)

        if hx >= 0:
            ymax = self.radius
            ymin = ymax - width
        elif hx < 0:
            ymin = -self.radius
            ymax = ymin + width

        return ymin <= hy <= ymax

    def __getitem__(self, idx):
        return self.cells[idx]

    def __iter__(self):
        return self.cells.itervalues()

    def __repr__(self):
        return "<HexGrid: radius %d>" % self.radius
