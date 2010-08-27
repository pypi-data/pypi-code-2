#encoding:utf-8
from django.conf.urls.defaults import patterns, url, include
from helmholtz.experiment.admin import experiment_admin
from helmholtz.experiment.models import Experiment

def base_context(cls):
    d = {'queryset': cls.objects.all(),
         'extra_context': {'object_name': cls._meta.verbose_name,
                           'object_name_plural': cls._meta.verbose_name_plural},
         'template_name':'experiment_list.html',
         'get_statistics':True
    }
    return d

def paginated_context(cls, pagination):
    d = base_context(cls)
    d['paginate_by'] = pagination
    return d

urlpatterns = patterns('',
    (r'^admin/', include(experiment_admin.urls)),
    url(r'^data/(?P<lab>\w+(\s\S+)*)/$', 'helmholtz.experiment.views.experiment_list', paginated_context(Experiment, 25), name='experiment-list'),
    url(r'^data/(?P<lab>\w+(\s\S+)*)/(?P<expt>\w[\w\-]*)/$', 'helmholtz.experiment.views.experiment_detail', {'template':"experiment_detail.html", "get_statistics":True}, name='experiment-detail'),
)
