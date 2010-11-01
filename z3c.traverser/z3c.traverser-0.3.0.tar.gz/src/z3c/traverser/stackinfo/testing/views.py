from zope.traversing.browser.absoluteurl import absoluteURL

from z3c.traverser.stackinfo import interfaces

class StackInfoView(object):

    def __call__(self):
        url = absoluteURL(self, self.request)
        res = [u'Stack Info from object at %s:' % url]
        for consumer in interfaces.ITraversalStackInfo(
            self.request):
            res.append(u'consumer %s:' % consumer.__name__)
            for arg in consumer.arguments:
                res.append(u'%s = %r' % (arg, getattr(consumer, arg)))
        return u'\n'.join(res)
                
        
