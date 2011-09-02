#!/usr/bin/env python
# -*- coding: utf-8 -*-

''' Produce print-quality TIFFs and JPGs from a directory of PDFs.

    * Works on multilayer PDFs and some types of bad vectors
    * Each page of a multipage PDF will become one TIFF
    * tif_dir must exist before running script
    * Hard-coded values for output file format and DPI
    * ImageMagic (convert) must be installed and on your system path
 
    Usage: serenifypdf <pdf_dir> <tif_dir>
'''

try:
    from argparse import ArgumentParser
except:
    print("Sorry, I couldn't find the argparse module.")
    print("Please make sure you have it installed for your version of Python.")
    exit(1) # Error 1: Couldn't find argparse

import os
import subprocess

__author__ = "Ben Rousch"
__copyright__ = "Copyright 2011, Ben Rousch"
__credits__ = ["Ben Rousch"]
__license__ = "MIT"
__version__ = "0.2"
__maintainer__ = "Ben Rousch"
__email__ = "brousch@gmail.com"
__status__ = "Development"

#TODO: Create output dir if it doesn't exist. Warn if not empty.
#TODO: Strip out potentially troublesome characters from file name: "&" ","
#TODO: Use pdftk to burst before conversion. Saves a lot of RAM.
#TODO: Option to convert PDF to B&W (fixes problems with printing colors)
#    convert -DENSITY 300 orig.pdf -colorspace Gray -threshold 99% fixed
#TODO: Option to make orientation consistent throughout document
#TODO: Command line argument for other output types (jpg, pdf)
#TODO: Command line argument for output QUALITY (1 - 100)
#TODO: Progress indicator
#TODO: Remove print statements, add logging

QUALITY = '10' # JPG quality (not currently used)
OUTPUT_FORMAT = 'tif' # TIFF is the only current conversion target

def whereis(program):
    ''' Tries to find program on the system path.

        Returns the path if it is found or None if it's not found.
    '''
    for path in os.environ.get('PATH', '').split(':'):
        if os.path.exists(os.path.join(path, program)) and \
            not os.path.isdir(os.path.join(path, program)):
            return os.path.join(path, program)
    return None

def main():
    ''' Runs the script.
    '''

    # Command line parsing
    parser = ArgumentParser(description='Produce print-quality TIFFs '+\
                                        'from a directory of PDFs')
    parser.add_argument('pdf_dir', help='Directory with PDFs to convert')
    parser.add_argument('tif_dir', help='Directory in which to store TIFFs')
    parser.add_argument('-dpi', type=int, default=300,
                        help='DPI of output TIFFs. Default: 300')
    args = parser.parse_args()

    #TODO: Verify these dirs are legit
    pdf_dir = args.pdf_dir
    tif_dir = args.tif_dir
    density = args.dpi

    # Before we get too far, let's make sure ImageMagick is installed
    im_path = whereis('convert')
    if not im_path:
        print("ImageMagic (convert) is not installed or is not on the path.")
        print("I can't do anything until it's installed and on the path.")
        exit(2) # Error 2: Couldn't find ImageMagic (convert)

    # Get the list of files to convert and start converting        
    orig_files_all = os.listdir(pdf_dir)
    had_error = False
    for fil in orig_files_all:
        if fil.lower().endswith('.pdf'):
            orig_full_path = os.path.join(pdf_dir, fil)
            print("Converting: {0}".format(orig_full_path,))
            tif_full_path = os.path.join(tif_dir, fil[:-3]+OUTPUT_FORMAT)
            ret_val = subprocess.call([im_path,
                                 '-compress', 'Group4',
                                 '-density', str(density),
                                 '-type', 'Grayscale', #1.1 min/file
                                 '-background', 'white',
                                 '-flatten',
                                 orig_full_path,
                                 tif_full_path ])
            if not ret_val:   # No return value means success
                print("Successfully converted: {0}.".format(tif_full_path,))
            else:
                had_error = True
                print("Error converting: {0}. Continuing with next file."\
                      .format(orig_full_path,))
    if not had_error:
        print("Finished all conversions without problems.")
    else:
        print("Finished conversions, but there were some problems.")

if __name__ == '__main__':
    main()

