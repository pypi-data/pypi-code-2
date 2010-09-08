#!/usr/bin/env python
# -*- coding: utf-8 -*-   -*- mode: python -*-

"""
opens the demo console or directly an example defined by its number:

./demo.py 25
./demo.py -N 40b

usage: %prog [opts] ex_number
   -N, --no-gtk-debug: gtk debug
   -g, --gtk: gtk debug in window
   -t, --test: run all snippets and run t.reload() for each of them
   -o, --offset=n: skip the first 'n' snippets
   -n, --number=l: stop after 'n' snippets
   -r, --reload: reload all snippets (some will stop for confirmation)
   -e, --exit: exit on exception
"""


import gtk
import sys
import os
import gobject

pdir = os.path.dirname(os.getcwd())
ppdir = os.path.dirname(pdir)
sys.path.insert(0,pdir)    
sys.path.insert(0,ppdir)    

from sqlkit.misc import optionparse
opts, args = optionparse.parse(__doc__)

if opts.gtk:
    from sqlkit import debug as dbg
    dbg.debug(True)
    dbg.debug(True, gtk=True)
    dbg.trace_class(ok='SqlTable|SqlWidget|SqlMask|Completion')
    but = 'set_fkey_descr|(lookup|get)_value' + \
        '|lookup_value|is_fkey'
    dbg.trace_function(exclude=but)

from demo_tour import Demo
import sqlkit
from sqlkit.widgets import SqlMask, SqlTable
from sqlkit.db import proxy, defaults, utils
import model

class DemoSql(Demo):
    def load_module(self, demo):
        ### fill text: src, notes, and xml
        self.insert_source(demo.body, self.src)
        self.note.set_text(demo.doc)

        ### exec the example
        GLOB = {
            'sqlkit': sqlkit,
            'SqlMask': SqlMask,
            'SqlTable': SqlTable,
            'gtk': gtk,
            'db': model.db,
            'model': model,

            }
        execfile(demo.filename, GLOB)
        self.last_lo = GLOB['t'].lay_obj
        self.last_w  = GLOB['t'].widgets
        self.t = GLOB['t']
        try:
            self.t1 = GLOB['t1']
        except:
            pass
            

        #self.xml.set_text(GLOB['l'].xml())
        self.create_widget_tree(toplevel=GLOB['t'].widgets['Window'])
        self.prepare_treestore_for_elements(GLOB['t'].lay_obj.elements)
        GLOB['t'].widgets['Window'].set_title(demo.filename)
        self.w['Window'].set_title("Example: %s" % (demo.filename))

        while gtk.events_pending():
            gtk.main_iteration()

        return GLOB['t']

d = DemoSql(xml=False, debug=True)

if args:
    d.iconify()
    d.load_module_by_idx(args[0])
    def quit(widget):
        gtk.main_quit()

    try:
        d.t.connect('delete-event', quit)
    except AttributeError:
        print "No such example ", args[0]
        sys.exit(1)

if opts.gtk:
    l =d.execute_clicked_cb(None)
#    gobject.idle_add(l.model_clear, None)

if opts.test:
    start = opts.offset and int(opts.offset) or 0
    stop = opts.number and start + int(opts.number) or None
    print start, ':', stop
    for demo in d.demos[start:stop]:
        print "------------------ %s %s --------------" % (d.demos.index(demo), demo)
        try:
            t = d.load_module(demo)
            if opts.reload:
                t.reload()
        except Exception, e:
            print e
            if opts.exit:
                sys.exit(1)
        
if __name__ == '__main__':
    gtk.main()

