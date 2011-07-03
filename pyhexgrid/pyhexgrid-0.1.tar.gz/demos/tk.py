"""
Draw a hex grid in a Tk canvas.
"""

import sys
sys.path.insert(0, "..")

import Tkinter as Tk

from hexgrid import HexGrid

class HexCanvas(Tk.Canvas):
    def __init__(self, parent, gridsize, *args, **kw):
        Tk.Canvas.__init__(self, parent, *args, **kw)
        self.grid = HexGrid(gridsize)
        self.bind('<Configure>', self.draw)

    def draw(self, event = None):
        self.delete("cell")

        width = float(self.winfo_width())
        height = float(self.winfo_height())

        self.grid.set_size(width, height)
        self.grid.set_margin(min(width, height) / 10.0)
        self.grid.set_cellsize(0.9)

        for cell in self.grid:
            item = self.create_polygon(*cell.outline,
                                       outline = "black", fill = "red")

        self.addtag_all("cell")

if __name__ == "__main__":
    root = Tk.Tk()
    root.title("HexGrid demo")

    frame = Tk.Frame(root)
    frame.pack(expand = True, fill = 'both')

    canvas = HexCanvas(frame, 5, relief = Tk.SUNKEN, borderwidth = 2)
    canvas.pack(expand = True, fill = 'both')

    root.mainloop()
