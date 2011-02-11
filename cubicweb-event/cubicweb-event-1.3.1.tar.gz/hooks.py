from cubicweb.selectors import is_instance
from cubicweb.sobjects.notification import ContentAddedView

class EventAddedView(ContentAddedView):
    """get notified from new events"""
    __select__ = is_instance('Event')
    content_attr = 'description'
