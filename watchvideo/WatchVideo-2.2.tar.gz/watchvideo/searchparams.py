# -*- coding: utf-8 -*-
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

"""Based on Minitube's searchparams"""


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
      
