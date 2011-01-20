from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse
from models import Panorama, PanoramaNote
from django.template import RequestContext
import simplejson
# Create your views here.

def panorama_json(request,pk):
    panorama= get_object_or_404(Panorama, pk=pk)
    mimetype = 'application/javascript'
    data_dict = {'imgurl': panorama.image.url,
                 'width': panorama.image.width,
                 'height': panorama.image.height}
    data = simplejson.dumps(data_dict)
    return HttpResponse(data,mimetype)

def show_note(request,pk):
    panoramanote = get_object_or_404(PanoramaNote, pk=pk)
    context = RequestContext(request, {'panoramanote': panoramanote})
    return render_to_response('panorama/show_panoramanote.html', context)
