from django.utils import simplejson
from django.views.generic.list_detail import object_list, object_detail
from django.views.generic.create_update import create_object, update_object, delete_object
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.core import serializers
from django.http import HttpResponse
from django.utils import simplejson
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.shortcuts import redirect

from locationbase.models import Location


def list(request):
    return render_to_response('locationbase/location/list.html', dict(locations=Location.objects.all()), context_instance=RequestContext(request))


def geocoding(request):
    return render_to_response('locationbase/location/geocoding.html', {}, context_instance=RequestContext(request))

@login_required
def location_from_geocoding(request):
    name = "Unknown"
    if request.is_ajax():
        try:
            name = request.POST.get('name', None)
            if not name:
                raise Exception("Missing name of location.")
            
            data = simplejson.loads(request.POST.get('params', ''))
            if data.get('Pa'):
                longitude = data.get('Pa', None)
                latitude = data.get('Oa', None)
            else:
                longitude = data.get('Oa', None)
                latitude = data.get('Na', None)

            if not longitude or not latitude:
                raise Exception("Missing latitude (%s) or longitude (%s). Add location manually." % (latitude, longitude))
            
            Location(
                name = name,
                longitude = longitude,
                latitude = latitude,
                location = "%s, %s" % (latitude, longitude),
                owner=request.user,
                street_address = request.POST.get('street_address', ""),
                street_number = request.POST.get('street_number', ""),
                country_name = request.POST.get('country', ""),
                city = request.POST.get('city', ""),
                province_state = request.POST.get('state', ""),
                zip_code = request.POST.get('postal_code', ""),
                tagname = '',
                country_code ='',
                altitude = 0
            ).save()
            return HttpResponse("'%s' was created successfully." % name)
        except Exception, e:
            print "Exceptionem", e
            return HttpResponse("Error creating location: %s because %s." % (name, e))
    return HttpResponse("This is an ajax view.")
