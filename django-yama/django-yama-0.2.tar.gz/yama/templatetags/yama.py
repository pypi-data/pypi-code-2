from django import template
import re

DEFAULT_CLASSES = {
            'first_li_class' : "first", 
            'first_a_class' : "a_first",
            'last_li_class' : "last", 
            'last_a_class' : "a_last",
            'dir_li_class' : "li_dir",
            'dir_a_class' : "dir",
}


# Regex for token keyword arguments
kwarg_re = re.compile(r"(?:(\w+)=)?(.+)")

def parse_keyword_args(parser, token, node_class, min_args=0):
    '''
    Parse a template tag which takes variable length and keyword arguments.

    Arguments ``parser`` and ``token`` should come directly from the
    tag compilation function. Argument given by ``node_class`` should
    be a subclass of template.Node; ``min_args`` gives the minimum
    number of arguments that the tag expects (not counting the tag
    name itself).

    Given a tag:

        {% tag arg1 arg2 key1=val1 key2=val2 %}

    the result will be a ``node_class`` instance, instantiated with *args and
    **kwargs, where :
        args = [arg1, arg2] 
    and 
        kwargs = { key1 : val1, key2 : val2 }

    The implementation was ripped mostly straight from
    django.template.defaulttags.url.

    '''

    args = []
    kwargs = {}

    bits = token.split_contents()
    tag_name = bits[0]
    min_length = min_args + 1
    if len(bits) < min_length:
        raise template.TemplateSyntaxError(
            "'%s' takes at least %d argument(s)" % (tag_name, min_args)
        )

    bits = bits[1:]
    if len(bits):
        for bit in bits:
            match = kwarg_re.match(bit)
            if not match:
                raise TemplateSyntaxError("Malformed arguments to %s tag" % tag_name)
            name, value = match.groups()
            if name:
                kwargs[name] = parser.compile_filter(value)
            else:
                args.append(parser.compile_filter(value))

    return node_class(*args, **kwargs)

register = template.Library()

@register.tag(name='menu_as_ul')
def do_menu_as_ul(parser, token):
    return parse_keyword_args(parser, token, MenuNode, 1)

def dict_map(f, d):
    return dict((k, f(v)) for (k, v) in d.iteritems())

class MenuNode(template.Node):
    def __init__(self, menu, **opts):
        self.menu = menu 

        self.opts = opts

    def render(self, context):
        menu = self.menu.resolve(context)
        default = DEFAULT_CLASSES.copy()
        resolved = dict_map(lambda x: x.resolve(context), self.opts)
        default.update(resolved)
        default.update({'menu' : menu})
        ctx = template.Context(default, autoescape=context.autoescape)
        t = template.loader.get_template('yama/fragments/menu.html')
        return t.render(ctx)

@register.tag(name='menu_item_as_li')
def do_menuitem_as_li(parser, token):
    return parse_keyword_args(parser, token, MenuItemNode, 1)

class MenuItemNode(template.Node):
    def __init__(self, item, **opts):
        self.opts = { }
        self.opts.update(opts)
        self.item = item

    def render(self, context):
        item = self.item.resolve(context)

        li_classes = []
        a_classes = []
        try:
            first = self.opts['first'].resolve(context)
        except:
            first = False
        try:
            last = self.opts['last'].resolve(context)
        except:
            last = False

        if first:
            li_classes.append(context['first_li_class'])
            a_classes.append(context['first_a_class'])
        if last:
            li_classes.append(context['last_li_class'])
            a_classes.append(context['last_a_class'])
        if item.has_visible_children():
            li_classes.append(context['dir_li_class'])
            a_classes.append(context['dir_a_class'])

        opts = {
            'item' : item,
            'item_li_classes' : ' '.join(li_classes),
            'item_a_classes' : ' '.join(a_classes),
        }
        opts.update((cls, context[cls]) for cls in DEFAULT_CLASSES)
        ctx = template.Context(opts, autoescape=context.autoescape)

        t = template.loader.get_template('yama/fragments/menuitem.html')
        return t.render(ctx)

