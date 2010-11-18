from django import template

from cms.templatetags.placeholder_tags import  PlaceholderNode
from cms.models import Placeholder

register = template.Library()

class PlaceholderNodeAS(PlaceholderNode):
    
    def __init__(self, placeholder, width, asvar):
        super(PlaceholderNodeAS, self).__init__(placeholder, width)
        self.asvar = asvar
    
    def render(self, context):
        context[self.asvar] = super(PlaceholderNodeAS, self).render(context)
        return u''

def render_placeholder_as(parser, token):
    bits = token.split_contents()
    
    if 'as' not in bits:
        raise template.TemplateSyntaxError("%s needs a 'as' argument" % bits[0])
    
    name = parser.compile_filter(bits[1])
    
    kw = {}
    remaining_bits = bits[2:]
    for idx, bit in enumerate(remaining_bits):
       if idx == 0 or idx % 2 == 0:
           kw[str(bit)] = remaining_bits[idx+1]
    
    width = None
    if 'width' in kw:
        width = parser.compile_filter(kw['width'])
    
    return PlaceholderNodeAS(name, width, kw['as'])

register.tag('render_placeholder_as', render_placeholder_as)

def choose_placeholder(placeholders, placeholder):
    try:
        return placeholders.get(slot=placeholder)
    except Placeholder.DoesNotExist:
        return None
register.filter('choose_placeholder', choose_placeholder)