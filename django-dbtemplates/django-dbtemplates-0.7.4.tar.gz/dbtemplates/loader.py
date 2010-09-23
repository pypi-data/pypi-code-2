from django import VERSION
from django.conf import settings
from django.contrib.sites.models import Site
from django.template import TemplateDoesNotExist

from dbtemplates.models import Template, backend

def load_template_source(template_name, template_dirs=None):
    """
    A custom template loader to load templates from the database.

    Tries to load the template from the dbtemplates cache backend specified
    by the DBTEMPLATES_CACHE_BACKEND setting. If it does not find a template
    it falls back to query the database field ``name`` with the template path
    and ``sites`` with the current site.
    """
    if VERSION[:2] >= (1, 2):
        # For backward compatibility
        import warnings
        warnings.warn(
            "`dbtemplates.loader.load_template_source` is deprecated; "
            "use `dbtemplates.loader.Loader` instead.",
            PendingDeprecationWarning
        )
    site = Site.objects.get_current()
    display_name = 'db:%s:%s:%s' % (settings.DATABASE_ENGINE,
                                    template_name, site.domain)
    if backend:
        try:
            backend_template = backend.load(template_name)
            if backend_template:
                return backend_template, template_name
        except:
            pass
    try:
        template = Template.on_site.get(name__exact=template_name)
        # Save in cache backend explicitly if manually deleted or invalidated
        if backend:
            backend.save(template_name, template.content)
        return (template.content, display_name)
    except:
        pass
    raise TemplateDoesNotExist(template_name)
load_template_source.is_usable = True


if VERSION[:2] >= (1, 2):
    # providing a class based loader for Django >= 1.2, yay!
    from django.template.loader import BaseLoader

    class Loader(BaseLoader):
        __doc__ = load_template_source.__doc__

        is_usable = True

        def load_template_source(self, template_name, template_dirs=None):
            return load_template_source(template_name, template_dirs)

