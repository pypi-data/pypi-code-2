
from os import path
from cStringIO import StringIO

from sphinx.application import TemplateBridge

from djangosans.template.loaders.filesystem import FileSystemLoaderManager
from djangosans.template.context import Context
from djangosans.conf import settings

#settings.TEMPLATE_DEBUG = True

if 'wuxi' not in settings.INSTALLED_APPS:
    settings.INSTALLED_APPS += ('wuxi',)

class DjangoTemplateBridge(TemplateBridge):

    def init(self, builder, theme=None, dirs=None):
        """
        Called by the builder to initialize the template system.

        *builder* is the builder object; you'll probably want to look at the
        value of ``builder.config.templates_path``.

        *theme* is a :class:`sphinx.theming.Theme` object or None; in the latter
        case, *dirs* can be list of fixed directories to look for templates.
        """
        # create a chain of paths to search
        if theme:
            # the theme's own dir and its bases' dirs
            chain = theme.get_dirchain()
            # then the theme parent paths
            chain.extend(theme.themepath)
        elif dirs:
            chain = list(dirs)
        else:
            chain = []

        # prepend explicit template paths
        self.templatepathlen = len(builder.config.templates_path)
        if builder.config.templates_path:
            chain[0:0] = [path.join(builder.confdir, tp)
                          for tp in builder.config.templates_path]

        # make the paths into loaders
        self.loaders = FileSystemLoaderManager(chain)

    def newest_template_mtime(self):
        """
        Called by the builder to determine if output files are outdated
        because of template changes.  Return the mtime of the newest template
        file that was changed.  The default implementation returns ``0``.
        """
        return 0

    def render(self, template, context):
        """
        Called by the builder to render a template given as a filename with a
        specified context (a Python dictionary).
        """
        return self.loaders.render_to_string(template, context)

    def render_string(self, template, context):
        """
        Called by the builder to render a template given as a string with a
        specified context (a Python dictionary).
        """
        t = self.loaders.get_template_from_string(template)
        buf = StringIO()
        ctx = Context(context, out=buf)
        t.render(ctx)
        return buf.getvalue()

