# -*- coding: utf-8 -*- #
# Copyright (C) 2010, 2011 Carlos Pais <freemind@lavabit.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os.path

import watchvideo.constants as c
from watchvideo import main

import tempfile

class VideoInfo(object):
    def __init__(self, name="", url="", dl_url="", down=True, folder=c.HOME_FOLDER, after_dl=0,
                 overwrite=False):
        self._name = name
        self.url = url
        self.dl_url = dl_url
        self.down = down
        self._folder = folder
        self.after_complete = after_dl
        self.m_description = ""
        self.m_published = ""
        self.thumbnail = ""
        self.tree_widget_item = None

        if self._name:
          if overwrite is False:
              self.filepath = main.get_new_file(self._folder, self._name)
              self._name = os.path.split(self.filepath)[1]
          else:
              self.filepath = os.path.join(self._folder, self._name)
            
        
    
    def getFolder(self):
        return self._folder
    def setFolder(self, folder):
        self._folder = folder
        self.filepath = main.get_new_file(self._folder, self._name)
    folder = property(getFolder, setFolder)
        
    
    def getName(self):
        return self._name
    def setName(self, name):
        self._name = name
        self.filepath = main.get_new_file(self._folder, self._name)
    name = property(getName, setName)
    
    def toPlay(self):
        self.down = False
    
    def toDownload(self):
        self.down = True
        
    def setTitle(self, title):
        self._name = title
        self.filepath = main.get_new_file(tempfile.gettempdir(), self._name)
        
    def getTitle(self):
        return self._name
    
    def setAuthor(self, author):
        self.m_author = author
        
    def getAuthor(self):
        return self.m_author
    
    def setDescription(self, desc):
        self.m_description = desc
            
    def getDescription(self):
        return self.m_description
        
    def setDuration(self, dur):
        self.duration = dur
        
    def addThumbnailUrl(self, thumb):
        """Receives a QUrl"""
        self.thumbnail = thumb
    
    def getThumbnailUrl(self):
        return str(self.thumbnail.toString())
    
    def setPublished(self, published):
        self.m_published = published
        
    def published(self):
        return self.m_published
            
    def setWebpage(self, webpage):
        """Receives a QUrl"""
        self.m_webpage = webpage
        self.url = str(self.m_webpage.toString())
        
    def webpage(self):
        return str(self.m_webpage.toString())
        
    def getOriginalUrl(self):
        return str(self.m_webpage.toString())
        
    def setViewCount(self, viewCount):
        self.m_viewCount = viewCount
        
    def setTreeWidgetItem(self, item):
        self.tree_widget_item = item
        
    def getTreeWidgetItem(self):
        return self.tree_widget_item
