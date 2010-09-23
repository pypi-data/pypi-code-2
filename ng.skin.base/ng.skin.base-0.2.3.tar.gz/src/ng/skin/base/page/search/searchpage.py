### -*- coding: utf-8 -*- #############################################
#######################################################################
"""MixIn class for searchpage.

$Id: searchpage.py 53378 2009-07-05 20:46:14Z cray $
"""
__author__  = "Andrey Orlov 2006 12 05"
__license__ = "GPL"
__version__ = "$Revision: 53378 $"

import zope.component
from zope.app import zapi
from zope.app.catalog.interfaces import ICatalog
from urllib import quote
from zope.publisher.browser import Record
from ng.adapter.path.interfaces import IPath
from ng.adapter.pager.resultset2pagersourceadapter import ResultSet2PagerSourceAdapter
from ng.adapter.pager.interfaces import IPager
from ng.adapter.adaptiveurl.adaptiveurl import adaptiveURL
from zope.app.securitypolicy.interfaces import IPrincipalPermissionMap
import zope.app.securitypolicy.zopepolicy
import re

class Participation(object) :
    interaction = None
    def __init__(self,principal) :
        self.principal = principal

def check(context,request) :
    interaction = zope.app.securitypolicy.zopepolicy.ZopeSecurityPolicy()
    participation = Participation(request.principal)
    interaction.add(participation)
    return interaction.checkPermission("zope.ManageContent",context)

class Search(object) :

    @property
    def nextkeyword(self) :
        if "keyword" in self.request.form :
            return str(self.request.form['keyword']['any_of'][0])
        elif "name" in self.request.form :
            return str(self.request.form['name']['any_of'][0])
        return self.request.form.get('common','')

    @property
    def quotenextkeyword(self) :
        return quote(re.sub("\s+"," ",self.nextkeyword.strip()))
    
    @property
    def pager(self) :
        d = {}
        for key,value in self.request.form.items() :
            if key in ['x','y',''] :
                continue
            
            if isinstance(value,Record) :
                value = dict(value) 

            d[str(key)] = value

        try :
            del d['current']
        except KeyError :
            pass

        if 'keyword' in d :
            d['keyword']['any_of'] = (re.sub("\s+"," ",d['keyword']['any_of'][0]).strip().lower(),)
        elif 'name' in d :
            d['name']['any_of'] = (re.sub("\s+"," ",d['name']['any_of'][0].strip()),re.sub("\s+"," ",d['name']['any_of'][0]).lower().strip())            
        elif 'urlpath' in d :            
            path=IPath(self.context).path
            d['urlpath'] = (path,path+u'\xff')
        
        if 'nickname' in d and not d['nickname'] :
            del d['nickname']

        if 'email' in d and not d['email'] :
            del d['email']
        
        crosswiki = None
        if 'crosswiki' in d :
            crosswiki = d['crosswiki']
            del d['crosswiki']
            
        res = zapi.getUtility(ICatalog,context=self.context).searchResults(**d)        
        pagersource = ResultSet2PagerSourceAdapter(res)

        if len(res) == 0 :
            if "keyword" in self.request.form :
                dictionary = zapi.getUtility(
                      zope.app.container.interfaces.IContainer,
                      name="Main",context=self.context)['dictionary']
                if check(dictionary,self.request) :
                    self.request.response.redirect(
                      adaptiveURL(dictionary,self.request)
                      +"/+/AddDictionaryItem.html=?field.keyword.0.=%(keyword)s&field.keyword.count=1&field.title=%(keyword)s&crosswiki=%(crosswiki)s" % { 'keyword': self.quotenextkeyword,  'crosswiki' : crosswiki } ) 
                elif crosswiki :
                    self.request.response.redirect("%(crosswiki)s/@@searchpage.html?query=%(keyword)s&predicate=keyword" % { 'keyword': self.quotenextkeyword, 'crosswiki' : crosswiki } )
            elif "name" in self.request.form :
                url = adaptiveURL(self.context,self.request)
                if check(self.context,self.request) :
                    self.request.response.redirect(url+"/+/AddArticle.html=?field.title="+self.quotenextkeyword)

        if len(res) == 1 :
            self.request.response.redirect(adaptiveURL(
                pagersource[pagersource.keys()[0]],
                self.request)) 
            
        return pagersource
                                       
        
