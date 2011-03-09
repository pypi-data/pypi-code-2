from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.utils import simplejson
from django.views.decorators.cache import never_cache

from staging import settings
from staging.utils import staging_manager


@never_cache
def staging_revision(request):
    revision = staging_manager.get_revision()
    result = {'revision': revision,
              'update_url': reverse(start_push)}
    return HttpResponse(simplejson.dumps(result), mimetype='text/plain')


@never_cache
def start_push(request):
    #success = staging_manager.start_server()
    success = True
    result = {'success': success,
              'next_url': reverse(make_push),
              'remote': False,
              'port': settings.STAGING_HG_SERVE_PORT}
    return HttpResponse(simplejson.dumps(result), mimetype='text/plain')


@never_cache
def make_push(request):
    url = request.GET.get('url')
    staging_manager.make_push(url)
    result = {'success': True,
              'next_url': reverse(finish_push),
              'remote': True}
    return HttpResponse(simplejson.dumps(result), mimetype='text/plain')


@never_cache
def finish_push(request):
    #staging_manager.end_server()
    staging_manager.staging_import()
    result = {'success': True}
    return HttpResponse(simplejson.dumps(result), mimetype='text/plain')


@never_cache
def download_repository(request):
    response = HttpResponse(staging_manager.make_bundle(), mimetype='application/zip')
    response['Content-Disposition'] = 'attachment; filename=bundle.hg'
    return response


@never_cache
def check_repository(request):
    if staging_manager.check_repository():
        answer = 'ok'
    else:
        answer = 'error'
    return HttpResponse(answer, mimetype='text/plain')
