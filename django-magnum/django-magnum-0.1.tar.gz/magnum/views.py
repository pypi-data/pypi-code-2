from django.conf import settings
from django.http import Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views import static
from django.views.decorators.cache import cache_page
from magnum.package_index import DjangoCachingPackageIndex
import os.path


INDEX = DjangoCachingPackageIndex(
    serve_path=settings.MAGNUM_SERVE_PATH,
    cache_path=settings.MAGNUM_CACHE_PATH,
    remote_url=settings.MAGNUM_REMOTE_URL,
    remote_package_names_lifetime=settings.MAGNUM_REMOTE_PACKAGE_NAMES_LIFETIME,
    remote_dist_names_lifetime=settings.MAGNUM_REMOTE_DIST_NAMES_LIFETIME,
)


@cache_page(INDEX.remote_package_names_lifetime)
def index(request, template='magnum/index.html'):
    package_names = sorted(INDEX.package_names(), key=lambda name: name.lower())
    
    return render_to_response(template, {
        'package_names': package_names,
    }, context_instance=RequestContext(request))


@cache_page(INDEX.remote_dist_names_lifetime)
def package(request, package_name, template='magnum/package.html'):
    filenames = sorted(INDEX.dist_names(package_name), reverse=True)
    
    return render_to_response(template, {
        'package_name': package_name,
        'filenames': filenames,
    }, context_instance=RequestContext(request))


def download_dist(request, package_name, filename):
    try:
        local_filename = INDEX.dist_filename(package_name, filename)
    except INDEX.DistributionNotFound, exc:
        raise Http404(unicode(exc))
    
    return static.serve(request,
        path=os.path.basename(local_filename),
        document_root=os.path.dirname(local_filename),
    )
