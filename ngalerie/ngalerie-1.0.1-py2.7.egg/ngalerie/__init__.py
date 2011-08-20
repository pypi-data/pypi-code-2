#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (C) 2008-2011 Rémy HUBSCHER <natim@users.sf.net> 
#               http://www.trunat.fr/portfolio/python.html

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

# Using :
# - Python Imaging Library PIL http://www.pythonware.com/products/pil/index.htm
# - pyexiv2                    http://tilloy.net/dev/pyexiv2/

"""
This command has the following behaviour

"""
__version__ = '1.0.1'

import argparse
import os
import sys
import errno
import glob

try:
    import Image
except ImportError:
    print ("To use this program, you need to install Python Imaging Library"
           "- http://www.pythonware.com/products/pil/")
    sys.exit(1)

try:
    import pyexiv2
except ImportError:
    print ("To use this program, you need to install pyexiv2"
           "- http://tilloy.net/dev/pyexiv2/")
    sys.exit(1)

############# DEFAULT Configuration ##############
_SIZE_MINI = 200
_SIZE_MAXI = 600

_MINI_DIRNAME = None
_MAXI_DIRNAME = ''

# Information about the Photograph should be in ASCII
_COPYRIGHT = "Remy Hubscher - http://www.trunat.fr/"
_ARTIST = "Remy Hubscher"
##########################################

def list_jpeg(directory):
    "Return a list of the JPEG files in the directory"
    file_list = []
    for ext in ('jpg', 'JPG'):
        file_list += glob.glob(os.path.join(directory, '*.'+ext))
    return [os.path.basename(f) for f in file_list]

def _mkdir(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST:
            pass
        else: raise

def main():

    parser = argparse.ArgumentParser(description="A command interface to manage CAMERA JPG files",
                                     prog='NGalerie')

    parser.add_argument(dest='indir', nargs='?', help="Path where to find the raw pictures")
    parser.add_argument(dest='outdir', nargs='?', help="Path where to put generated pictures")

    parser.add_argument('-r', '--rename', dest='rename', action='store_true',
                        help='Use EXIF.Image.DateTime information to rename the picture')

    parser.add_argument('--resize', dest='resize', default=None, type=int,
                        help="Ask to resize pictures eventually set the size")
    parser.add_argument('-t', '--rotate', dest='rotate', action='store_true',
                        help='Ask to force rotate the picture using EXIF information')
    parser.add_argument('--max-dir', dest='max_dir', default=_MAXI_DIRNAME,
                        help="The prefix directory for resized files")
    parser.add_argument('--thumb-dir', dest='thumb_dir', default=_MINI_DIRNAME,
                        help="The prefix directory for thumbnails")
    parser.add_argument('--thumb-size', dest='thumb_size', default=_SIZE_MINI, type=int,
                        help="The size for thumbnails if thumb-dir only works with --resize")
    parser.add_argument('--artist', dest='artist', default=_ARTIST,
                        help="Name of the artist")
    parser.add_argument('--copyright', dest='copyright', default=_COPYRIGHT,
                        help="Copyright of the pictures")
    parser.add_argument('--version', action='version', version=__version__,
            help='Print the NGalerie version and exit')
    

    args = parser.parse_args()

    if not args.indir or not args.outdir:
        print parser.print_help()
        return 1

    max_size = _SIZE_MAXI if args.resize is None else args.resize

    max_dir = os.path.join(args.outdir, args.max_dir)
    thumb_dir = os.path.join(args.outdir, args.thumb_dir) if args.thumb_dir else None

    print max_dir, thumb_dir if thumb_dir else ''

    _mkdir(max_dir)
    if thumb_dir is not None:
        _mkdir(thumb_dir)

    for infile in list_jpeg(args.indir):
        if thumb_dir is not None:
            mini  = os.path.join(thumb_dir, infile)
        grand = os.path.join(max_dir, infile)
        file_path = os.path.join(args.indir, infile).decode('utf-8')

        metadata = pyexiv2.ImageMetadata(file_path)
        metadata.read()

        metadata['Exif.Image.Artist'] = args.artist
        metadata['Exif.Image.Copyright'] = args.copyright

        if thumb_dir:
            mini  = os.path.join(thumb_dir, infile)
        grand = os.path.join(max_dir, infile)

        if args.rename:
            key = 'Exif.Image.DateTime'
            # We look for a meanful name
            if 'Exif.Photo.DateTimeOriginal' in metadata.exif_keys:
                key = 'Exif.Photo.DateTimeOriginal'
            
            if key in metadata.exif_keys:
                filename = metadata[key].value\
                    .strftime('%Y-%m-%d_%H-%M-%S.jpg')
            
                if thumb_dir:
                    mini  = os.path.join(thumb_dir, filename)
                grand = os.path.join(max_dir, filename)
                counter = 0
                while os.path.isfile(grand):
                    # Il se peut qu'on prenne plusieurs photos à la même seconde ...
                    counter += 1
                    filename = metadata[key].value\
                        .strftime('%Y-%m-%d_%H-%M-%S')+'_%d.jpg' % counter
                    if thumb_dir is not None:
                        mini  = os.path.join(thumb_dir, filename)
                    grand = os.path.join(max_dir, filename)

        # We create the thumbnail
        im = Image.open(file_path)
        if args.resize:
            size = (max_size, max_size)
            im.thumbnail(size, Image.ANTIALIAS)

        # We rotate regarding to the EXIF orientation information
        if 'Exif.Image.Orientation' in metadata.exif_keys and args.rotate:
            orientation = metadata['Exif.Image.Orientation']
            if orientation == 2:
                # Vertical Mirror
                mirror = im.transpose(Image.FLIP_LEFT_RIGHT)
            elif orientation == 3:
                # Rotation 180°
                mirror = im.transpose(Image.ROTATE_180)
            elif orientation == 4:
                # Horizontal Mirror
                mirror = im.transpose(Image.FLIP_TOP_BOTTOM)
            elif orientation == 5:
                # Horizontal Mirror + Rotation 270°
                mirror = im.transpose(Image.FLIP_TOP_BOTTOM)\
                           .transpose(Image.ROTATE_270)
            elif orientation == 6:
                # Rotation 270°
                mirror = im.transpose(Image.ROTATE_270)
            elif orientation == 7:
                # Vertical Mirror + Rotation 270°
                mirror = im.transpose(Image.FLIP_LEFT_RIGHT)\
                           .transpose(Image.ROTATE_270)
            elif orientation == 8:
                # Rotation 90°
                mirror = im.transpose(Image.ROTATE_90)
            else:
                # Nothing
                mirror = im.copy()
        
            # No more Orientation information
            metadata['Exif.Image.Orientation'] = 1
        else:
            # No EXIF information, the user has to do it
            mirror = im.copy()
        
        mirror.save(grand, "JPEG", quality=85)
        
        img_grand = pyexiv2.ImageMetadata(grand)
        img_grand.read()
        metadata.copy(img_grand)
        img_grand.write()
        print grand
        
        if thumb_dir:
            size = (args.thumb_size, args.thumb_size)
            mirror.thumbnail(size, Image.ANTIALIAS)
            mirror.save(mini, "JPEG", quality=85)
            print mini
            print

    return 0

if __name__ == '__main__':
    sys.exit(main())
