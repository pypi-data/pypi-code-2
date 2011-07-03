"""
Draw a hex grid in a PNG image.  You'll need PIL installed.
"""

import sys
sys.path.insert(0, "..")

import Image
import ImageDraw

from hexgrid import HexGrid

def heximage(size, width, height):
    # Create the image.
    im = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(im)

    # Create a grid with the same canvas size.
    grid = HexGrid(size)

    grid.set_size(width, height)
    grid.set_margin(30)
    grid.set_cellsize(0.9)

    # Draw each cell in the image.
    for cell in grid:
        # The hex cell.
        draw.polygon(cell.outline, outline = 'black', fill = 'pink')

        # Centred text showing the cell coordinate.
        text = "%d,%d" % cell.hpos
        w, h = draw.textsize(text)

        x, y = cell.centre
        x -= w / 2
        y -= h / 2

        draw.text((x, y), text, fill = 'red')

    return im

if __name__ == "__main__":
    im = heximage(4, 600, 500)
    im.save('image.png')
