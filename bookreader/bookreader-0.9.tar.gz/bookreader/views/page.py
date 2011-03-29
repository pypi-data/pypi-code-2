from urllib import urlopen

from django.conf import settings
from django.http import *
from django.shortcuts import get_object_or_404, get_list_or_404, redirect
from django.views.generic import list_detail

from bookreader.models import Book, Page


def view(request, object_id, **kwargs):
    kwargs.setdefault('template_object_name','page')
    return list_detail.object_detail(request, Page.objects.all(),
                                     object_id=object_id, **kwargs)

def jp2_metadata(request):
    if not 'rft_id' in request.REQUEST:
        return HttpResponseBadRequest('rft_id required')
    
    url = '%s?url_ver=Z39.88-2004&rft_id=%s&svc_id=info:lanl-repo/svc/getMetadata' % (settings.DJATOKA_BASE_URL, request.REQUEST['rft_id'],)
    
    try:
        return HttpResponse(urlopen(url).read(), mimetype="application/javascript")
    except:
        return HttpResponse('{}', mimetype="application/javascript")

def annotations(request, object_id, **kwargs):
    kwargs.setdefault('template_name','bookreader/annotation/page.html')
    return view(request, object_id, **kwargs)

def printable(request, object_id):
    from bookreader.templatetags.bookreader_djatoka import DjatokaResolverNode
    
    page = get_object_or_404(Page, pk=object_id)
    
    if not page.jp2:
        return HttpResponseNotFound('Page is missing')
    
    return HttpResponseRedirect(DjatokaResolverNode('"%s"' % (page.jp2,),
                                                    ['svc.scale=1.0']).render({}))
