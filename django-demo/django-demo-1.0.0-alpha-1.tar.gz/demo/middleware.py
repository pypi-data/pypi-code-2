from demo.exceptions import DatabaseLimit, DatabaseExpired
from demo.models import SessionDatabase
from demo import settings as demo_settings
from demo.shared import THREAD_LOCALS
from django.conf import settings
from django.shortcuts import render_to_response


class DemoMiddleware(object):
    def process_request(self, request):
        if demo_settings.ALLOW_SHARE and demo_settings.SHARE_PARAMETER in request.GET:
            try:
                THREAD_LOCALS.database = SessionDatabase.objects.share(request)
            except DatabaseExpired:
                return render_to_response('demo/database_expired.html')
        try:
            THREAD_LOCALS.database = SessionDatabase.objects.get_db_name(request)
        except DatabaseLimit:
            data = {'next_death': SessionDatabase.objects.get_next_death()}
            return render_to_response('demo/database_limit.html', data)
        request.demo_session = request.session.session_key
        
    def process_response(self, request, response):
        if not hasattr(request, 'demo_session'):
            return response # error happened!
        if request.demo_session != request.session.session_key:
            SessionDatabase.objects.reattach(request.demo_session, request.session.session_key)
        THREAD_LOCALS.database = None
        return response