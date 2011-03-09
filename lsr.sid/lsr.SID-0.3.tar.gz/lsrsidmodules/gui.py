#!/usr/bin/env python
# coding:utf-8

# lsrSID - Python HVSC browser and sidplay2 GUI.
# Copyright (C) 2010  Daniel Nögel
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import sys
import os
import cgi
import gtk
import glib
import pickle
import gobject
import logging
import gtk.glade
import gettext
import random
import string

import starscale
import sidinfo
import exceptions
import playlist
import helpers
helpers.translation_gettext()
import lsrsidmodules
import assistant 
import constants
(
 COLUMN_INDICATOR,
 COLUMN_ARTIST,
 COLUMN_TITLE,
 COLUMN_LENGTH,
 COLUMN_COPYRIGHT,
 COLUMN_SONG,
 COLUMN_RATING,
 COLUMN_PLAYCOUNTER,
 COLUMN_NUM_SONGS,
 COLUMN_PATH,
 COLUMN_HASH,
 
) = range(11)

(
 COLUMN_DIRNAME,
 COLUMN_DIRPATH,
) = range(2)

(
 COLUMN_SEARCH_ARTIST,
 COLUMN_SEARCH_TITLE,
 COLUMN_SEARCH_PATH,
) = range(3)

(
 COLUMN_ARTISTS_ARTIST,
 COLUMN_ARTISTS_TRACK,
 COLUMN_ARTISTS_LENGTH,
 COLUMN_ARTISTS_PATH,
) = range(4)

(
 COLUMN_DATE_DATE,
 COLUMN_DATE_ARTIST,
 COLUMN_DATE_TRACK,
 COLUMN_DATE_LENGTH,
 COLUMN_DATE_PATH,
) = range(5)

