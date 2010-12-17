from django.http import Http404, HttpResponseNotAllowed, HttpResponseRedirect
from django.template import RequestContext

from urlreduce.models import Link


def forward( request, id ):
    """
    View Definition for the Homepage
    """
    if request.method == 'GET':  
        try:
            link = Link.objects.get( short_url = id )
            return HttpResponseRedirect( link.url )
        except Link.DoesNotExist:
            return Http404( "Shortlink does not exist for the requested url: %s" % url )
    else:
        return HttpResponseNotAllowed( ['GET'] )

    