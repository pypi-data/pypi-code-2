#! -*- coding: UTF-8 -*-
from Acquisition import aq_inner
from zope.interface import implements
from zope.component import adapts
from zope.annotation.interfaces import IAnnotations
from persistent.interfaces import IPersistent

from Products.PyConBrasil.interfaces import INumberator, INumbered
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from persistent.mapping import PersistentMapping

SEED_NUM_KEY_PREFIX = 'pyconbrasil.number'
MAP_NUM_KEY_PREFIX = 'pyconbrasil.numbers.map'
NUM_KEY_PREFIX = 'pyconbrasil.seed_number'

class PloneNumberator(object):
    implements(INumberator)
    adapts(IPloneSiteRoot)

    def __init__(self, context):
        self.context = context

    def _annotation(self):
        return IAnnotations(self.context)

    def get_current(self):
        ann_obj = self._annotation()
        return ann_obj.get(SEED_NUM_KEY_PREFIX, 0)

    def get_UID(self, number):
        ann_obj = self._annotation()
        return ann_obj[MAP_NUM_KEY_PREFIX][number]

    def number_it(self, content):
        ann_obj = self._annotation()
        number = self._get_next()
        num_map = ann_obj.setdefault(MAP_NUM_KEY_PREFIX,  PersistentMapping({}))
        num_map[number] = content.UID()

        return number
    
    def _get_next(self):
        ann_obj = self._annotation()
        try:
            ann_obj[SEED_NUM_KEY_PREFIX] += 1
        except KeyError:
            ann_obj[SEED_NUM_KEY_PREFIX] = 1
        return ann_obj[SEED_NUM_KEY_PREFIX]

class Numbered(object):
    adapts(IPersistent)
    implements(INumbered)

    def __init__(self, context):
        self.context = context 

    def _annotation(self):
        return IAnnotations(self.context)

    def _get_numerator(self):
        portal_url = getToolByName(self.context, 'portal_url')
        plone = portal_url.getPortalObject()

        return INumberator(plone)

    def _create_number(self):
        numerator = self._get_numerator()
        num = numerator.number_it(self.context)

        ann_obj = self._annotation()
        ann_obj[NUM_KEY_PREFIX] = num
        return num

    def get_number(self):
        try:
            return self._annotation()[NUM_KEY_PREFIX]
        except KeyError:
            return self._create_number()


class URLNumber(BrowserView):

    def verification_url(self, year):
	context = aq_inner(self.context)
        portal_url = getToolByName(context, 'portal_url')
        portal = portal_url.getPortalObject()
	n = INumbered(context).get_number()
    	return "%s/%s/verifica?n=%s" % (portal_url(), year, n) 


class CheckNumber(BrowserView):
    nome = ''
    number = 0

    def __call__(self):
        self.update()
        return self.index()

    def update(self):
        portal_url = getToolByName(self.context, 'portal_url')
        portal = portal_url.getPortalObject()
        numberator = INumberator(portal)
        self.number = int(self.request.get('n', 0))
        try:
            uid = numberator.get_UID(self.number)
        except KeyError:
            return 

        catalog = getToolByName(portal, 'portal_catalog')
        results = catalog(UID=uid)
        if results:
            content = results[0].getObject()
            self.nome = getattr(content, 'getNome', getattr(content, 'Title', ''))
            if callable(self.nome):
                self.nome = self.nome()



