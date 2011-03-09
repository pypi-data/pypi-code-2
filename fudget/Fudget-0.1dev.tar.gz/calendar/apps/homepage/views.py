from django.shortcuts import render_to_response, get_object_or_404
from django.db.models import Avg
from django.template import RequestContext

def index(request, template_name="homepage/index.html"):
	return render_to_response(template_name, {}, context_instance=RequestContext(request))