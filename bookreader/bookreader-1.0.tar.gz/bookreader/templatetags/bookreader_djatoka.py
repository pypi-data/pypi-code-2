from urllib import urlencode
from django import template
from django.conf import settings

register = template.Library()

@register.tag
def djatoka_resolver_url(parser, token):
    token = token.split_contents()
    
    if len(token) < 2:
        raise template.TemplateSyntaxError, '%s tag requires a resource url to be the first argument' % token[0]
    
    return DjatokaResolverNode(token[1], len(token) > 2 and token[2:] or [])

class DjatokaResolverNode(template.Node):
    def __init__(self, url, arguments):
        if url[0] == url[-1] and url[0] in ("'",'"'):
            self.rft_id = url[1:-1]
        else:
            self.rft_id = template.Variable(url)
        
        self.arguments = arguments
    
    def render(self, context):
        kwargs = settings.DJATOKA_ARGUMENTS.copy()
        
        for arg in self.arguments:
            try:
                key, value = arg.split('=',1)
                kwargs[key] = value
            except:
                pass
        
        if isinstance(self.rft_id, basestring):
            kwargs['rft_id'] = self.rft_id
        else:
            kwargs['rft_id'] = self.rft_id.resolve(context)
        
        return '%s?%s' % (settings.DJATOKA_BASE_URL, urlencode(kwargs, True),)

@register.simple_tag
def djatoka_base_url():
    return settings.DJATOKA_BASE_URL