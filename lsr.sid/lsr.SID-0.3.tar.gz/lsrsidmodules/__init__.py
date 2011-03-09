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
import gui
import copy
import Queue
import logging

import exceptions
import events
import playsid
import sidinfo
#~ import zip
import config
import database
import hotkeys



__VERSION__ = "0.3"
__AUTHOR__ = "Daniel Nögel"
__TITLE__ = "lsr.SID"
__LICENSE__ = "GPLv3"

class Main(object):
    def __init__(self):
        
        hotkeys.Hotkeys(self)
        self.queue = Queue.Queue()
        
        self.config = config.Config()
        self.basedir = self.config.get_value("general", "hvsc-dir", None)
        
        self.events = events.Events()
        self.playsid = playsid.PlaySID(self, self.queue)
        
        self.database = database.DB(self)
                
                #~ print "lala"
            #~ try:
                #~ self.gui.select_hvsc_folder()
            #~ except exceptions.FolderException, message:
                #~ dia= gui.ErrorDialog(exceptions.FolderException, message)
                #~ dia.run()
                #~ dia.destroy()
        self.gui = gui.GUI(self)

        self.cancel = False
        if not self.basedir or self.database.is_empty:
            if self.gui.show_assistant():
                self.config.set_value("general", "hvsc-dir", self.basedir)
            else:
                self.cancel = True
                return
        else:
            self.gui.show()
        
        self.songlengthdb = sidinfo.SongLengthDatabase(self.basedir)
        self.playsid.start()
        
        #~ if self.database.is_empty:
            #~ logging.info("Will now import all sids to database.")
            #~ logging.info("This might take a while.")
            #~ for sids in sidinfo.recursive_read_directory(self.basedir, self.songlengthdb):
                #~ self.database.insert_sids(sids)
            #~ self.database.create_index()
            
            
        self.gui.fill_directory_list()
        self.songlengthdb._load_database()
        self.gui.fill_artist_list()
        self.gui.fill_date_list()
        self.gui.show_stats()
        
    def quit(self):
        self.database.quit()
        self.playsid.cancel(hold=True)
        self.queue.put(playsid.Job("QUIT"))
        
        
        
    def set_hvsc_folder(self, folder):
        self.config.set_value("general", "hvsc-dir", folder)
        self.basedir = folder
        self.gui.fill_directory_list()
        self.songlengthdb.load_database()
        
        
        #~ self.play(self.get_file("/MUSICIANS/W/Welle_Erdball/Tanz_Eiskalt.sid"))
        #~ self.add_folder("/MUSICIANS/X/")

    def play(self, sid, subtune=None, startpos=None):
        if self.playsid.playing:
            self.playsid.cancel_all()

        if sid is None: return

        #~ sid = self.database.get_sid(path) #sidinfo.get_md5_hash(path)
        print self.database.get_artist_playstats(sid.artist)
        if not startpos:
            self.database.increase_listen_counter(sid.hash)
        job = playsid.Job("PLAY", sid, subtune, startpos)
        self.queue.put(job)

    def readdir(self, folder):
        ret = []
        logging.info ("Reading Directory: %s" % folder) 
        for root, dirs, files in os.walk(folder, topdown=True):
            for file in files:
                if file.lower().endswith(".sid"):
                    ret.append( os.path.join(root, file) )
        return ret

        
    def add_folder(self, path, pos=-1):
        path = self.get_file(path)
        for root, folders, files in os.walk(path):
            for file in files:
                if file.endswith(".sid"):
                    p = os.path.join(root, file)
                    self.append_file(p)
        
    def get_file(self, path):
        """Right now kind of obsolete. This will transform a
        relative HVSC-path into a real path to a file on the
        filesystem.
        
        Later this will also extract files from zip-archives and
        return a path pointing to them"""
        if not self.basedir in path:
            if path.startswith("/"):
                path = path[1:]
            return os.path.join(self.basedir, path)
        else:
            return path
    
    def get_file_infos(self, path, subtune=None):
        infos = sidinfo.get_infos(path)
        try:
            time = self.songlengthdb.query(path)
            if subtune:
                time = time[subtune-1][0]
            else:
                time = time[infos["startsong"]-1][0]
        except KeyError:
            time = "???"
            pass
        
        return (infos, time)
        
    def append_file(self, path, subtune=None):
        infos, time = self.get_file_infos(path, subtune)
        self.gui.append_playlist(path, infos, time)

