# -*- coding:utf-8 -*-
""" support for HelpCenter templates """

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from DateTime import DateTime
import types

class DynaPageView(BrowserView):
    """ support for DynaPage templates """

    __call__ = ViewPageTemplateFile('dynapage_view.pt')

    def __init__(self, context, request):
        """ set up a few convenience object attributes """

        self.context = context
        self.request = request

    def hasFrontpageImage(self):
        try:
            if not self.context.inheritImage and 'etusivu.jpg' in self.context.objectIds():
                return True
            elif self.context.inheritImage and self.context['etusivu.jpg']:
                return True
            else:
                return False
        except KeyError:
            return False

    def getListPath(self, refs):
        """ Digs the referenced objects path """

        paths = {
            'paths': [],
            'uids': []
            }

        for ref in refs:
            try:
                obj = self.context.reference_catalog.lookupObject(ref)
                path = "/".join(obj.getPhysicalPath())
                if path:
                    paths['paths'].append(path)
		    paths['uids'].append(ref)

            except AttributeError:
                return None

        return paths


    def getActiveLists(self):
        """Returns lists which should be visible."""

        activeLists = []

        positions = ['first_list_position','second_list_position','third_list_position','fourth_list_position']

        topPosition = 0
        bottomPosition = 0

        if self.context.first_list_active:
            activeLists.append({
                'list_position' : self.context.first_list_position,
                'list_style' : self.context.first_list_style,
                'list_title' : self.context.first_list_title,
                'list_order' : self.context.first_list_order,
                'list_order_by' : self.context.first_list_order_by,
                'list_types' : self.context.first_list_types,
                'list_state' : self.context.first_list_state,
                'list_custom_view_fields' : self.context.first_list_custom_view_fields,
                'list_keywords' : self.context.first_list_keywords,
                'list_items' : self.context.first_list_items,
                'list_path'  : self.getListPath(self.context.getRawFirst_list_path()),
                'rss_title'  : self.context.getFirst_list_rss_title(),
                'list_edit'  : 'atct_edit?fieldset=1st_list',
            })

        if self.context.second_list_active:
            activeLists.append({
                'list_position' : self.context.second_list_position,
                'list_style' : self.context.second_list_style,
                'list_title' : self.context.second_list_title,
                'list_order' : self.context.second_list_order,
                'list_order_by' : self.context.second_list_order_by,
                'list_types' : self.context.second_list_types,
                'list_state' : self.context.second_list_state,
                'list_custom_view_fields' : self.context.second_list_custom_view_fields,
                'list_keywords' : self.context.second_list_keywords,
                'list_items' : self.context.second_list_items,
                'list_path'  : self.getListPath(self.context.getRawSecond_list_path()),
                'rss_title'  : self.context.getSecond_list_rss_title(),
                'list_edit'  : 'atct_edit?fieldset=2nd_list',
            })

        if self.context.third_list_active:
            activeLists.append({
                'list_position' : self.context.third_list_position,
                'list_style' : self.context.third_list_style,
                'list_title' : self.context.third_list_title,
                'list_order' : self.context.third_list_order,
                'list_order_by' : self.context.third_list_order_by,
                'list_types' : self.context.third_list_types,
                'list_state' : self.context.third_list_state,
                'list_custom_view_fields' : self.context.third_list_custom_view_fields,
                'list_keywords' : self.context.third_list_keywords,
                'list_items' : self.context.third_list_items,
                'list_path'  : self.getListPath(self.context.getRawThird_list_path()),
                'list_edit'  : 'atct_edit?fieldset=3rd_list',
                'rss_title'  : self.context.getThird_list_rss_title(),
            })

        if self.context.fourth_list_active:
            activeLists.append({
                'list_position' : self.context.fourth_list_position,
                'list_style' : self.context.fourth_list_style,
                'list_title' : self.context.fourth_list_title,
                'list_order' : self.context.fourth_list_order,
                'list_order_by' : self.context.fourth_list_order_by,
                'list_types' : self.context.fourth_list_types,
                'list_state' : self.context.fourth_list_state,
                'list_custom_view_fields' : self.context.fourth_list_custom_view_fields,
                'list_keywords' : self.context.fourth_list_keywords,
                'list_items' : self.context.fourth_list_items,
                'list_path'  : self.getListPath(self.context.getRawFourth_list_path()),
                'list_edit'  : 'atct_edit?fieldset=4th_list',
                'rss_title'  : self.context.getFourth_list_rss_title(),
            })

        return activeLists


    def getListsPosition(self, position="top"):
        """Returns lists which should be positioned to top of the page."""

        activeLists = self.getActiveLists()

        listsPosition = []

        if 1 in activeLists and position in self.context.first_list_position:
            listsPosition.append(1)
        if 2 in activeLists and position in self.context.second_list_position:
            listsPosition.append(2)
        if 3 in activeLists and position in self.context.third_list_position:
            listsPosition.append(3)
        if 4 in activeLists and position in self.context.fourth_list_position:
            listsPosition.append(4)

        return listsPosition


    def getListData(self):

        path = '/'.join(self.context.getPhysicalPath()[:-1])

        lists = self.getActiveLists()
        catalogData = []
        now = DateTime()

        topPosition = 0
        bottomPosition = 0

        for list in lists:
            # Create query dictionary
            query = {}
            query['portal_type'] = list['list_types']
            query['path'] = list['list_path']['paths']
            query['review_state'] = list['list_state'] or ""
            query['sort_on'] = list['list_order_by']
            query['sort_order'] = list['list_order']
            query['effectiveRange'] = now
            query['sort_limit'] = list['list_items']

            if len(list['list_keywords']):
                query['Subject'] = list['list_keywords']

            catalog = self.context.portal_catalog.queryCatalog(query)[:list['list_items']]


            if len(catalog) > 0:

                # Remove the root from results if we're looking for folders
                # (for some reason the root is always included in the results)
                if 'Folder' in list['list_types']:
                    brainlist = [i for i in catalog]
                    catalog = []
                    for i in brainlist:
                        if i.UID not in list['list_path']['uids']:
                            catalog.append(i)
                
                rss_searchPath    = self.getSyndicationURL(
                    title         = list['rss_title'],
                    portal_types  = list['list_types'],
                    path          = list['list_path']['paths'],
                    keywords      = list['list_keywords'],
                    sort_on       = list['list_order_by'],
                    sort_order    = list['list_order'],
                    review_states = list['list_state'])

                catalogData.append({
                    'listObjects'   : catalog[:list['list_items']],
                    'position'      : list['list_position'],
                    'title'         : list['list_title'],
                    'fields'        : list['list_custom_view_fields'],
                    'rss'           : rss_searchPath,
                    'edit'          : list['list_edit'],
                })

                if list['list_position'] == 'top':
                    topPosition += 1
                else:
                    bottomPosition += 1

        if topPosition >= 3:
            top = "thirdWidthList"
        elif topPosition == 2:
            top = "halfWidthList"
        elif topPosition == 1:
            top = "fullWidthList"
        else:
            top = "fullWidthList"

        if bottomPosition >= 3:
            bottom = "thirdWidthList"
        elif bottomPosition == 2:
            bottom = "halfWidthList"
        elif bottomPosition == 1:
            bottom = "fullWidthList"
        else:
            bottom = "fullWidthList"

        return {'data': catalogData, 'top': top, 'bottom': bottom}


    def getSyndicationURL(self, sort_on=None, sort_order=None, portal_types=None, path=None, keywords=None, title=None, review_states=None):
        """ returns a URL for RSS feed of help doc types """
        try:
            search_path = ""
            if path and type(path) == types.ListType and len(path)>1:
                for p in path:
                    search_path += "&path=" + p
            elif path and type(path) == types.ListType and len(path)==1:
                search_path = "&path=%s" % path[0]
            elif path:
                search_path = "&path=%s" % path
            else:
                search_path = path
            url = self.context.absolute_url() + '/search_rss?title=%s&sort_on=%s&sort_order=%s%s' % (title, sort_on, sort_order, search_path)
            if review_states:
                url += '&' + ('&'.join(['review_state=%s' % s for s in review_states]))
            url += '&' + ('&'.join(['portal_type=%s' % s for s in portal_types]))
            if keywords:
                url += '&' + ('&'.join(['Subject=%s' % s for s in keywords]))

             # This would hide expired items for logged in users, but harms caching
#            now = DateTime()
#            url += '&effectiveRange=%s-%s-%s %s:%s' % (now.year(), now.month(), now.day(), now.hour(), now.minute())

            return url

        except AttributeError, e:
            print "JYUDynaPage - getSyndicationURL: AttributeError - %s" % e
            return None
