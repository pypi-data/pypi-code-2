
from djangosans import template

register = template.Library()

@register.tag
def relativize(parser, token):
    """
    Relative any path, optionally appending a suffix
    """
    try:
        tagname, suffix = token.split_contents()
    except ValueError:
        suffix = ''
    else:
        if suffix[0] in ['"', "'"]:
            if suffix[-1] != suffix[0]:
                raise template.TemplateSyntaxError("mismatched quotes in suffix")
            else:
                suffix = suffix[1:-1]
        suffix = parser.compile_filter(suffix)
    nodelist = parser.parse(('endrelativize',))
    parser.delete_first_token()
    return RelativizedPathNode(nodelist, suffix)

class RelativizedPathNode(template.Node):

    def __init__(self, nodelist, suffix=''):
        self.nodelist = nodelist
        self.suffix = suffix

    def render(self, context, write):
        buf = context.out
        i = buf.tell()
        self.nodelist.render(context)
        buf.seek(i)
        newval = '%s%s' % (context['pathto']._pathto(buf.read(), True), self.suffix)
        buf.seek(i)
        write(newval)

@register.inclusion_tag('localtoc.html', takes_context=True)
def localtoc(context):
    return {
            'toc': context.get('toc'),
            'pathto': context['pathto'],
            'display_toc': context.get('display_toc'),
            'master_doc': context.get('master_doc'),
            }

@register.inclusion_tag('sidebar.html', takes_context=True)
def sidebar(context):
    d = localtoc(context)
    d.update({
            'logo': context.get('logo'),
            'sidebars': context.get('sidebars'),
            'render_sidebar': context.get('render_sidebar'),
            })
    return d

@register.inclusion_tag('relbar.html', takes_context=True)
def relbar(context):
    reldelim1 = context.get('reldelim1') or ' &raquo;'
    reldelim2 = context.get('reldelim2') or ' |'
    return {
            'pathto': context['pathto'],
            'master_doc': context.get('master_doc'),
            'shorttitle': context.get('shorttitle'),
            'rellinks': context.get('rellinks'),
            'parents': context.get('parents'),
            'reldelim1': reldelim1,
            'reldelim2': reldelim2,
            }