class GUI(object):
    
    def __init__(self, main):
        self.main = main
        
        
        gtk.glade.bindtextdomain("lsrsid", os.path.join(helpers.install_dir(), "locale"))
        gtk.glade.textdomain("lsrsid")        
        gettext.bindtextdomain("lsrsid", os.path.join(helpers.install_dir(), "locale"))
        gettext.textdomain("lsrsid")
        
        self.now_playing_iter = None
        
        self.glade = gtk.glade.XML(os.path.join(helpers.install_dir(), "glade", "window.glade"))
        
        self.window = self.glade.get_widget('window1')
        self.window.set_icon_from_file(os.path.join(helpers.install_dir(), "images", "audio_icon.png"))
        self.window.set_title("{0} - {1}".format(lsrsidmodules.__TITLE__, lsrsidmodules.__VERSION__))
    
                
        ## Menu shorter/longer
        self.mnuShorter = self.glade.get_widget("mnuShorter")
        self.mnuLonger = self.glade.get_widget("mnuLonger")
        mnu = gtk.Menu()
        for i in xrange(180, 0, -10):
            mnuitem = gtk.MenuItem(_("… {secs} seconds".format(secs=i)))
            mnuitem.connect("activate", self.mnu_shorter_activate_cb, i)
            mnu.append(mnuitem)
        self.mnuShorter.set_submenu(mnu)
        mnu = gtk.Menu()
        counter = 0
        row = 0
        column = 0
        for counter, i in enumerate(xrange(10, 370, 10)):
            mnuitem = gtk.MenuItem(_("… {secs} seconds".format(secs=i)))
            mnuitem.connect("activate", self.mnu_longer_activate_cb, i)
            #~ mnu.append(mnuitem)
            mnu.attach(mnuitem, column, column+1, row, row+1)
            if counter in [9, 19, 29]:
                column += 1
                row = -1
            row += 1
        self.mnuLonger.set_submenu(mnu)
            
        #~ print self.glade.get_widget("statusbar1").pack_start(gtk.Frame("Test"))
        ## Rate
        rate = self.glade.get_widget("tbRate")
        rate.set_expand(False)
        self.starscale = starscale.StarScale(10,overlap=True)
        #~ rate.add(self.starscale)
        #~ self.glade.get_widget("vboxRate").pack_start(gtk.Label(""), False, False)
        self.glade.get_widget("vboxRate").pack_start(self.starscale, False, True)
        #~ self.glade.get_widget("vboxRate").pack_start(gtk.Label(""), False, False)
        self.starscale.connect("rating-changed", self.starscale_rating_changed_db)
        
        
        ## tbShuffle
        w, h = gtk.icon_size_lookup(self.glade.get_widget("toolbar1").get_icon_size())
        self.tbShuffle = self.glade.get_widget("tbShuffle")
        img = gtk.Image()
        pb = gtk.gdk.pixbuf_new_from_file_at_size(os.path.join(helpers.install_dir(), "images", "badaman_dice.png"), w, h)
        img.set_from_pixbuf(pb)
        self.tbShuffle.set_icon_widget(img)
        
        ## HScale
        self.scale = self.glade.get_widget("hscale1")
        self.scale.set_update_policy(gtk.UPDATE_CONTINUOUS)
        
        ## Expander
        #~ self.glade.get_widget('tbExpand').set_expand(True)
        #~ self.glade.get_widget('tbExpand2').hide()
        #~ self.glade.get_widget('tbSlider').set_expand(True)
        
        ## Time
        #~ self.lblTime = self.glade.get_widget('lblTime')
        
        ##Search
        self.tvsearch = gtk.TreeView()
        self.tvsearch.connect("row_activated", self.tvsearch_rowactivated_cb)
        self.tvsearch.enable_model_drag_source(gtk.gdk.BUTTON1_MASK, [('text/plain', 0, 0)], gtk.gdk.ACTION_COPY)
        self.tvsearch.connect("drag-data-get", self.tvsearch_drag_data_get)
        
        ## Artist
        self.tvartists = gtk.TreeView()
        self.tvartists.connect("row_activated", self.tvartists_rowactivated_cb)
        self.tvartists.connect("row-expanded", self.tvartists_row_expanded_cb)
        self.tvartists.enable_model_drag_source(gtk.gdk.BUTTON1_MASK, [('text/plain', 0, 0)], gtk.gdk.ACTION_COPY)
        self.tvartists.connect("drag-data-get", self.tvartists_drag_data_get)
        
        ## Date
        self.tvdate = gtk.TreeView()
        self.tvdate.connect("row_activated", self.tvdate_rowactivated_cb)
        self.tvdate.connect("row-expanded", self.tvdate_row_expanded_cb)
        self.tvdate.enable_model_drag_source(gtk.gdk.BUTTON1_MASK, [('text/plain', 0, 0)], gtk.gdk.ACTION_COPY)
        self.tvdate.connect("drag-data-get", self.tvdate_drag_data_get)
        
        ## Playlist
        self.tvplaylist = gtk.TreeView()
        #~ self.tvplaylist.set_fixed_height_mode(40)
        self.tvplaylist.connect("row_activated", self.tvplaylist_rowactivated_cb)
        self.tvplaylist.enable_model_drag_dest([('text/plain', 0, 0)], gtk.gdk.ACTION_COPY)
        self.tvplaylist.connect("drag-data-received", self.tvplaylist_drag_data_received)
        #~ self.tvplaylist.set_search_column(COLUMN_PATH)
        self.tvplaylist.set_search_equal_func(self.search_tvplaylist, self.tvplaylist)
        
        ## Directories
        self.tvdirectories = gtk.TreeView()
        self.tvdirectories.connect("row-expanded", self.tvdirectories_row_expanded_cb)
        self.tvdirectories.connect("drag-data-get", self.tvdirectories_drag_data_get)
        self.tvdirectories.enable_model_drag_source(gtk.gdk.BUTTON1_MASK, [('text/plain', 0, 0)], gtk.gdk.ACTION_COPY)
        self.tvdirectories.set_search_equal_func(self.search_tvdirectories, self.tvplaylist)
        
        scrolledwindow = self.glade.get_widget('scrolledwindow1')
        scrolledwindow.add(self.tvplaylist)
        scrolledwindow = self.glade.get_widget('scrolledwindow2')
        scrolledwindow.set_size_request(200, -1)
        scrolledwindow.add(self.tvdirectories)
        scrolledwindow = self.glade.get_widget('swSearch')
        scrolledwindow.add(self.tvsearch)
        scrolledwindow = self.glade.get_widget('swArtists')
        scrolledwindow.add(self.tvartists)
        scrolledwindow = self.glade.get_widget('scrolledwindow5')
        scrolledwindow.add(self.tvdate)
        
        self.setup_playlist_treeview(self.tvplaylist)
        self.setup_search_treeview(self.tvsearch)
        self.setup_artists_treeview(self.tvartists)
        self.setup_date_treeview(self.tvdate)
        
        self.main.events.connect_event("now-playing", self.now_playing_cb)
        self.main.events.connect_event("track-over", self.track_over_cb)
        self.main.events.connect_event("playback-stopped", self.playback_stopped_cb)
        
        self.glade.signal_autoconnect(self)
        
        gobject.timeout_add(1000, self.timeout_cb)
    
    def show(self):
        self.window.show_all()
        self.scale.hide()
        self.starscale.hide()
    
    def show_status_message(self, message):
        statusbar = self.glade.get_widget("statusbar2")
        

        cid = statusbar.get_context_id("message")        
        statusbar.push(cid, message)
    
    def show_stats(self):
        statusbar1 = self.glade.get_widget("statusbar1")
        
       
        artists = len(self.main.database.get_artists())
        songs = self.main.database.get_number_of_songs()

        cid = statusbar1.get_context_id("stats")        
        statusbar1.push(cid, "{0} artists, {1} songs".format(artists,songs))
    
    def show_playlist_length(self):
        model = self.tvplaylist.get_model()
        statusbar = self.glade.get_widget("statusbar3")
        
       
        number_of_songs = model.iter_n_children(None)

        cid = statusbar.get_context_id("songs")        
        statusbar.push(cid, "{0} songs in playlist".format(number_of_songs))
    
    def select_hvsc_folder(self):
        chooser = gtk.FileChooserDialog(title="Select hvsc folder", 
        action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER ,
        buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK) 
        )
        ret = chooser.run()
        if ret == gtk.RESPONSE_OK:
            folder = chooser.get_filename()
            if os.path.exists(folder):
                files = os.listdir(folder)
                if "DEMOS" in files and "GAMES" in files and "MUSICIANS" in files:
                    self.main.set_hvsc_folder(folder)
                else:
                    chooser.destroy()
                    raise exceptions.FolderException("'{0}' is not a valid HVSC folder".format(folder))
                    return
            else:
                chooser.destroy()
                raise exceptions.FolderException("'{0}' is not a valid HVSC folder".format(folder))
                return
                
        chooser.destroy()

    def fill_date_list(self):
        parent = {}
        parent[""] = None
        model = self.tvdate.get_model()
        
        logging.info("Populating date tab…")
        dates = self.main.database.get_date()
        for date in dates:
            
            iter = model.append(parent[""])
            parent[str(date)] = iter
            
            model.set_value(iter, COLUMN_DATE_DATE, str(date))
            model.append(iter, ("", "", "", "", ""))
            #~ sids = self.main.database.get_artists_tracks(artist)
            #~ for sid in sids:
                #~ model.append(parent[str(sid.artist)], (self.escape(str(sid.title)), sid.path))
        logging.info("… done")

    def fill_artist_list(self):
        parent = {}
        parent[""] = None
        model = self.tvartists.get_model()
        
        logging.info("Populating artist tab…")
        artists = self.main.database.get_artists()
        for artist in artists:
            iter = model.append(parent[""])
            parent[str(artist)] = iter
            
            model.set_value(iter, COLUMN_ARTISTS_ARTIST, str(artist))
            model.append(iter, ("", "", "", ""))
            #~ sids = self.main.database.get_artists_tracks(artist)
            #~ for sid in sids:
                #~ model.append(parent[str(sid.artist)], (self.escape(str(sid.title)), sid.path))
        logging.info("… done")
    
    def fill_directory_list(self):
        #~ file_structure = []
        
        parent = {}
        parent[self.main.basedir] = None
        self.tvdirectories.set_model(None)
        model = self.setup_directories_treeview(self.tvdirectories)
        model.clear()
        
        logging.info("Reading directory tree…")
        root = self.main.basedir
        dirs = os.listdir(self.main.basedir)
        for dir in sorted(dirs):
            if not dir.endswith("update") and not dir.endswith("DOCUMENTS") and \
            not root.endswith("update") and not root.endswith("DOCUMENTS") and \
            os.path.isdir(os.path.join(root, dir)):
                pardir = os.path.join(root,dir)
                iter = model.append(parent[root], (self.escape(dir),(pardir))) 
                parent[pardir] = iter
                model.append(iter, ("", ""))
        #~ for root, dirs, files in os.walk(self.main.basedir, topdown=True):
            #~ for dir in sorted(dirs):
                #~ if not dir.endswith("update") and not dir.endswith("DOCUMENTS") and \
                #~ not root.endswith("update") and not root.endswith("DOCUMENTS"):
                    #~ pardir = os.path.join(root,dir)
                    #~ parent[pardir] = model.append(parent[root], (self.escape(dir),(pardir))) 
            #~ for file in sorted(files):
                #~ if file.lower().endswith(".sid"):
                    #~ model.append(parent[root], (self.escape(file),(os.path.join(root, file)))) 
        logging.info("…done")
        self.tvdirectories.set_model(model)
       
    def escape(self, s):
        return glib.markup_escape_text(s)
        #~ return cgi.escape(s.decode("iso8859-15"))

    def setup_search_treeview(self, treeview):
        model = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING)
        
        selection = treeview.get_selection()
        selection.set_mode(gtk.SELECTION_MULTIPLE)
        
        renderer = gtk.CellRendererText()
        renderer.set_data("column", COLUMN_SEARCH_ARTIST)
        column = gtk.TreeViewColumn(_('Artist'), renderer, markup=COLUMN_SEARCH_ARTIST)#text=0)
        column.set_sort_column_id(COLUMN_SEARCH_ARTIST)
        treeview.append_column(column)

        renderer = gtk.CellRendererText()
        renderer.set_data("column", COLUMN_SEARCH_TITLE)
        column = gtk.TreeViewColumn(_('Title'), renderer, markup=COLUMN_SEARCH_TITLE)#text=0)
        column.set_sort_column_id(COLUMN_SEARCH_TITLE)
        treeview.append_column(column)

        treeview.set_model(model)

    def setup_date_treeview(self, treeview):
        #~ COLUMN_DATE_DATE,
         #~ COLUMN_DATE_ARTIST,
         #~ COLUMN_DATE_TRACK,
         #~ COLUMN_DATE_LENGTH,
         #~ COLUMN_DATE_PATH,
        model = gtk.TreeStore(gobject.TYPE_STRING, gobject.TYPE_STRING,  gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING)
        
        selection = treeview.get_selection()
        selection.set_mode(gtk.SELECTION_MULTIPLE)

        renderer = gtk.CellRendererText()
        renderer.set_data("column", COLUMN_DATE_DATE)
        column = gtk.TreeViewColumn(_('Date'), renderer, text=COLUMN_DATE_DATE)#text=0)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        column.set_resizable(True)
        column.set_fixed_width(80)
        column.set_sort_column_id(COLUMN_DATE_DATE)
        treeview.append_column(column)    
        
        renderer = gtk.CellRendererText()
        renderer.set_data("column", COLUMN_DATE_ARTIST)
        column = gtk.TreeViewColumn(_('Artists'), renderer, text=COLUMN_DATE_ARTIST)#text=0)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        column.set_resizable(True)
        column.set_fixed_width(80)
        column.set_sort_column_id(COLUMN_DATE_ARTIST)
        treeview.append_column(column)

        renderer = gtk.CellRendererText()
        renderer.set_data("column", COLUMN_DATE_TRACK)
        column = gtk.TreeViewColumn(_('Title'), renderer, markup=COLUMN_DATE_TRACK)#text=0)
        column.set_resizable(True)
        column.set_sort_column_id(COLUMN_DATE_TRACK)
        treeview.append_column(column)

        renderer = gtk.CellRendererText()
        renderer.set_data("column", COLUMN_DATE_LENGTH)
        column = gtk.TreeViewColumn(_('Length'), renderer, markup=COLUMN_DATE_LENGTH)#text=0)
        column.set_resizable(True)
        column.set_sort_column_id(COLUMN_DATE_LENGTH)
        treeview.append_column(column)

        treeview.set_model(model)

    def setup_artists_treeview(self, treeview):
         #~ COLUMN_ARTISTS_ARTIST,
         #~ COLUMN_ARTISTS_TRACK,
         #~ COLUMN_ARTISTS_LENGTH,
         #~ COLUMN_ARTISTS_PATH,
        model = gtk.TreeStore(gobject.TYPE_STRING,  gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING)
        
        selection = treeview.get_selection()
        selection.set_mode(gtk.SELECTION_MULTIPLE)
    
        
        renderer = gtk.CellRendererText()
        renderer.set_data("column", COLUMN_ARTISTS_ARTIST)
        column = gtk.TreeViewColumn(_('Artists'), renderer, text=COLUMN_ARTISTS_ARTIST)#text=0)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        column.set_resizable(True)
        column.set_fixed_width(80)
        column.set_sort_column_id(COLUMN_ARTISTS_ARTIST)
        treeview.append_column(column)

        renderer = gtk.CellRendererText()
        renderer.set_data("column", COLUMN_ARTISTS_TRACK)
        column = gtk.TreeViewColumn(_('Title'), renderer, markup=COLUMN_ARTISTS_TRACK)#text=0)
        column.set_resizable(True)
        column.set_sort_column_id(COLUMN_ARTISTS_TRACK)
        treeview.append_column(column)

        renderer = gtk.CellRendererText()
        renderer.set_data("column", COLUMN_ARTISTS_LENGTH)
        column = gtk.TreeViewColumn(_('Length'), renderer, markup=COLUMN_ARTISTS_LENGTH)#text=0)
        column.set_resizable(True)
        column.set_sort_column_id(COLUMN_ARTISTS_LENGTH)
        treeview.append_column(column)

        treeview.set_model(model)

    def setup_directories_treeview(self, treeview):
        model = gtk.TreeStore(gobject.TYPE_STRING, gobject.TYPE_STRING)
        
        selection = treeview.get_selection()
        selection.set_mode(gtk.SELECTION_SINGLE)
        
        renderer = gtk.CellRendererText()
        renderer.set_data("column", COLUMN_DIRNAME)
        column = gtk.TreeViewColumn(_('Folder'), renderer, markup=COLUMN_DIRNAME)#text=0)
        treeview.append_column(column)
        
        return model
    
    def _set_playback_indicator(self, tvcolumn, cell, model, iter):
        
        if model.get_value(iter, COLUMN_INDICATOR) == ">":
            cell.set_property('stock-id', gtk.STOCK_MEDIA_PLAY)
            cell.set_property('stock-size', gtk.ICON_SIZE_SMALL_TOOLBAR)
        else:
            cell.set_property('stock-id', None)
            
    def setup_playlist_treeview(self, treeview):
        model = gtk.ListStore(
            gobject.TYPE_STRING,
            gobject.TYPE_STRING,
            gobject.TYPE_STRING,
            gobject.TYPE_STRING,
            gobject.TYPE_STRING,
            gobject.TYPE_STRING,
            gobject.TYPE_INT,
            gobject.TYPE_STRING,
            gobject.TYPE_STRING,
            gobject.TYPE_STRING,
            gobject.TYPE_STRING
       )
        
        treeview.set_model(model)
        
        ## Columns
        # Indicator
        #~ renderer = gtk.CellRendererText()
        renderer = gtk.CellRendererPixbuf()
        renderer.set_data("column", COLUMN_INDICATOR)
        column = gtk.TreeViewColumn("", renderer)
        treeview.append_column(column)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        column.set_cell_data_func(renderer, self._set_playback_indicator)
        column.set_fixed_width(30)
        
        # Artist
        renderer = gtk.CellRendererText()
        renderer.set_data("column", COLUMN_ARTIST)
        column = gtk.TreeViewColumn(_("Artist"), renderer, markup=COLUMN_ARTIST)
        treeview.append_column(column)
        #~ column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        column.set_resizable(True)
        column.set_sort_column_id(COLUMN_ARTIST)
        column.set_fixed_width(70)
        
        # Title
        renderer = gtk.CellRendererText()
        renderer.set_data("column", COLUMN_TITLE)
        column = gtk.TreeViewColumn(_("Title"), renderer, markup=COLUMN_TITLE)
        treeview.append_column(column)
        #~ column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        column.set_resizable(True)
        column.set_sort_column_id(COLUMN_TITLE)
        #~ column.set_fixed_width(70)
        
        # Length
        renderer = gtk.CellRendererText()
        renderer.set_data("column", COLUMN_LENGTH)
        column = gtk.TreeViewColumn(_("Length"), renderer, markup=COLUMN_LENGTH)
        treeview.append_column(column)
        #~ column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        column.set_resizable(True)
        column.set_sort_column_id(COLUMN_LENGTH)
        #~ column.set_fixed_width(70)
        
        # Copyright
        renderer = gtk.CellRendererText()
        renderer.set_data("column", COLUMN_COPYRIGHT)
        column = gtk.TreeViewColumn(_("Copyright"), renderer, markup=COLUMN_COPYRIGHT)
        treeview.append_column(column)
        #~ column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        column.set_resizable(True)
        column.set_sort_column_id(COLUMN_COPYRIGHT)
        #~ column.set_fixed_width(70)
        
        
        
        ## COMBO
        lsmodel = gtk.ListStore(gobject.TYPE_STRING)
        renderer = gtk.CellRendererCombo()
        renderer.set_property("text-column", 0)
        renderer.set_property("editable", True)
        renderer.set_property("has-entry", True)
        renderer.set_property("model", lsmodel)
        column = gtk.TreeViewColumn(_("Subsong"), renderer, text=COLUMN_SONG)
        column.set_sort_column_id(COLUMN_NUM_SONGS)
        treeview.append_column(column)
        renderer.connect('editing-started', self.populate_combo_cb, (lsmodel,))
        renderer.connect('edited', self.combo_edited)

        #~ # Subsongs
        #~ renderer = gtk.CellRendererText()
        #~ renderer.set_data("column", COLUMN_NUM_SONGS)
        #~ column = gtk.TreeViewColumn(_("# Subsongs"), renderer, markup=COLUMN_NUM_SONGS)
        #~ treeview.append_column(column)
        #~ column.set_resizable(True)
        #~ column.set_sort_column_id(COLUMN_NUM_SONGS)
        
        # Rating
        renderer = gtk.CellRendererText()
        renderer.set_data("column", COLUMN_RATING)
        column = gtk.TreeViewColumn(_("Rating"), renderer, markup=COLUMN_RATING)
        treeview.append_column(column)
        column.set_resizable(True)
        column.set_sort_column_id(COLUMN_RATING)
        model.set_sort_func(COLUMN_RATING, self.num_sort, COLUMN_RATING)
        column.set_fixed_width(30)
        
        # Playcounter
        renderer = gtk.CellRendererText()
        renderer.set_data("column", COLUMN_PLAYCOUNTER)
        column = gtk.TreeViewColumn(_("Played"), renderer, markup=COLUMN_PLAYCOUNTER)
        treeview.append_column(column)
        column.set_resizable(True)
        column.set_sort_column_id(COLUMN_PLAYCOUNTER)
        model.set_sort_func(COLUMN_PLAYCOUNTER, self.num_sort, COLUMN_PLAYCOUNTER)
        column.set_fixed_width(30)

        x="""
        # Defaultsong
        renderer = gtk.CellRendererText()
        renderer.set_data("column", COLUMN_SONG)
        column = gtk.TreeViewColumn(_("Default Song"), renderer, markup=COLUMN_SONG)
        treeview.append_column(column)
        #~ column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        column.set_resizable(True)
        column.set_sort_column_id(COLUMN_SONG)
        #~ column.set_fixed_width(70)
        """
        
        return model
    
    def num_sort(self, model, iter1, iter2, column):
        v1 = int(model.get_value(iter1, column))
        v2 = int(model.get_value(iter2, column))
        #~ print v1, v2
        
        if v1 > v2:
            return -1
        elif v1 == v2:
            return 0
        else:
            return 1

    def combo_edited(self, cellrenderertext, path, new_text):
        treeviewmodel = self.tvplaylist.get_model()
        iter = treeviewmodel.get_iter(path)
        
        numsongs = treeviewmodel.get_value(iter, COLUMN_NUM_SONGS)
        path = treeviewmodel.get_value(iter, COLUMN_PATH)
        try:
            song, length = new_text.split(":", 1)
            length = length.strip()
        except ValueError:

            if new_text.isdigit():
                song = int(new_text)
                if song > numsongs:
                    song = numsongs
                if song < 1:
                    song = 1
            else:
                song = 1
                
            sid = self.main.database.get_sid(path)
            length = sidinfo.seconds_to_readable_time(sid.get_songlength(song))
                
            
            
        
        treeviewmodel.set_value(iter, COLUMN_SONG, "{0}/{1}".format(song, numsongs))
        treeviewmodel.set_value(iter, COLUMN_LENGTH, length)
    
    def populate_combo_cb(self, cell, editable, path, data):
        combo_model = cell.get_property("model")
        combo_model.clear()
        
        treemodel = self.tvplaylist.get_model()
        songs = int(treemodel.get_value(treemodel.get_iter_from_string(path), COLUMN_NUM_SONGS))
        
        for i in range(1, songs+1):
            sid = self.main.database.get_sid(treemodel.get_value(treemodel.get_iter_from_string(path), COLUMN_PATH))
            length = sidinfo.seconds_to_readable_time(sid.get_songlength(i))
            combo_model.append(["{0}: {1}".format(i, length)])
            
    
    def append_playlist(self, sids, get_ratings=True):
        model = self.tvplaylist.get_model()
        model.set_default_sort_func(lambda *args: -1) 
        model.set_sort_column_id(-1, gtk.SORT_ASCENDING)
        
        hashes = []
        
        for sid in sids:
            iter = model.append()
            model.set (iter,
                COLUMN_ARTIST, self.escape(sid.artist),
                COLUMN_TITLE, self.escape(sid.title),
                COLUMN_LENGTH, self.escape(sidinfo.seconds_to_readable_time(sid.get_songlength(sid.startsong))),
                COLUMN_COPYRIGHT, self.escape(sid.copyright),
                COLUMN_SONG, "{0}/{1}".format(sid.startsong, sid.subsongs),
                COLUMN_NUM_SONGS, sid.subsongs,
                COLUMN_PATH, self.escape(sid.path),
                COLUMN_HASH, sid.hash
            )
            hashes.append(sid.hash)
            
        if get_ratings:
            self.get_ratings(hashes)
        
        #~ self.show_playlist_length()
        
    def update_rating(self, hashes):
        ret = self.main.database.get_sid_rating(hashes)
        d = {}
        for hash, rating, counter in ret:
            if rating is None: rating = 0 
            if counter is None: counter = 0 
            d[hash] = (rating, counter)
        
        
        model = self.tvplaylist.get_model()    
        iter = model.get_iter_first()
        while iter:
            hash = model.get_value(iter, COLUMN_HASH)
            try:
                model.set(iter ,
                    COLUMN_RATING, d[hash][0],
                    COLUMN_PLAYCOUNTER, d[hash][1]
                )
            except KeyError:
                pass
            iter = model.iter_next(iter)

    def get_ratings(self, hashes):
        ret = self.main.database.get_sid_rating(hashes)
        d = {}
        for hash, rating, counter in ret:
            if rating is None: rating = 0 
            if counter is None: counter = 0 
            d[hash] = (rating, counter)
        
        
        model = self.tvplaylist.get_model()    
        iter = model.get_iter_first()
        while iter:
            hash = model.get_value(iter, COLUMN_HASH)
            try:
                model.set(iter ,
                    COLUMN_RATING, d[hash][0],
                    COLUMN_PLAYCOUNTER, d[hash][1]
                )
            except KeyError:
                model.set(iter, 
                    COLUMN_RATING, 0,
                    COLUMN_PLAYCOUNTER, 0
                )
            iter = model.iter_next(iter)
            
        

    def next_prev_track(self, relation):
        model = self.tvplaylist.get_model()
        number_of_rows = model.iter_n_children(None)
        
        if number_of_rows == 0:
            return
        
        if self.now_playing_iter:
            path = model.get_path(self.now_playing_iter)
            if self.tbShuffle.get_active():
                next_iter = model.get_iter(random.randint(0, number_of_rows-1))
            else:
                if not path: return
                try:
                    next_iter = model.get_iter(path[0] + relation)
                except ValueError:
                    return
            
            path = model.get(next_iter, COLUMN_PATH)[0]
            sid = self.main.database.get_sid(path) #sidinfo.get_md5_hash(path)
            song = int(model.get(next_iter, COLUMN_SONG)[0].split("/")[0])
            self.main.play(sid, song)
    def quit(self):
        self.main.events.disconnect_event("now-playing", self.now_playing_cb)
        self.main.events.disconnect_event("track-over", self.track_over_cb)
        self.main.events.disconnect_event("playback-stopped", self.playback_stopped_cb)
        self.main.quit()
        gtk.main_quit()
        
    #
    # CALLBACKS
    #
    def mnuInfo_activate_cb(self, widget):
        dia = AboutDialog()
        dia.run()
        dia.destroy()
        
    def mnuReindex_activate_cb(self, widget):
        logging.info("Dropping 'sids' table in order to force reindexing…")
        self.main.database.drop_table_sids()
        logging.info("… done")
        self.quit()
        os.execv(sys.argv[0], sys.argv)
       
   
    def mnuShuffle_activate_cb(self, widget):
        model = self.tvplaylist.get_model()
        number_of_rows = model.iter_n_children(None)
        
        l = []

        model.set_default_sort_func(lambda *a: 0) 
        model.set_sort_column_id(-1, gtk.SORT_ASCENDING)

        #~ self.tvplaylist.freeze_child_notify()
        iter = model.get_iter_first()
        while iter:
            #~ iter = model.iter_nth_child(None, random.randint(0, number_of_rows-1))
            l.append(model.get(iter, *xrange(0, COLUMN_HASH+1)))
            iter = model.iter_next(iter)

        model.clear()
        random.shuffle(l)
        
        for i in l:
            iter_new = model.append()
            model.set (iter_new,
            COLUMN_INDICATOR, i[0],
            COLUMN_ARTIST, i[1],
            COLUMN_TITLE, i[2],
            COLUMN_LENGTH, i[3],
            COLUMN_COPYRIGHT, i[4],
            COLUMN_SONG, i[5],
            COLUMN_RATING, i[6],
            COLUMN_PLAYCOUNTER, i[7],
            COLUMN_NUM_SONGS, i[8],
            COLUMN_PATH, i[9],
            COLUMN_HASH, i[10],
            )
            

    
    def mnuBestRated_activate_cb(self, widget):
        sids = self.main.database.get_best_rated()
        self.append_playlist(sids)
            
        #~ self.show_playlist_length()
    def mnuRandom_activate_cb(self, activate):
        sids = self.main.database.get_random_sids(25)
        self.append_playlist(sids)
        
        #~ self.show_playlist_length()
    def mnuMostPlayed_activate_cb(self, widget):
        sids = self.main.database.get_most_played()
        self.append_playlist(sids)
        #~ self.show_playlist_length()
        
        
    def starscale_rating_changed_db(self, widget, rating):
        self.main.database.rate_track(self.main.playsid.current_sid.hash, rating)
        self.update_rating([self.main.playsid.current_sid.hash])
        self.show_status_message("Rated '{0}' with {1} star(s)".format(self.main.playsid.current_sid.title, rating))
        
    def window1_delete_event_cb(self, widget, events):
        self.quit()
        
    def entrySearch_activate_cb(self, widget):
        model = self.tvsearch.get_model()
        model.clear()
        
        for sid in self.main.database.search(widget.get_text()):
            iter = model.append(None)
            model.set (iter,
                COLUMN_SEARCH_ARTIST, self.escape(sid.artist),
                COLUMN_SEARCH_TITLE, self.escape(sid.title),
                COLUMN_SEARCH_PATH, self.escape(sid.path),
            )
        
    def mnuSave_activate_cb(self, widget):
        chooser = gtk.FileChooserDialog(title="Save playlist", 
        action=gtk.FILE_CHOOSER_ACTION_SAVE ,
        buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK) 
        )
        filter = gtk.FileFilter()
        filter.add_pattern("*.spl")
        filter.set_name("SPL Playlists")
        chooser.add_filter(filter)
        ret = chooser.run()
        if ret == gtk.RESPONSE_OK:
            fl = chooser.get_filename()
            if not fl.lower().endswith(".spl"):
                fl = "{0}.spl".format(fl)
            ## TODO - ASK IF OVERWRITING FILE IS OK
            paths = []
            model = self.tvplaylist.get_model()
            iter = model.get_iter_first()
            while iter:
                paths.append(model.get(iter, COLUMN_PATH)[0])
                iter = model.iter_next(iter)
            
            sids = list(self.main.database.get_sids(paths, sort=True))
            playlist.write_playlist(sids, fl, self.main.basedir)
                
        chooser.destroy()

    def mnuQuit_activate_cb(self, widget):
        self.quit()
    
    def mnuLoad_activate_cb(self, widget):
        chooser = gtk.FileChooserDialog(title="Open playlist", 
        action=gtk.FILE_CHOOSER_ACTION_OPEN ,
        buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK) 
        )
        filter = gtk.FileFilter()
        filter.add_pattern("*.spl")
        filter.set_name("SPL Playlists")
        chooser.add_filter(filter)
        ret = chooser.run()
        if ret == gtk.RESPONSE_OK:
            fl = chooser.get_filename()
            if os.path.exists(fl):
                ## Todo: If I convert the app to exclusive hash-use one day
                # playlists which are returned in PATH_MODE need to be
                # converted to hash-mode: So there should be query returning
                # a list of hashes for giving pathes (database)
                mode, pl = playlist.read_playlist(fl, playlist.PATH_MODE)
                if mode == playlist.HASH_MODE:
                    pass
                else:
                    #~ sids = list(self.main.database.iter_sids_ordered(pl))
                    sids = self.main.database.get_sids(pl, sort=True)
                self.append_playlist(sids)
            else:
                chooser.destroy()
                dia =ErrorDialog(exceptions.FileException, "'{0}' is not a valid file".format(fl))
                dia.run()
                dia.destroy()
                return
                
        chooser.destroy()
    
        
    def mnu_shorter_activate_cb(self, widget, seconds):
        model = self.tvplaylist.get_model()
        iter = model.get_iter_first()
        paths = []
        while iter:
            duration = sidinfo.readable_time_to_seconds(model.get(iter, COLUMN_LENGTH)[0])
            if duration < seconds:
                paths.append(gtk.TreeRowReference(model, model.get_path(iter)))
            iter = model.iter_next(iter)
        
        for TreeRef in paths:
            iter = model.get_iter(TreeRef.get_path())
            model.remove(iter)
    def mnu_longer_activate_cb(self, widget, seconds):
        model = self.tvplaylist.get_model()
        iter = model.get_iter_first()
        paths = []
        while iter:
            duration = sidinfo.readable_time_to_seconds(model.get(iter, COLUMN_LENGTH)[0])
            if duration > seconds:
                paths.append(gtk.TreeRowReference(model, model.get_path(iter)))
            iter = model.iter_next(iter)
        
        for TreeRef in paths:
            iter = model.get_iter(TreeRef.get_path())
            model.remove(iter)
    
    def scale_button_press_cb(self, widget, event):
        # make sure we get changed notifies
        self.changed_id = self.scale.connect('value-changed',
                self.scale_value_changed_cb)
            
    def scale_value_changed_cb(self, widget):
        #~ if self.changed_id < 0:
            #~ t = int(widget.get_value())
            #~ self.main.play(self.main.playsid.current_file, startpos=t)
            pass
    def scale_move_slider_cb(self, widget):
        #~ treeselection = self.tvplaylist.get_selection()
        #~ model, iter = treeselection.get_selected()
        
        t = int(widget.get_value())
        if self.now_playing_iter:
            song = int(model.get(iter, COLUMN_SONG)[0].split("/")[0])
            self.main.play(self.main.playsid.current_sid, song, startpos=t)
        self.main.play(self.main.playsid.current_sid, startpos=t)

    def scale_button_release_cb(self, widget, event):
        if self.changed_id < 0: return
        widget.disconnect(self.changed_id)
        self.changed_id = -1

        treeselection = self.tvplaylist.get_selection()
        model, iter = treeselection.get_selected()
        
        t = int(widget.get_value())
        if self.now_playing_iter:
            song = int(model.get(iter, COLUMN_SONG)[0].split("/")[0])
            self.main.play(self.main.playsid.current_sid, song, startpos=t)
        self.main.play(self.main.playsid.current_sid, startpos=t)
    
    def scale_format_value_cb(self, widget, value):
        t = self.main.playsid.timer
        if t:
            l = ""
            if self.main.playsid.current_sid:
                l = sidinfo.seconds_to_readable_time( self.main.playsid.current_sid.get_songlength(self.main.playsid.current_subtune))
            m, s = divmod(t, 60)
            return "%02d:%02d / %s" % (m, s, l)
        else:
            return "???"
        
        t = self.main.playsid.timer
        if t:
            m, s = divmod(t, 60)
            return "%02d:%02d" % (m, s)
        else:
            return "???"
        
    def timeout_cb(self):
        self.show_playlist_length()
        if self.main.playsid.error:
            err, msg = self.main.playsid.error
            gtk.gdk.threads_enter()
            dia = ErrorDialog(err, msg)
            dia.run()
            dia.destroy()
            gtk.gdk.threads_leave()
            self.main.playsid.error = None
        
        t = self.main.playsid.timer
        if t:
            l = ""
            if self.main.playsid.current_sid:
                l = self.main.playsid.current_sid.get_songlength(self.main.playsid.current_subtune)
            m, s = divmod(t, 60)
            #~ self.lblTime.set_text("%02d:%02d / %s" % (m, s, l))
            self.scale.set_value(t)
        #~ else:
            #~ self.lblTime.set_text("")
        return True
        
    def mnuClearPlaylist_activate_cb(self, widget):
        model = self.tvplaylist.get_model()
        model.clear()

    def tvdate_rowactivated_cb(self, treeview, path, view_column):
        model = treeview.get_model()
        iter = model.get_iter(path)
        path = model.get(iter, COLUMN_DATE_PATH)[0]
        
        if not path: # when a whole date node was clicked
            date = model.get(iter, COLUMN_DATE_DATE)[0]
            sids = self.main.database.get_tracks_by_year(date)
            self.append_playlist(sids)
        else:
            sid = self.main.database.get_sid(path)
            self.append_playlist([sid])


    def tvdate_row_expanded_cb(self, widget, iter, path):
        model = widget.get_model()

        num_childs = model.iter_n_children(iter)
        delete = []
        for i in xrange(0, num_childs):
            delete.append(model.iter_nth_child(iter, i))
        
        date = model.get_value(iter, COLUMN_DATE_DATE)
        sids = self.main.database.get_tracks_by_year(unicode(date))
        for sid in sids:
            sub_iter = model.append(iter)
            model.set(sub_iter,
                COLUMN_DATE_ARTIST, str(sid.artist),
                COLUMN_DATE_TRACK, self.escape(str(sid.title)),
                COLUMN_DATE_LENGTH, sidinfo.seconds_to_readable_time(sid.get_songlength(sid.startsong)),
                COLUMN_DATE_PATH, self.escape(sid.path)
            )
        
        for iter in delete:
            model.remove(iter)

    def tvdate_drag_data_get(self, widget, drag_context, selection, info, timestamp):
        sel = widget.get_selection()
        model, paths = sel.get_selected_rows()
        data = []
        
        
        for path in paths:
            iter = model.get_iter(path)
            p = model.get_value(iter, COLUMN_DATE_PATH)
            if p: ## A single song
                data.append(model.get_value(iter, COLUMN_DATE_PATH))
            else: # whole date node
                date = model.get(iter, COLUMN_DATE_DATE)[0]
                sids = self.main.database.get_tracks_by_year(unicode(date))
                for sid in sids:
                    data.append(sid.path)
                
        d = u"__SEPERATOR__".join(data)
        selection.set(selection.target, 8, d)
        return

    def tvartists_drag_data_get(self, widget, drag_context, selection, info, timestamp):
        sel = widget.get_selection()
        model, paths = sel.get_selected_rows()
        data = []
        
        #~ artists = []
        
        for path in paths:
            iter = model.get_iter(path)
            p = model.get_value(iter, COLUMN_ARTISTS_PATH)
            if p: ## A single song
                data.append(model.get_value(iter, COLUMN_ARTISTS_PATH))
            else: # whole artist node
                artist = model.get(iter, COLUMN_ARTISTS_ARTIST)[0]
                #~ artists.append(unicode(artist))
                sids = self.main.database.get_artists_tracks(unicode(artist))
                for sid in sids:
                    data.append(sid.path)
        
        #~ if artists != []:
            #~ sids = self.main.database.get_multiple_artists_tracks(artists)
            #~ for sid in sids:
                #~ data.append(sid.path)
            
        
        d = u"__SEPERATOR__".join(data)
        selection.set(selection.target, 8, d)
        return
    
    def tvsearch_drag_data_get(self, widget, drag_context, selection, info, timestamp):
        sel = widget.get_selection()
        model, paths = sel.get_selected_rows()
        data = []
        for path in paths:
            iter = model.get_iter(path)
            data.append(model.get_value(iter, COLUMN_SEARCH_PATH))
        d = u"__SEPERATOR__".join(data)
        selection.set(selection.target, 8, d)
        return
    
    def tvdirectories_row_expanded_cb(self, widget, iter, path):
        model = widget.get_model()
        
        num_childs = model.iter_n_children(iter)
        delete = []
        for i in xrange(0, num_childs):
            delete.append(model.iter_nth_child(iter, i))
        
        p = model.get_value(iter, COLUMN_DIRPATH)
        content = sorted(os.listdir(p))
        for f in content:
            path = os.path.join(p, f)
            sub_iter = model.append(iter)
            model.set(sub_iter,
                COLUMN_DIRNAME, self.escape(f),
                COLUMN_DIRPATH, path
            )
            if os.path.isdir(path):
                model.append(sub_iter, ("", ""))
                
        for iter in delete:
            model.remove(iter)
    
    def tvartists_row_expanded_cb(self, widget, iter, path):
        model = widget.get_model()
        
        num_childs = model.iter_n_children(iter)
        delete = []
        for i in xrange(0, num_childs):
            delete.append(model.iter_nth_child(iter, i))

        artist = model.get_value(iter, COLUMN_ARTISTS_ARTIST)
        sids = self.main.database.get_artists_tracks(unicode(artist))
        for sid in sids:
            sub_iter = model.append(iter)
            model.set(sub_iter,
                COLUMN_ARTISTS_ARTIST, str(sid.artist),
                COLUMN_ARTISTS_TRACK, self.escape(str(sid.title)),
                COLUMN_ARTISTS_LENGTH, sidinfo.seconds_to_readable_time(sid.get_songlength(sid.startsong)),
                COLUMN_ARTISTS_PATH, self.escape(sid.path)
            )
        
        for iter in delete:
            model.remove(iter)

    def tvdirectories_drag_data_get(self, widget, drag_context, selection, info, timestamp):
        sel = widget.get_selection()
        model, iter = sel.get_selected()
        data = model.get_value(iter, 1)
        selection.set(selection.target, 8, data)
        return
        
    def tvplaylist_drag_data_received(self, widget, context, x, y, selection, info, timestamp):
        model = widget.get_model()
        data = selection.data
        if os.path.isdir(data):
            data = self.main.readdir(data)
        elif "__SEPERATOR__" in data:
            data = data.split("__SEPERATOR__")
        else:
            data = [data]

        model.set_default_sort_func(lambda *args: -1) 
        model.set_sort_column_id(-1, gtk.SORT_ASCENDING)

        self.tvplaylist.freeze_child_notify()


        drop_info = widget.get_dest_row_at_pos(x, y)
        data.sort(reverse=not not drop_info)
        
        hashes = []
        
        for sids in self.main.database.iter_sids(data, 5000, sort=False):
            self.tvplaylist.thaw_child_notify()
            #~ while gtk.events_pending(): gtk.main_iteration()
            if drop_info:
                for sid in sids:
                    path, position = drop_info

                    iter = model.get_iter(path)
                    if (position == gtk.TREE_VIEW_DROP_BEFORE or position == gtk.TREE_VIEW_DROP_INTO_OR_BEFORE):
                        model.insert_before(iter,
                            (
                            "", 
                            self.escape(sid.artist),
                            self.escape(sid.title),
                            self.escape(sidinfo.seconds_to_readable_time(sid.get_songlength(sid.startsong))),
                            self.escape(sid.copyright),
                            "{0}/{1}".format(sid.startsong, sid.subsongs),
                            0,
                            0,
                            sid.subsongs,
                            self.escape(sid.path),
                            sid.hash
                            )
                        )
                        hashes.append(sid.hash)
                        #~ self.lsR.events.raise_event("add_song_to_playlist", datum, path[0], 0)
                    else:
                        model.insert_after(iter,
                            (
                            "",
                            self.escape(sid.artist),
                            self.escape(sid.title),
                            self.escape(sidinfo.seconds_to_readable_time(sid.get_songlength(sid.startsong))),
                            self.escape(sid.copyright),
                            "{0}/{1}".format(sid.startsong, sid.subsongs),
                            0,
                            0,
                            sid.subsongs,
                            self.escape(sid.path),
                            sid.hash
                            )
                        )
                        hashes.append(sid.hash)
                        #~ self.lsR.events.raise_event("add_song_to_playlist", datum, path[0], 1)
                        
                    #~ ## Connect TreeView and Liststore again
                    #~ widget.set_model(model)
                    #~ widget.thaw_child_notify()
            else:
                self.append_playlist(sids)#, get_ratings=False)
                #~ for sid in sids:
                    #~ hashes.append(sid.hash)
                    #~ model.append([str, datum])
                    #~ self.lsR.events.raise_event("append_song_to_playlist", datum)
            self.tvplaylist.freeze_child_notify()
        self.tvplaylist.thaw_child_notify()
        
        self.get_ratings(hashes)
        
        #~ while gtk.events_pending():
            #~ gtk.main_iteration()
            #~ print 469546 54654
        #~ self.show_playlist_length()
        if context.action == gtk.gdk.ACTION_MOVE:
            context.finish(True, True, timestamp)
        return
        
    def track_over_cb(self):
        if not self.main.playsid.hold:
            self.next_prev_track(+1)
    
    def playback_stopped_cb(self, hold):
        tbplaystop = self.glade.get_widget("tbPlayStop")
        tbplaystop.set_stock_id(gtk.STOCK_MEDIA_PLAY)
        
        if hold:
            self.scale.hide()
            self.starscale.hide()
        
        model = self.tvplaylist.get_model()
        if self.now_playing_iter:
            model.set(self.now_playing_iter, COLUMN_INDICATOR, "")
        
        
    def now_playing_cb(self, sid):
        gtk.gdk.threads_enter()
        
        self.timeout_cb()
        model = self.tvplaylist.get_model()
        
        ## If there is a now_playing_iter start searching for the next
        # track there - else start from the first iter
        if self.now_playing_iter:
            iter = self.now_playing_iter
        else:
            iter = model.get_iter_first()
        while iter:
            if model.get(iter, COLUMN_HASH)[0] == sid.hash:
                if self.now_playing_iter:
                    model.set(self.now_playing_iter, COLUMN_INDICATOR, "")
                model.set(iter, COLUMN_INDICATOR, ">")
                self.now_playing_iter = iter
                self.update_rating([sid.hash])
                self.tvplaylist.set_cursor(model.get_path(iter))
                break
            iter = model.iter_next(iter)
        else:
            if self.now_playing_iter:
            ## If we checked all iters beginning with the now_playing_iter
            # and did not find any matching track, start all over
            # beginning with the first iter!
                iter = model.get_iter_first()
                while iter:
                    if model.get(iter, COLUMN_PATH)[0] == sid.path:
                        if self.now_playing_iter:
                            model.set(self.now_playing_iter, COLUMN_INDICATOR, "")
                        model.set(iter, COLUMN_INDICATOR, ">")
                        self.now_playing_iter = iter
                        self.tvplaylist.set_cursor(model.get_path(iter))
                        break
                    iter = model.iter_next(iter)
        
        if self.main.playsid.current_sid:
            max = sid.get_songlength(self.main.playsid.current_subtune)
        else:
            max = 500

        adj = gtk.Adjustment(value=self.main.playsid.timer, lower=0, upper=max, step_incr=10, page_incr=60)
        self.scale.set_adjustment(adj)
        self.scale.show()
        self.starscale.show()
        sid = self.main.database.get_sid(self.main.playsid.current_sid.path)
        
        self.starscale.set_value(self.main.database.get_track_rating(sid.hash))
        
        tbplaystop = self.glade.get_widget("tbPlayStop")
        tbplaystop.set_stock_id(gtk.STOCK_MEDIA_STOP)
        
        gtk.gdk.threads_leave()
        
    def tvartists_rowactivated_cb(self, treeview, path, view_column):
        model = treeview.get_model()
        iter = model.get_iter(path)
        path = model.get(iter, COLUMN_ARTISTS_PATH)[0]
        
        if not path: # when a whole artists' node was clicked
            artist = model.get(iter, COLUMN_ARTISTS_ARTIST)[0]
            sids = self.main.database.get_artists_tracks(artist)
            self.append_playlist(sids)
        else:
            sid = self.main.database.get_sid(path)
            self.append_playlist([sid])

    def tvsearch_rowactivated_cb(self, treeview, path, view_column):
        model = treeview.get_model()
        iter = model.get_iter(path)
        path = model.get(iter, COLUMN_SEARCH_PATH)[0]
        
        sid = self.main.database.get_sid(path)
        self.append_playlist([sid])
        
    def tvplaylist_rowactivated_cb(self, treeview, path, view_column):
        model = treeview.get_model()
        iter = model.get_iter(path)
        path = model.get(iter, COLUMN_PATH)[0]
        song = int(model.get(iter, COLUMN_SONG)[0].split("/")[0])
        
        sid = self.main.database.get_sid(path) #sidinfo.get_md5_hash(path)
        self.main.play(sid, song)
        
        if self.now_playing_iter:
            model.set(self.now_playing_iter, COLUMN_INDICATOR, "")
        
        model.set(iter, COLUMN_INDICATOR, ">")
        self.now_playing_iter = iter

    def search_tvdirectories(self, model, column, key, iter, data):
        #~ self.tvdirectories.expand_all()
        path = model.get(iter, COLUMN_DIRPATH)[0]
        #~ print path
        return not key.lower() in path.lower().replace("_", " ")

    def search_tvplaylist(self, model, column, key, iter, data):
        path = model.get(iter, COLUMN_PATH)[0]
        return not key.lower() in path.lower().replace("_", " ")
        
    def tbPrev_clicked_cb(self, widget):
        self.next_prev_track(-1)
    def tbShuffle_toggled_cb(self, widget):
        pass
        
    def tbPlayStop_clicked_cb(self, widget):
        if self.main.playsid.playing:
            self.main.playsid.cancel(hold=True)
        else:
            treeselection = self.tvplaylist.get_selection()
            model, iter = treeselection.get_selected()
            if iter:
                path =  model.get(iter, COLUMN_PATH)[0]
                song = int(model.get(iter, COLUMN_SONG)[0].split("/")[0])
                sid = self.main.database.get_sid(path) #sidinfo.get_md5_hash(path)
                self.main.play(sid, song)
        
    def tbNext_clicked_cb(self, widget):
        self.next_prev_track(+1)
        
    def show_assistant(self):
        assi = assistant.Assistant(self.main)
        while assi.done == False and assi.cancel == False:
            gtk.main_iteration()

        return not assi.cancel
        
