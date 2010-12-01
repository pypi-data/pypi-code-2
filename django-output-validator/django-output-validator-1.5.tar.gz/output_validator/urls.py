from django.conf.urls.defaults import *
from output_validator.models import ValidationFailure

info_dict = {
    'queryset': ValidationFailure.objects.all(),
}

urlpatterns = patterns('',
    (r'^$',
        'django.views.generic.list_detail.object_list',
        dict(info_dict, allow_empty=True)),
    (r'^(?P<object_id>\d+)/$',
        'django.views.generic.list_detail.object_detail',
        info_dict),
    (r'^(?P<object_id>\d+)/delete/$',
        'output_validator.views.delete'),
    (r'^delete/$',
        'output_validator.views.bulkdelete'),
)
