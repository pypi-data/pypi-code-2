# coding=utf-8
from django.template import Library, Node, TemplateSyntaxError, loader
from django_inline import templates_list

register = Library()

@register.tag
def editable(parser, token):
    """
    Puts a jeditable HTML element (span.jeditable) around the contents of the tag.
    Usage:
       {% editable object field_name %}
    """
    bits = token.contents.split()    
    
    nodelist = parser.parse(('endeditable',))
    parser.delete_first_token()
    
    if len(bits) != 3:
        raise TemplateSyntaxError("%s tag requires exactly two arguments: object and the field to edit" % bits[0])
    
    return EditableNode(nodelist, parser.compile_filter(bits[1]), bits[2])


class EditableNode(Node):
    def __init__(self, nodelist, obj, field):
        self.nodelist = nodelist
        self.obj = obj
        self.field = field

    def render(self, context):
        inner_content = self.nodelist.render(context)
        obj = self.obj.resolve(context)
        class_name = obj.__class__.__name__
        app_label = obj._meta.app_label
        
        if not context['user'].has_perm('%s.can_edit' % class_name):
            return inner_content
        
        return loader.render_to_string(templates_list('inline-editable.html', obj), {
            'class': class_name,
            'label': app_label,
            'id': obj.id,
            'field': self.field,
            'inner': inner_content,
        })
