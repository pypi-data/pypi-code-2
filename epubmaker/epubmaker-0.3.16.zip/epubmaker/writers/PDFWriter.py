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

from epubmaker.lib.Logger import debug, info, warn, error
from epubmaker.lib.GutenbergGlobals import SkipOutputFormat

from epubmaker import ParserFactory
from epubmaker import writers

class Writer (writers.BaseWriter):
    """ Class to write PDF. """

    def build (self):
        """ Build PDF file. """

        inputfilename  = self.options.candidate.filename # self.ibiblio_local_file ()
        outputfilename = os.path.join (self.options.outputdir, self.options.outputfile)

        debug ("Inputfile: %s" % inputfilename)
        info ("Creating PDF file: %s" % outputfilename)

        parser = ParserFactory.ParserFactory.create (inputfilename,
                                                     self.options.candidate.mediatype)
        parser.options = self.options

        if not hasattr (parser, 'rst2xetex'):
            error ('PDFWriter can only work on a RSTParser.')
            return
        
        # Brain-dead xetex doesn't understand unix pipes
        # so we have to write a temp file
        
        texfilename = os.path.splitext (outputfilename)[0] + '.tex'
        auxfilename = os.path.splitext (outputfilename)[0] + '.aux'
        logfilename = os.path.splitext (outputfilename)[0] + '.log'

        try:
            os.remove (auxfilename)
        except OSError:
            pass
        
        tex = parser.rst2xetex ()
        with open (texfilename, 'w') as fp:
            fp.write (tex.encode ('utf-8'))

        # rst2xetex now fixes the image filenames, so we don't need to copy
        # self.copy_aux_files (self.options.outputdir)
        
        try:
            _xetex = subprocess.Popen ([options.config.XELATEX,
                                        "-output-directory", self.options.outputdir,
                                        "-interaction", "nonstopmode",
                                        texfilename],
                                       stdin = subprocess.PIPE, 
                                       stdout = subprocess.PIPE, 
                                       stderr = subprocess.PIPE)
        except OSError, what:
            error ("PDFWriter: %s %s" % (options.config.XELATEX, what))
            raise SkipOutputFormat

        (dummy_stdout, dummy_stderr) = _xetex.communicate ()
        
        with open (logfilename) as fp:
            for line in fp:
                line = line.strip ()
                if line.find ('Error') > -1:
                    error ("xetex: %s" % line)
                if line.find ('Warning') > -1:
                    warn ("xetex: %s" % line)

        info ("Done PDF file: %s" % outputfilename)


