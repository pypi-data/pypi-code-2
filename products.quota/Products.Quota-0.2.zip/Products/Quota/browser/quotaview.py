from zope.component import getUtility
from Products.Five import BrowserView
from Products.Quota.interfaces import IQuotaService


class QuotaView(BrowserView):

    def context():
        def get(self):
            return self._context[0]
        def set(self, context):
            self._context = [context]
        return property(get, set)
    context = context()

    def quota(self):
        sizer = getUtility(IQuotaService)
        quota = sizer.max_size(self.context)
        return round(float(quota)/(1024*1024), 1)

    def hard_quota(self):
        sizer = getUtility(IQuotaService)
        quota = sizer.max_size(self.context)
        threshold = sizer.size_threshold(self.context)
        hard_limit = quota + threshold
        return round(float(hard_limit)/(1024*1024), 1)

    def size(self):
        sizer = getUtility(IQuotaService)
        size = sizer.get_size(self.context)
        return round(float(size)/(1024*1024), 1)

    def total(self):
        sizer = getUtility(IQuotaService)
        total = sizer.get_total(self.context)
        return round(float(total)/(1024*1024), 1)
