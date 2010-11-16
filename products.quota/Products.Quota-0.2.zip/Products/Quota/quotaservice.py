from zope.component import getUtility
from zope.interface import implements
from Products.Quota.interfaces import IQuotaRecurse, IQuotaAware, \
    IQuotaService, IQuotaSizer, IQuotaSettings


class DefaultQuotaService(object):

    implements(IQuotaService)

    def get_increment(self, ob):
        try:
            sizer = IQuotaSizer(ob)
        except TypeError:
            return 0
        return sizer.get_increment()

    def get_size(self,ob):
        try:
            sizer = IQuotaSizer(ob)
        except TypeError:
            return 0
        return sizer.get_size()

    def get_total(self, ob, increment=0):
        try:
            sizer = IQuotaSizer(ob)
        except TypeError:
            return 0
        return sizer.get_total(increment)

    def recurse_quota(self, container, size):
        try:
            recurser = IQuotaRecurse(container)
        except TypeError:
            return
        recurser.recurse_quota(size)

    def max_size(self, ob):
        assert(IQuotaAware.providedBy(ob))
        quota = float(ob.size_limit)
        qs = getUtility(IQuotaSettings)
        enforce = qs.enforce_quota
        gen_quota = float(qs.size_limit)
        if quota > -1 and enforce:
            quota = min(quota, gen_quota)
        elif quota == -1:
            quota = gen_quota
        return quota*1024*1024

    def size_threshold(self, ob):
        assert(IQuotaAware.providedBy(ob))
        threshold = float(ob.size_threshold)
        qs = getUtility(IQuotaSettings)
        enforce = qs.enforce_quota
        gen_threshold = float(qs.size_threshold)
        if threshold > 0 and enforce:
            threshold = min(threshold, gen_threshold)
        elif threshold == 0:
            threshold = gen_threshold
        return threshold*1024*1024

