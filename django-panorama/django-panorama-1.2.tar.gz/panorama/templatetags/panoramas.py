"templatetas for panoramas"
from django import template
from panorama.models import PanoramaInfo
from django.conf import settings
import panorama.settings as panoramasettings
register = template.Library()


@register.simple_tag
def panorama_js():
    "Javascript includes needed by panoramas"
    return """
    <script type="text/javascript" src="%spanorama/js/jquery.js"></script>
    <script type="text/javascript" 
            src="%spanorama/js/jquery.fancybox-1.3.1.pack.js"></script>
    <script type="text/javascript" 
            src="%spanorama/js/jquery.panorama.js"></script>
    """ % ((settings.STATIC_URL,)*3)


@register.inclusion_tag('panorama/img.html', takes_context=True)
def show_panorama(context, panorama):
    """Show a panorama.

       First argument must be a Panorama instance.

       Rest of arguments can be picked from context:
         - start_position
         - auto_start
         - viewport_width
         - speed
         - direction
         - control_display
         - mode_360
    """
    infos = []
    for subinfo in PanoramaInfo.__subclasses__():
        infos += subinfo.objects.filter(panoramainfo_ptr__panorama=panorama)

    out_context = {'panorama':panorama,
            'panoramainfos':infos,
            'STATIC_URL': settings.STATIC_URL}

    #Search display options in context, model and settings, in this order
    for opt in ('start_position', 'auto_start', 'viewport_width', 'speed',
                'direction', 'control_display', 'mode_360'):
        if context.get(opt) is not None:
            out_context[opt] = context.get(opt)
        elif getattr(panorama, opt, None) is not None:
            out_context[opt] = getattr(panorama, opt, None)
        else:
            out_context[opt] = getattr(panoramasettings, opt.upper())
    return out_context