class ErrorDialog(gtk.MessageDialog):
    def __init__(self, error, message, trace=""):
        gtk.MessageDialog.__init__(self, None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, None)

        self.set_resizable(True)

        prim = error.name
        sec = error.desc
        
        self.set_markup("<b>%s</b>" % prim)
        self.set_title( _("Error"))
        self.format_secondary_markup(sec)
        
        expander = gtk.Expander(_("Additional Information"))
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        tb = gtk.TextBuffer()
        tv = gtk.TextView(tb)
        tb.set_text(str(message))
        sw.add(tv)
        expander.add(sw)
        self.vbox.pack_start(expander, True, True, 5)
        
        
        
        
        #~ #trace = "asdadsas\nasdasdasdas dak sjdhasj dhaskjhdj ashoda\n\nasdasho dahsijkd aks "
        #~ if trace != "":
            #~ expander = gtk.Expander(_("Additional Information"))            
            #~ lbl = gtk.Label()
            #~ lbl.set_justify(gtk.JUSTIFY_FILL)
            #~ lbl.set_line_wrap(True)        
            #~ lbl.set_markup(trace)
            #~ lbl.set_single_line_mode(False)
            #~ expander.add(lbl)
            #~ self.vbox.pack_start(expander, False, True, 5)
        self.show_all()        
        
class AboutDialog(gtk.AboutDialog):
    def __init__(self):
        gtk.AboutDialog.__init__(self)
        
        self.set_name(lsrsidmodules.__TITLE__)
        self.set_version(str(lsrsidmodules.__VERSION__))
        self.set_copyright(lsrsidmodules.__LICENSE__)
        self.set_program_name(lsrsidmodules.__TITLE__)
        
        self.set_license(lsrsidmodules.__LICENSE__)
        self.set_wrap_license(True)
        
        self.set_comments(_("lsR SID"))
        
        self.set_website("http://launchpad.net/lsr.sid")
        self.set_website_label(_("Project page on Launchpad"))
        
        self.set_authors([lsrsidmodules.__AUTHOR__])
        
        pb = gtk.gdk.pixbuf_new_from_file(os.path.join(helpers.install_dir(), "images", "drafts", "192.png"))
        self.set_logo(pb)
