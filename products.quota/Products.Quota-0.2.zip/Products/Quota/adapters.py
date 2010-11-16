from Acquisition import aq_inner, aq_parent
from persistent.mapping import PersistentMapping
from zExceptions import Redirect
from zope.component import adapts, getUtility
from zope.interface import implements
from zope.annotation.interfaces import IAnnotations
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.interfaces import IBaseFolder, IBaseObject
from Products.Quota import QuotaMessageFactory as _
from Products.Quota.interfaces import IQuotaRecurse, IQuotaEnforcer, \
    IQuotaAware, IQuotaService, IQuotaSizer


class ATQuotaSizer(object):
    implements(IQuotaSizer)
    adapts(IBaseObject)

    def __init__(self, context):
        self.context = context

    def get_increment(self):
        ob = self.context
        size = 0
        for f in ob.schema.fields():
            size += f.get_size(ob)
        ann = IAnnotations(ob)
        if ann.has_key('quota'):
            old_size = ann['quota']['size']
        else:
            ann['quota'] = PersistentMapping()
            old_size = 0
        ann['quota']['size'] = size
        return size - old_size

    def get_size(self):
        ob = self.context
        ann = IAnnotations(ob)
        if ann.has_key('quota'):
            return ann['quota']['size']
        else:
            return self.get_increment()

    def get_total(self, increment=0):
        ob = self.context
        if not IQuotaAware.providedBy(ob):
            return 0
        ann = IAnnotations(ob)
        qs = getUtility(IQuotaService)
        # get the size outside of the condition below,
        # in case there is not yet an annotation
        size = qs.get_size(ob)
        if not ann['quota'].has_key('total'):
            ann['quota']['total'] = size
        ann['quota']['total'] += increment
        return int(ann['quota']['total'])


class QuotaRecurse(object):
    implements(IQuotaRecurse)
    adapts(IBaseFolder)

    def __init__(self, context):
        self.context = context

    def recurse_quota(self, increment):
        try:
            enforcer = IQuotaEnforcer(self.context)
        except TypeError:
            pass
        else:
            enforcer.enforce_quota(increment)
        parent = aq_parent(aq_inner(self.context))
        try:
            recurser = IQuotaRecurse(parent)
        except TypeError:
            pass
        else:
            recurser.recurse_quota(increment)


class QuotaEnforcer(object):
    implements(IQuotaEnforcer)
    adapts(IQuotaAware)

    def __init__(self, context):
        self.context = context

    def enforce_quota(self, increment):
        qs = getUtility(IQuotaService)
        total = qs.get_total(self.context, increment)
        max_size = qs.max_size(self.context)
        threshold = qs.size_threshold(self.context)
        hard_max = max_size + threshold
        if max_size > -1:
            putils = getToolByName(self.context, 'plone_utils')
            if total > hard_max:
                # first, clear previous status messages
                old = putils.showPortalMessages()
                putils.addPortalMessage(_(u'ERROR: QUOTA EXCEEDED'))
                raise Redirect, '%s/quota?increment=%d' % \
                                 (self.context.absolute_url(),
                                 round(float(increment)/(1024*1024), 1))
            elif total > max_size:
                # first, clear previous status messages
                old = putils.showPortalMessages()
                putils.addPortalMessage(_(u'WARNING: SOFT QUOTA EXCEEDED'))


