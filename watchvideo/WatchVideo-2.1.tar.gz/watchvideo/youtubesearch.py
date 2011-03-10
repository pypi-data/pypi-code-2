# -*- coding: utf-8 -*- #

#Minitube's youtubesearch

from watchvideo.main import MATCHER
from watchvideo.qt.QtCore import QUrl


class YoutubeSearch(object):
  
    
  def __init__(self):
    self.videos = []
    self.abortFlag = False
  
  def search(self, searchParams, _max, skip):
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
    else:
      self.videos = []
   
    return self.videos
    
  def getVideos(self):
    return self.videos
    
  def abort(self):
    self.abortFlag = True
