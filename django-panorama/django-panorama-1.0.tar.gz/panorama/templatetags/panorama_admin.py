from django import template
from panorama.models import Panorama, PanoramaInfo
from django.core.urlresolvers import reverse
import re

register = template.Library()

@register.inclusion_tag('panorama/panorama_selector.html')
def panorama_selector(panoramainfo=None):
    if panoramainfo is None:
        panorama = Panorama.objects.all()[0]
    else:
        panorama = panoramainfo.panorama
    json_url = reverse('panorama.views.panorama_json',kwargs={'pk':panorama.pk})
    return {'panorama':panorama,
            'panoramainfo':panoramainfo,
            'json_url':json_url}


class PanoramaInfoTypes(template.Node):
    def __init__(self, var_name):
        self.var_name = var_name
    def render(self, request):
        infos = PanoramaInfo.__subclasses__()
        urls = []
        for info in infos:
            url = 'admin:%s_%s_add' % (info._meta.app_label, info._meta.module_name)
            urls.append({'label':info._meta.verbose_name, 'url':reverse(url)})
        request[self.var_name] = urls
        return ''

@register.tag
def panoramainfo_types(parser, token):
    m = re.search(r'panoramainfo_types as (\w+)', token.contents)
    if not m:
        raise template.TemplateSyntaxError, "panoramainfo_types needs variable name. Example {%panoramainfo_types as pitypes%}"
    var_name = m.groups()[0]
    return PanoramaInfoTypes(var_name)

