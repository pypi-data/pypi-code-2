# -*- coding: utf-8 -*- #
# Copyright (C) 2011 Carlos Pais <freemind@lavabit.com>
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


"""Based on Minitube's youtubesearch"""

from watchvideo.main import MATCHER
from watchvideo.qt.QtCore import QUrl


class YoutubeSearch(object):
  
    
  def __init__(self):
    self.videos = []
    self.abortFlag = False
  
  def search(self, searchParams, _max, skip):
    self.videos = []
    url = QUrl("http://gdata.youtube.com/feeds/api/videos")
    url.addQueryItem("max-results", unicode(_max))
    url.addQueryItem("start-index", unicode(skip))
    if searchParams.keywords():
      url.addQueryItem("q", searchParams.keywords())
    if searchParams.author() :
      url.addQueryItem("author", searchParams.author())
      
    self.search_keywords = searchParams.keywords()
    print "keywords: " + str(self.search_keywords)

    sort = searchParams.availableSorts[searchParams.sortBy()]
    url.addQueryItem(sort[0], sort[1])
    
    plugin = MATCHER.match(str(url.toString()))
    if plugin is not None:
      self.videos = list(plugin)
   
    return self.videos
    
  def getVideos(self):
    return self.videos
    
  def abort(self):
    self.abortFlag = True
