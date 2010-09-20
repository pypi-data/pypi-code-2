import time
import string
from Acquisition import aq_inner
from zope.component import getUtility
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone.interfaces import IPloneSiteRoot
from collective.contentleadimage.config import IMAGE_FIELD_NAME
from collective.contentleadimage.leadimageprefs import ILeadImagePrefsForm
from Products.CMFCore.utils import getToolByName
from collective.flowplayer.interfaces import IFlowPlayable

class ColorContextWorkView(BrowserView):
    
    @property
    def prefs(self):
        portal = getUtility(IPloneSiteRoot)
        return ILeadImagePrefsForm(portal)

    def tag(self, obj, css_class='tileImage'):
        context = aq_inner(obj)
        field = context.getField(IMAGE_FIELD_NAME)
        if field is not None:
            if field.get_size(context) != 0:
                scale = self.prefs.desc_scale_name
                return field.tag(context, scale=scale, css_class=css_class)
        return ''

    def currenttime(self):
	return time.time()
    
    def trimDescription(self, desc):
	if len(desc) > 250: 
		res = desc[0:250]
		lastspace = res.rfind(" ")
		res = res[0:lastspace] + " ..."
		return res
	else:
		return desc

    def workGoto(self, toNext):
	catalog = getToolByName(self, 'portal_catalog')
	inner = self.context.aq_inner
	parent = inner.aq_parent
	parent_path = parent.getPhysicalPath()
	parent_url = '/'.join(parent_path)
	results = catalog.searchResults(path = {'query' : parent_url,'depth' : 1 }, sort_on = 'getObjPositionInParent',portal_type = ('Work'))
	current = self.context.absolute_url()
	prev = None
	next = None
	found = False
	for item in results:
		if not found:
			if item.getURL() == current:
				found = True
			else:
				prev = item.getURL()
		else:
			if item.portal_type == 'Work':
				next = item.getURL()
				break
	if toNext:
		if next is None:
			return None
		else:
			return next + '/view'
	else:
		if prev is None:
			return None
		else:
			return prev + '/view'

    def workGotoThumb(self, toNext):
	catalog = getToolByName(self, 'portal_catalog')
	inner = self.context.aq_inner
	parent = inner.aq_parent
	parent_path = parent.getPhysicalPath()
	parent_url = '/'.join(parent_path)
	results = catalog.searchResults(path = {'query' : parent_url,'depth' : 1 }, sort_on = 'getObjPositionInParent',portal_type = ('Work'))
	current = self.context.absolute_url()
	prev = None
	next = None
	found = False
	p_video = False
	n_video = False

	for item in results:
		if not found:
			if item.getURL() == current:
				found = True
			else:
				prev = item.getURL()
				
		else:
			if item.portal_type == 'Work':
				next = item.getURL()
				break
	if toNext:
		if next is None:
			return None
		else:
			return next + '/leadImage_mini'
	else:
		if prev is None:
			return None
		else:
			return prev + '/leadImage_mini'
