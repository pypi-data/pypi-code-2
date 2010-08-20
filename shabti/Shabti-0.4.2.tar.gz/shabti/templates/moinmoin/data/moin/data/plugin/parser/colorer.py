"""
    MoinMoin - parser for Syntax Highlighting using the 
    http://colorer.sf.net
    by
    belugin@mail.ru

    based on
    
    MoinMoin - Processor for Syntax Highlighting using the enscript

    Copyright (c) 2002 by Won-Kyu Park <wkpark@kldp.org>
    All rights reserved, see COPYING for details.

    $Id$

    Usage:
    {{{#!colorer sql
       select * from testTable where a='test string'
    }}}
"""
import os,re,string,sys,popen2
Dependencies = ["time"]

class Parser:
    def __init__(self, raw, request, **kw):
        # save call arguments for later use in format
        self.raw = raw
        self.request = request
        self.kw= kw

    def format(self, formatter):
    	#type to pass to colorer
        type=string.strip(self.kw['format_args'])
        options='-c /usr/local/colorer/catalog.xml -dh -h -t%s' % type
        cmd = '/usr/local/bin/colorer ' + options          	        
        try:
            fromchild, tochild = popen2.popen4(cmd)
            tochild.write(self.raw)
            tochild.flush()
            tochild.close()
            fromchild.flush()
            html = fromchild.readlines()
        finally:
            fromchild.close()

        html=html[2:-4]
        html='<PRE>'+string.join(html, '')+'</PRE>'

        self.request.write(formatter.rawHTML(html))
