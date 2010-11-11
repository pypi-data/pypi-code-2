from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render_to_response
from django.template import RequestContext

from genericforeignkey.utils import get_objects_of_content_type


def generic_object_list(request):
    content_type_id = request.GET.get('content_type_id', None)
    content_type = ContentType.objects.get(pk=content_type_id)
    objs = get_objects_of_content_type(request, content_type=content_type)
    return render_to_response('genericforeignkey/object_list.html',
                              {'objs': objs,
                               'content_type': content_type},
                              context_instance=RequestContext(request))
