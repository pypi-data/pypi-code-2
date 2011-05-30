# -*- coding: utf-8 -*-
"""Define a browser view for the Archive Text content type. In the FTI 
configured in profiles/default/types/*.xml, this is being set as the default
view of that content type.
"""

from Acquisition import aq_inner
from zope.interface import implements
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from plone.memoize.instance import memoize

from datetime import datetime, date

class BluethemeEventListingView(BrowserView):
    """Listing view for events
    """
    
    html_template = ViewPageTemplateFile('templates/event_listing.pt')

    def __call__(self):
        return self.html_template()
        
    def nice_event_url(self,event_url):
        """url should not be to long
        """
        url_max_length = 65
        nice_event_url=event_url.lstrip('http://').lstrip('https://')
        if len(nice_event_url) >= url_max_length: 
            nice_event_url = nice_event_url[:url_max_length] + '(...)'
        
        return nice_event_url        
    
    @memoize
    def actual(self):
        now = datetime.now()
        return {'year':now.year , 'month':now.month , 'day':now.day}

    @memoize
    def all_years(self):
        now = datetime.now()
        years = [ now.year-2, now.year-1, now.year, now.year+1, now.year+2, now.year+3 ]
        return years
        
    @memoize    
    def count_events(self,year):
        start  = datetime(year,1,1)
        end    = datetime(year+1,1,1)

        context = aq_inner(self.context)
        search = getToolByName(context,"portal_catalog")
        
        q = search(    
              portal_type='Event',
              start = {
                 "query" : [start,end], 
                 "range": "minmax"}, 
                 )   
        return len(q)
    
    @memoize        
    def month_of_year(self):
        month_of_year = []                                                
        for i in range(1,13):
            month_of_year.append(  date(2010, i, 1).strftime('%b').lower()  )                            
        return month_of_year    
        
    @memoize
    def count_monthly_events(self,year):
        """returns a list with 12 values [3,12,5,8,0,0,...]
           ex. jan:3, feb:12, mar:5 etc
        """
        item_count = [0]*12
        context = aq_inner(self.context)
        search = getToolByName(context,"portal_catalog")
        if year:
            for month in range(1,13):
                start  = datetime(year,month,1)
                
                if month >= 12:
                    end    = datetime(year+1,1,1)
                else:
                    end    = datetime(year,month+1,1)
                
                res    = search(portal_type='Event',start = {"query" : [start,end], "range": "minmax"})
                if res:
                    item_count[month-1] = len(res) 
            
        return item_count
        
    @memoize       
    def items_of_period(self,folderContents,year,month,latest=3,show_only_upcoming_dates=True):
        """ Returns events of a given period
        """
        res = []
        context = aq_inner(self.context)
        search = getToolByName(context,"portal_catalog")
        
        if not year:
            year  = self.request.get("y")
        if not month:
            month = self.request.get("m")
                
        if year and month:
            # all events of a given month 
            start  = datetime(year,month,01)
            if month < 12:
                end    = datetime(year,month+1,01)
            else:
                end    = datetime(year+1,1,1)
            
        elif year:
            # all events of the year
            if year == self.actual()['year'] and show_only_upcoming_dates:
                start  = datetime.now()
            else:
                start  = datetime(year,1,1)
            end    = datetime(year+1,1,1)

        else:
            # return latest events
            res = search(    
                    portal_type='Event',
                    sort_on="start", 
                    sort_order="ascending")
            if res:
                return res[:latest]
            else:
                return ""
        
        # Catalog search ---
        res    = search(    
                    portal_type='Event',
                    start = {
                                "query" : [start,end], 
                                "range": "minmax"}, 
                    sort_on="start", 
                    sort_order="ascending")
        return res
        
        
    def getPublicationDate(self,item):
        try:
            # only press release has extradate
            context = aq_inner(self.context)                    
            pub_date = item.getExtradate() or item.toLocalizedTime(item.EffectiveDate())
            return pub_date
        except:
            return ""

