# Create your views here.
from shorturls.models import Shorturls
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404

def index(request, shortname):
    p = get_object_or_404(Shorturls, shortname=shortname)
    return HttpResponseRedirect(p.url)
