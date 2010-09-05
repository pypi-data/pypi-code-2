
__version__ = '0.1'

class PathTo(object):

    def __init__(self, pathto_func, master_doc, staticdir, style):
        self._pathto = pathto_func
        self.master_doc = pathto_func(master_doc, False)
        self.staticdir = staticdir
        self.style = pathto_func('/'.join([staticdir, style]), True)

    def __getattr__(self, name):
        return self._pathto(name, True)

def update_context(app, pagename, template_name, context, evt_arg):
    showsidebar = not context.get('embedded', False)
    if showsidebar:
        sidebars = context.get('sidebars')
        if sidebars is not None:
            showsidebar = sidebars and not context.get('theme_nosidebar')
    context['render_sidebar'] = showsidebar
    url_root = context['pathto']('', True)
    if url_root == '#':
        url_root = ''
    context['url_root'] = url_root
    staticdir = '_static'
    staticpaths = app.config.html_static_path
    if staticpaths:
        context['html_static_path'] = staticpaths
        staticdir = staticpaths[0]
    context['pathto'] = PathTo(
                            context['pathto'],
                            context['master_doc'],
                            staticdir,
                            context.get('style'),
                            )

def setup(app):
    app.connect('html-page-context', update_context)

