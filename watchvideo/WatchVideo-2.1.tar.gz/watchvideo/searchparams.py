# -*- coding: utf-8 -*- #

#Minitube's searchparams


class SearchParams(object):
    def __init__(self):
      self.m_keywords = None
      self.m_author = None
      self.m_sortBy = None
      self.m_sortBy = "SortByRelevance"
      self.availableSorts = {"SortByRelevance" : ("orderby", "relevance"), 
                      "SortByNewest" : ("orderby", "published"), 
                      "SortByViewCount" : ("orderby", "viewCount"),
                      }
  
      
    def keywords(self):
      return self.m_keywords
   
    def setKeywords(self, keywords):
      self.m_keywords = keywords.replace(" ", "+")
      
    
    def author(self):
      return self.m_author
    
    def setAuthor(self, author):
      self.m_autor = author
      
    def sortBy(self):
      return self.m_sortBy
    
    def setSortBy(self, sortBy):
      self.m_sortBy = sortBy
      