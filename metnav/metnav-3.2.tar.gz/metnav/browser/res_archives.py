# -*- coding: utf-8 -*-
## Copyright (C) 2009 Ingeniweb - Alter Way Solutions - all rights reserved
## No publication or distribution without authorization.

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from DateTime import DateTime

class res_archives(BrowserView):

    def archives(self, date_archives='', nb_limit=0, start=0, output='page'):
        context = self.context
        pp_tool = getToolByName(context, 'portal_properties')
        mn_tool = getToolByName(context, 'portal_metadataNav')
        affiche_mois= pp_tool.metnav_properties.getProperty('ARCHIVE_MOIS')
            
        #EPOC = "1900-01"
        #if date_archives >= DateTime().strftime('%Y-%M') or date_archives <= EPOC:
        #    date_archives = (DateTime() - 31).strftime('%Y-%M')
        if affiche_mois == True:

            news_params_dict = {'XSL':output,
                                'DATE_ARCHIVES':date_archives,
                                'NB_LIMIT':nb_limit,
                                'START':start,
                                'XSL_PARAMS':{'rss.title':"Archives de %s/%s" % (date_archives.split('-')[1],date_archives.split('-')[0]),
                                              'rss.desc':'Archives du mois',
                                              'rss.copyright':'Mon établissement',},
                               }
        else:

            news_params_dict = {'XSL':output,
                                'DATE_ARCHIVES':date_archives,
                                'NB_LIMIT':nb_limit,
                                'START':start,
                                'XSL_PARAMS':{'rss.title':"Archives de %s" % (date_archives),
                                              'rss.desc':'Archives de l\'année',
                                              'rss.copyright':'Mon établissement',},
                               }      

        query = (str(context.xq_archives) % mn_tool.getQueryParams(news_params_dict, context.REQUEST))
        #query = str(context.xq_archives) % {'DATE_ARCHIVES':date_archives,}
        
        da = mn_tool.getDA()
        res = da.query(query, object_only=1)

        return str(res)

