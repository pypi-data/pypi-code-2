from pystatsd import Client
from django.conf import settings

class DjangoStatsdMiddleware(object):
    """
    
    """
    def process_view(self, request, view_func, view_args, view_kwargs):
        
        start = time()
        
        if (hasattr(settings,'STATSD_SERVER') and hasattr(settings,'STATSD_PORT')):
            client = Client(settings.STATSD_SERVER, settings.STATSD_PORT)
        
        return None