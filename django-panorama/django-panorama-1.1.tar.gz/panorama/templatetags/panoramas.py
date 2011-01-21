"templatetas for panoramas"
from django import template
from panorama.models import PanoramaInfo
from django.conf import settings
register = template.Library()

def panorama_js():
    "Javascript includes needed by panoramas"
    return """
    <script type="text/javascript" src="%spanorama/js/jquery.js"></script>
    <script type="text/javascript" 
            src="%spanorama/js/jquery.fancybox-1.3.1.pack.js"></script>
    <script type="text/javascript" 
            src="%spanorama/js/jquery.panorama.js"></script>
    """ % ((settings.STATIC_URL,)*3)

panorama_js = register.simple_tag(panorama_js)


def show_panorama(panorama, position=None):
    """Show a panorama.

       First argument must be a Panorama instance.

       Second argument, if provided, controls the starting position of the
       panorama in pixels.
    """
    infos = []
    for subinfo in PanoramaInfo.__subclasses__():
        infos += subinfo.objects.filter(panoramainfo_ptr__panorama=panorama)
    return {'panorama':panorama,
            'position':position,
            'panoramainfos':infos}

show_panorama = register.inclusion_tag('panorama/img.html')(show_panorama)
