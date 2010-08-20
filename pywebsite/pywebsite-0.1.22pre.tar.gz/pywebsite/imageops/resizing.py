##    pywebsite - Python Website Library
##    Copyright (C) 2009, 2010 Rene Dudfield
##
##    This library is free software; you can redistribute it and/or
##    modify it under the terms of the GNU Library General Public
##    License as published by the Free Software Foundation; either
##    version 2 of the License, or (at your option) any later version.
##
##    This library is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
##    Library General Public License for more details.
##
##    You should have received a copy of the GNU Library General Public
##    License along with this library; if not, write to the Free
##    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
##
##    Rene Dudfield
##    renesd@gmail.com
"""

purpose:
    Resizing things in different useful ways.
"""



def resize_percent(width, height, percent_width, percent_height):
    """ resize_percent(width, height, percent_width, percent_height)
        Returns a (width, height) scaled by the percentages given.
    >>> resize_percent(100, 100, 50, 50)
    (50, 50)
 
    >>> sizes = ((100, 100, 50, 50), (100, 100, 200, 50), 
    ...          (100, 100, 200, 0))
    >>> for s in sizes:
    ...     print (resize_percent(*s))
    (50, 50)
    (200, 50)
    (200, 0)
    """
    return int((percent_width*width)/100), int((percent_height*height)/100)

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




def resize_ratio(width, height, ratio_width, ratio_height):
    """ resize_ratio(width, height, 
                     ratio_width, ratio_height) -> (width, height)

    resize with values 0..1.  Where 0. is 0% and 1.0 is 100%.

    >>> resize_ratio(100, 100, 0.5, 0.5)
    (50, 50)
    >>> resize_ratio(100, 100, 1.0, 1.0)
    (100, 100)
    >>> resize_ratio(100, 100, 2.0, 2.0)
    (200, 200)
    """
    return int(ratio_width*width), int(ratio_height*height)



def resize_crop():
    """
    resize to the given size keeping aspect ratio, 
        but crop off either the top/bottom or sides.

    So say you need exactly 64x64 image, you can resize but 
    chop off the bottom and top.
    """
    raise NotImplementedError()



if __name__ == "__main__":
    
    
    import doctest, sys
    if "test" in sys.argv:
        doctest.testmod() 
    
    

