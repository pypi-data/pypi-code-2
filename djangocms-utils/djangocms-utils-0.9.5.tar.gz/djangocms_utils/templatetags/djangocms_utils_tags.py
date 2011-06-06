from django import template
from classytags.arguments import Argument
from classytags.parser import Parser
from classytags.core import Options
from cms.templatetags.placeholder_tags import RenderPlaceholder
from cms.models import Placeholder
register = template.Library()
 
class RenderPlaceholderAs(RenderPlaceholder):
    name = 'render_placeholder_as'
    options = Options(
        Argument('placeholder'),
        'as',
        Argument('as_var', default=None, required=False),
        Argument('width', default=None, required=False)
    )

    def render_tag(self, context, **kwargs):
        rendered = super(RenderPlaceholderAs, self).render_tag(context, kwargs['placeholder'], kwargs['width'])
        if kwargs['as_var']:
            context.push()
            context[str(kwargs['as_var'])] = rendered
            return u''
        return rendered

register.tag(RenderPlaceholderAs)

def choose_placeholder(placeholders, placeholder):
    try:
        return placeholders.get(slot=placeholder)
    except Placeholder.DoesNotExist:
        return None
register.filter('choose_placeholder', choose_placeholder)

def get_placeholder_group(placeholder):
    placeholder_group = 'none'
    for group, placeholders in settings.PLACEHOLDER_GROUPS.items():
        if placeholder in placeholders:
            placeholder_group = group
    return placeholder_group
register.filter('get_placeholder_group', get_placeholder_group)
