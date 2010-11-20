from django.core.exceptions import ObjectDoesNotExist
from piston.handler import BaseHandler
from piston.utils import rc, throttle, require_mime
# >>> rc.CODES.keys()
# ['CREATED', 'DELETED', 'THROTTLED', 'FORBIDDEN', 'NOT_IMPLEMENTED', 'BAD_REQUEST', 'DUPLICATE_ENTRY', 'NOT_HERE', 'NOT_FOUND', 'ALL_OK']

#from eyeswebapp.core.models import Host
from eyeswebapp.core.models import Monitor
from util.monitor import validate_return_dictionary
import re
#from eyeswebapp.core.models import Datastore

class MonitorHandler(BaseHandler):
    """
    Handler entrypoint for monitors - currently without Authentication
    """
    allowed_methods = ('GET', )
    fields = ('id', 'lastupdate', 'plugin_name', 'name', 'json_argset', 'nextupdate', 'timeout')
    # fields = ('title', ...)
    # exclude = ('id', re.compile(r'^private_'))
    model = Monitor
    
    #@throttle(5, 10*60) # allow 5 times in 10 minutes
    def read(self, request, monitor_id=None):
        """ reads all monitors pending, or a specific monitor if provided"""
        if monitor_id is None:
            base_api = "/api/monitor/%d/"
            list_of_uri = []
            for pending_mon in Monitor.objects.pending_update():
                list_of_uri.append(base_api % pending_mon.id)
            return list_of_uri
        try:
            mon = Monitor.objects.get(pk=monitor_id)
            return mon
        except ObjectDoesNotExist:
            return rc.NOT_FOUND
        
class MonitorResultHandler(BaseHandler):
    """
    Handler entrypoint for processing results of a monitor invocation - JSON structure
    """
    allowed_methods = ('POST', )
    #fields = ('monitor_id', 'json_resultset')
    @require_mime('json')
    def create(self, request, monitor_id):
        """ processes the results of a monitor being invoked - storing the resulting data"""
        mon = None
        try:
            mon = Monitor.objects.get(pk=monitor_id)
        except ObjectDoesNotExist:
            return rc.NOT_FOUND
        if request.content_type == 'application/json':
            data = request.data
            was_stored = mon.store_dict_results(data, debug=True)
            if (was_stored):
                return rc.CREATED
        return rc.BAD_REQUEST

# class DatastoreHandler(BaseHandler):
#     """
#     Handler entrypoint for directly reading/writing datastore entries
#     """
