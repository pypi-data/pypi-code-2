from django.shortcuts import render_to_response
from django.template.context import RequestContext
from models import *

def index(request):
    return render_to_response('index.html', {'photos': Photo.objects.all()}, context_instance=RequestContext(request))
