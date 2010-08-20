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
    Doing operations on images in a caching manner.
    Scaling, rotation, text overlays, watermarking etc.

eg, 
gallery=mypics&image=image001.jpg&rotate=90
gallery=mypics&image=image001.jpg&width=10&height=10


gallery
image
width
height
rotate



check for ok extensions, ie jpg, png etc.  Not .php or other executable files.

TODO: 
    - make imagemagick backend.

"""

import os, stat
import pygame

from . import resizing

# 64MiB
MAX_CACHE_DIR = 64 * (1024*1024)

class ImageOps(object):
    def __init__(self, 
                 cache_dir, 
                 path_to_galleries, 
                 cache_max_size = MAX_CACHE_DIR, 
                 max_image_size = (4096,4096)):
        """ 
            cache_dir - directory to store the cached images.
            cache_max_size - maximum size of the cache files in bytes.
            path_to_galleries - path to a directory of galleries.
            max_image_size - maximum size the cached images can be.
        """
        self.cache_dir = cache_dir
        self.path_to_galleries = path_to_galleries 
        self.cache_max_size = cache_max_size
        self.max_image_size = max_image_size

        # make sure the paths validate ok.  
        #       are they there?  are they writable?
        if not os.path.exists(cache_dir):
            raise ValueError("cache_dir :%s: does not exist" % cache_dir)
        #TODO: check if the cache dir is writable?  If not warning.
        
        if not os.path.exists(path_to_galleries):
            raise ValueError(("path_to_galleries :%s: does not exist" % 
                              path_to_galleries))



    def check_valid_paths(self, path_parts):
        ''' see if each part of the path is a safe, and valid path.
        '''
        if [p for p in path_parts if ".." in p]:
            return False
        if [p for p in path_parts if p.startswith('/')]:
            return False

        return True


    def check_size(self, width, height):
        '''
        '''
        mw, mh = self.max_image_size
        if width > mw or height > mh:
            return False

        return True



    def get_cached_fname(self, 
                         gallery,
                         image,
                         width,
                         height,
                         rotate = False):
        """
        """
        #"400x400-gallery-rotate-image.jpg"
        fmt = "%sx%s-%s-%s-%s"
        args = (width, height, gallery, rotate, image)
        fname = os.path.join(self.cache_dir, fmt % args)
        return fname


    def check_cached_fname(self, orig_fname, cached_fname):
        ''' returns False if cached file is not valid.
        '''
        if not os.path.exists(cached_fname):
            return False
        cached_time = os.stat(cached_fname)[stat.ST_MTIME]
        orig_time = os.stat(orig_fname)[stat.ST_MTIME]

        if cached_time < orig_time:
            # cached file is older than original file.
            return False

        return True

    def get_image_path(self, gallery, image):
        return os.path.join(self.path_to_galleries, gallery, image)

    def resize(self, 
               gallery,
               image,
               width,
               height,
               rotate = False,
               exact_width = True,
               exact_height = True,
              ):
        """ resize the image.  Return the path of the resized image.

        gallery:      gallery in which the image is kept.
        image:        file name of the image.
        width:        wanted width to resize to.
        height:       wanted height to resize to.
        exact_width:  keep the exact width we ask for.  Otherwise use one 
                      based on the correct size from the heights aspect ratio.
        exact_height: keep the exact hight we ask for.  Otherwise use one 
                      based on the correct size from the widths aspect ratio.
        """
        width, height = int(width), int(height)

        if not self.check_valid_paths([image,gallery]):
            raise ValueError('invalid path')

        # generate the path.
        path = self.get_image_path(gallery, image)

        if not os.path.exists(path):
            raise IOError(2, "No such file or directory: '%s'" % path)

        if not self.check_size(width, height):
            raise ValueError('invalid image size')

        #print ("rotate:%s:" % rotate)
        if rotate in [0,False,'', '0']:
            rotate_float = False
        else:
            if type(rotate) != float:
                try:
                    if len(rotate) > 32:
                        raise ValueError("invalid rotate")
                except TypeError:
                        raise ValueError("invalid rotate")
                rotate_float = float(rotate)
            else:
                rotate_float = rotate

            if rotate_float < 0 or rotate_float > 360.0:
                raise ValueError('invalid rotation.  Must be between 0-360.')




        # if the cached file is already there, then we return it.
        cached_fname = self.get_cached_fname(gallery, image, width, height, 
                                             rotate_float)

        #TODO: check if it is a valid unix file name.
        
        
        # see if there is a valid cached version already there.
        if self.check_cached_fname(path, cached_fname):
            return cached_fname
        
        #TODO: check image size before loading it.
        if rotate_float is not False:
            raise NotImplementedError('rotate not implemented')
        else:
            surf = pygame.image.load(path)

            # do we keep the aspect ratio or not?
            if not exact_width or not exact_height:
                sw, sh = surf.get_size()
                if exact_width:
                    size = resizing.resize_aspect(sw, sh, width)
                else:
                    size = resizing.resize_aspect(sw, sh, None, height)
                awidth, aheight = size
            else:
                awidth, aheight = width, height

            print (awidth, aheight)
            try:
                transformed_surf = pygame.transform.smoothscale(surf, 
                                                            (awidth, aheight))
            except ValueError: 
                transformed_surf = pygame.transform.scale(surf, 
                                                            (awidth, aheight))

        # TODO: save to a temporary file in the same directory, then move.
        pygame.image.save(transformed_surf, cached_fname)
        
        return cached_fname

