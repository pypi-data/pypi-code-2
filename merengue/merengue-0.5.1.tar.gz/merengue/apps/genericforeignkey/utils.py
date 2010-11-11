from django.contrib.contenttypes.models import ContentType


def get_objects_of_content_type(request, content_type_id=None, content_type=None):
    content_type = content_type or ContentType.objects.get(pk=content_type_id)
    get = request.GET.copy()
    del(get['content_type_id'])
    request.GET = get
    return content_type.model_class().objects.all()
