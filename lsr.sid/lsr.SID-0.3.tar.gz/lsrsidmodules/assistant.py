#!/usr/bin/env python
# coding:utf-8

import os
import gtk
import gobject

import gtk.glade
import gettext

import helpers
helpers.translation_gettext()
import sidinfo 

BORDER_WIDTH = 20

class Assistant(gtk.Assistant):
    def __init__(self, main):
        gtk.glade.bindtextdomain("lsrsid", os.path.join(helpers.install_dir(), "locale"))
        gtk.glade.textdomain("lsrsid")        
        gettext.bindtextdomain("lsrsid", os.path.join(helpers.install_dir(), "locale"))
        gettext.textdomain("lsrsid")
        
        self.main = main
        
        gtk.Assistant.__init__(self)
        self.resize(640, 480)
        self.set_title(_("lsR SID - First Run Assistant"))
        
        self.basedir = None
        
        self.done = False
        self.cancel = False
        
        ## Intrudoction
        text = gtk.TextView()
        text.set_wrap_mode(gtk.WRAP_WORD)
        text.set_editable(False)
        text.set_cursor_visible(False)
        sw = gtk.ScrolledWindow()
        sw.add(text)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        tb = gtk.TextBuffer()
        text.set_buffer(tb)
        tb.set_text(_("""
lsR SID is a simple Frontent for sidplay2 and the High Voltage SID Collection.

The first time you use lsR SID you have to specify the localisation of the HVSC on your local disc. lsR SID will then scan the collection and create an internal database."""))
        self.append_page(sw)
        sw.set_border_width(BORDER_WIDTH)
        self.set_page_type(sw, gtk.ASSISTANT_PAGE_INTRO)
        self.set_page_title(sw, _("lsR SID - First Run"))
        self.set_page_complete(sw, True)
        
        ## SELECT FOLDER
        vbox = gtk.VBox()
        select = gtk.FileChooserWidget(action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER)
        select.connect("selection-changed", self.selection_changed_cb)
        vbox.pack_start(select, True, True)
        self.lblFolderCorrect = gtk.Label()
        self.lblFolderCorrect.set_markup(_("<span foreground='red' weight='ultrabold'>The selected folder is not a valid HVSC folder</span>"))
        vbox.pack_start(self.lblFolderCorrect, False, True)
        self.append_page(vbox)
        vbox.set_border_width(BORDER_WIDTH)
        self.set_page_type(vbox, gtk.ASSISTANT_PAGE_INTRO)
        self.set_page_title(vbox, _("Select HVSC main directory"))
        
        
        ## PROGRESS
        self.vboxProgress = gtk.VBox()
        self.progressbar = gtk.ProgressBar()
        self.lbl = gtk.Label()
        self.lbl.set_markup(_("Scanning the HVSC directory. This will take a while!"))
        self.vboxProgress.pack_start(self.lbl, False, True)
        self.vboxProgress.pack_start(self.progressbar, False, True)
        self.append_page(self.vboxProgress)
        self.vboxProgress.set_border_width(BORDER_WIDTH)
        self.set_page_type(self.vboxProgress, gtk.ASSISTANT_PAGE_PROGRESS)
        self.set_page_title(self.vboxProgress, _("Scanning directory"))
        
        lbl = gtk.Label(_("Done"))
        self.append_page(lbl)
        self.set_page_type(lbl, gtk.ASSISTANT_PAGE_SUMMARY)
        self.set_page_title(lbl, _("All done"))
        self.set_page_complete(lbl, True)
        
        self.connect('destroy', self.destroy)
        self.connect('cancel', self.destroy)
        self.connect('prepare', self.prepare)
        self.connect('close', self.close)
        
        
        self.show_all()
    def close(self, widget):
        self.done = True
        self.hide()
        self.main.gui.show()
    def destroy(self, widget):
        self.cancel = True
        #~ self.main.gui.quit()
        self.hide()
        self.main.quit()
        
        
    def prepare(self, widget, new_page):
        cur_page = self.get_current_page()

        if cur_page == 2 :## PROGRESS
            gobject.timeout_add(1000, self.timeout_cb)
        
    def timeout_cb(self):
        gtk.gdk.threads_enter()
        counter = 0
        self.main.database.drop_table_sids()
        self.main.database.create_database()
        
        songlength_db = sidinfo.SongLengthDatabase(self.basedir)
        
        results_per_round = 1000
        for sids in sidinfo.recursive_read_directory(self.basedir, songlength_db, num=results_per_round):
            self.main.database.insert_sids(sids)
            counter += results_per_round
            self.progressbar.set_fraction(counter / 40000.0 * 1.0)
            self.progressbar.set_text("{0} from approximately 40000 sids processed".format(counter))
            while gtk.events_pending():
                gtk.main_iteration()
        self.progressbar.set_fraction(1.0)
        self.progressbar.set_text(_("Done"))
        self.set_page_complete(self.vboxProgress, True)
        self.main.database.create_index()
        while gtk.events_pending():
            gtk.main_iteration()
        gtk.gdk.threads_leave()
        return False
            
        
    def selection_changed_cb(self, widget):
        folder = widget.get_filename()
        files = os.listdir(folder)
        if "DEMOS" in files and "GAMES" in files and "MUSICIANS" in files:
            self.set_page_complete(widget.get_parent(), True)
            self.lblFolderCorrect.set_markup(_("<span foreground='green' weight='ultrabold'>The selected folder is a valid HVSC folder</span>"))
            self.basedir = folder
            self.main.basedir = folder
        else:
            self.lblFolderCorrect.set_markup(_("<span foreground='red' weight='ultrabold'>The selected folder is not a valid HVSC folder</span>"))
            self.basedir = None
            self.set_page_complete(widget.get_parent(), False)
