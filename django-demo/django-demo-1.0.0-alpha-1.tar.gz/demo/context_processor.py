from demo.models import SessionDatabase
from demo.settings import SHARE_PARAMETER

def demo(request):
    return {
        'DEMO_DEATH': SessionDatabase.objects.get_death(request),
        'DEMO_SHARE_URL': '%s?%s=%s' % (request.path, SHARE_PARAMETER, request.session.session_key) 
    }