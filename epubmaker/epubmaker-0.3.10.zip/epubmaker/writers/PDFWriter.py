#!/usr/bin/env python
#  -*- mode: python; indent-tabs-mode: nil; -*- coding: utf-8 -*-

"""
PDFWriter.py

Copyright 2011 by Marcello Perathoner

Distributable under the GNU General Public License Version 3 or newer.

Convert RST to PDF.

"""

from __future__ import with_statement

import os
import subprocess

from epubmaker.lib.Logger import debug, info, error
from epubmaker.lib.GutenbergGlobals import SkipOutputFormat

from epubmaker import ParserFactory
from epubmaker import writers

class Writer (writers.BaseWriter):
    """ Class to write PDF. """

    def xetex (self, inputfilename, outputdir):
        """ Process thru xetex.

        """

        try:
            _xetex = subprocess.Popen ([options.config.XELATEX, 
                                        "-output-directory", outputdir,
                                        inputfilename],
                                       stdin = subprocess.PIPE, 
                                       stdout = subprocess.PIPE, 
                                       stderr = subprocess.PIPE)
        except OSError:
            error ("PDFWriter: executable not found: %s" % 'xelatex')
            raise SkipOutputFormat

        (stdout, stderr) = _xetex.communicate ()
        
        # pylint: disable=E1103
        stderr = stderr.strip ()
        if stderr:
            error ("xetex: %s" % stderr)



    def build (self):
        """ Build PDF file. """

        filename = os.path.join (self.options.outputdir, self.options.outputfile)

        info ("Creating PDF file: %s" % filename)

        parser = ParserFactory.ParserFactory.create (self.options.candidate.filename,
                                                     self.options.candidate.mediatype)
        parser.options = self.options

        if not hasattr (parser, 'rst2xetex'):
            error ('PDFWriter can only work on a RSTParser.')
            return
        
        tex = parser.rst2xetex ()
        texfilename = os.path.splitext (filename)[0] + '.tex'
        with open (texfilename, 'w') as fp:
            fp.write (tex.encode ('utf-8'))

        self.copy_aux_files (self.options.outputdir)
        
        self.xetex (texfilename, self.options.outputdir)
            
        info ("Done PDF file: %s" % filename)


