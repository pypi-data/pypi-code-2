# coding: utf-8

"""
setup some "static" variables
"""
from pylucid_project.apps.pylucid.markup.hightlighter import get_pygments_css

try:
    from functools import wraps
except ImportError:
    from django.utils.functional import wraps  # Python 2.3, 2.4 fallback.

from django.conf import settings
from django.contrib.sites.models import Site
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from dbtemplates.models import Template

from pylucid_project import VERSION_STRING
from pylucid_project.utils import slug


def add_plugin_info(view_function):
    """ Add css anchor into context. Used information from lucidTagNode. """
    @wraps(view_function)
    def _inner(request):
        context = view_function(request)

        if getattr(request, "plugin_name", None) != None:
            # Add css anchor info
            plugin_name = request.plugin_name
            method_name = request.method_name

            if not hasattr(request, "css_id_list"):
                request.css_id_list = []

            css_plugin_id = plugin_name + u"_" + method_name
            existing_slugs = request.css_id_list
            css_plugin_id = slug.makeUniqueSlug(css_plugin_id, existing_slugs)

            request.css_id_list.append(css_plugin_id)

            context["css_plugin_id"] = css_plugin_id
            context["css_plugin_class"] = plugin_name

        return context
    return _inner


@add_plugin_info
def pylucid(request):
    """
    A django TEMPLATE_CONTEXT_PROCESSORS
    http://www.djangoproject.com/documentation/templates_python/#writing-your-own-context-processors
    """
    if hasattr(request.PYLUCID, "context"):
        # reuse a exsiting context, so we save a few database requests
        # XXX: Is it's normal, das these context processor would be called more than one time?
        return request.PYLUCID.context


    current_site = Site.objects.get_current()
    all_sites = Site.objects.all()

    context = {
        "powered_by": mark_safe('<a href="http://www.pylucid.org">PyLucid v%s</a>' % VERSION_STRING),
        # This value would be changed in index._render_cms_page(), if the
        # plugin manager or any plugin set request.anonymous_view = False
        "robots": "index,follow", # TODO: remove in v0.9, see: ticket:161

        "CSS_PLUGIN_CLASS_NAME": settings.PYLUCID.CSS_PLUGIN_CLASS_NAME,

        "current_site": current_site,
        "sites": all_sites,

        "PyLucid_media_url": settings.MEDIA_URL + settings.PYLUCID.PYLUCID_MEDIA_DIR + "/",
        "Django_media_prefix": settings.ADMIN_MEDIA_PREFIX,

        "debug": settings.DEBUG,
    }

    context["PYLUCID"] = request.PYLUCID

    # FIXME: Should we only insert pygments in admin section?
    #    We can also add a new template tag to get the path and insert it in pylucid/templates/admin/base_site.html    
    # get the EditableHtmlHeadFile path to pygments.css (page_msg created, if not exists)
    pygments_css_path = get_pygments_css(request)
    context["pygments_css"] = pygments_css_path

    pagetree = getattr(request.PYLUCID, "pagetree", None)
    if pagetree:
        if "design_switch_pk" in request.session:
            # The user has switch the design with pylucid_plugins.design
            from pylucid_project.apps.pylucid.models import Design # import here, agains import loops

            design_id = request.session["design_switch_pk"]
            pagetree.design = Design.on_site.get(id=design_id)
#            messages.info(request, "switch to design: %r" % pagetree.design)

        template_name = pagetree.design.template
        context["template_name"] = template_name

        # Add the dbtemplates entry.
        # Used in pylucid_admin_menu.html for generating the "edit page template" link
        try:
            context["template"] = Template.on_site.get(name=template_name)
        except Template.DoesNotExist:
            context["template"] = None

    pagemeta = getattr(request.PYLUCID, "pagemeta", None)
    if pagemeta:
        context.update({
            "pagemeta": pagemeta,
            "page_title": pagemeta.get_title(),
            "page_keywords": pagemeta.keywords,
            "page_description": pagemeta.description,
            "page_robots": pagemeta.robots,
            "page_language": pagemeta.language.code,
            "page_permalink": pagemeta.get_permalink(),
            "page_absolute_url": pagemeta.get_absolute_url(),
        })

    return context
