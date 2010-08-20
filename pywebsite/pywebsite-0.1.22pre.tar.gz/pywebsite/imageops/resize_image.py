import pygame
import sys
import os


def resize_aspect(width, height, wanted_width = None, wanted_height = None):
    """ resize_aspect(width, height, wanted_width=None, wanted_height = None)

    resizes to either the width or height, and keeps the other one with
    the given aspect ratio.

    >>> resize_aspect(100, 120, None, 60)
    (50, 60)
    >>> resize_aspect(100, 120, 200, None)
    (200, 240)
    >>> resize_aspect(100, 120, 200, 200)
    Traceback (most recent call last):
    ...
    ValueError: must give either a wanted_width or wanted_height
    """
    
    if wanted_width is None and wanted_height is None:
        raise ValueError("must give either a wanted_width or wanted_height")
    if wanted_width is not None and wanted_height is not None:
        raise ValueError("must give either a wanted_width or wanted_height")

    # get the aspect ratio of the image.
    if wanted_height is not None:
        the_width = width / (float(height)/wanted_height)
        the_height = wanted_height
    else:
        the_width = wanted_width
        the_height = height / (float(width)/wanted_width)

    return int(the_width), int(the_height)



if __name__ == "__main__":

    fin, fout, width, height = sys.argv[1:]
    #print fname, width, height
    width, height = map(int, [width, height])

    if os.path.exists(fout):
        raise "fout exists"

    surf = pygame.image.load(fin)
    sw, sh = surf.get_size()

    size = resize_aspect(sw, sh, None, height)

    new_surf = pygame.transform.smoothscale(surf, size)
    pygame.image.save(new_surf, fout)

