"django-panorama templatetags for admin interface"
from django import template
from panorama.models import Panorama, PanoramaInfo
from django.core.urlresolvers import reverse
import re

register = template.Library()

@register.inclusion_tag('panorama/panorama_selector.html')
def panorama_selector(panoramainfo=None):
    "OpenLayers powered selector to set the bounding box of PanoramaInfos"
    if panoramainfo is None:
        panorama = Panorama.objects.all()[0]
    else:
        panorama = panoramainfo.panorama
    json_url = reverse('panorama.views.panorama_json',
                       kwargs={'pk':panorama.pk})
    return {'panorama':panorama,
            'panoramainfo':panoramainfo,
            'json_url':json_url}


class PanoramaInfoTypes(template.Node):
    "Add PanoramaInfo types to request"
    def __init__(self, var_name, *args, **kwargs):
        super(PanoramaInfoTypes, self).__init__(*args, **kwargs)
        self.var_name = var_name
    def render(self, request):
        infos = PanoramaInfo.__subclasses__()
        urls = []
        for info in infos:
            url = 'admin:%s_%s_add' % (info._meta.app_label,
                                       info._meta.module_name)
            urls.append({'label':info._meta.verbose_name, 'url':reverse(url)})
        request[self.var_name] = urls
        return ''

@register.tag
def panoramainfo_types(parser, token):
    "templatetag to load all diferent Models inherinting PanoramaInfo"
    match = re.search(r'panoramainfo_types as (\w+)', token.contents)
    if not match:
        raise template.TemplateSyntaxError, \
              "panoramainfo_types needs variable name. "\
              "Example {%panoramainfo_types as pitypes%}"
    var_name = match.groups()[0]
    return PanoramaInfoTypes(var_name)

