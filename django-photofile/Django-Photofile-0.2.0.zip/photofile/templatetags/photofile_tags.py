#coding=utf-8

from django import template
register = template.Library()

from photofile import get_filename, generate_thumb

@register.tag(name="generate_thumbnail")
def generate_thumbnail(parser, token):
    try:
        tokens = token.split_contents()
        if len(tokens) == 3:
            tagname, photo, resolution = tokens
            crop = False
        elif len(tokens) == 4:
            tagname, photo, resolution, option = tokens
            crop = option == "crop"
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires exactly two or three arguments." % tagname
    return FormatImageNode(photo, resolution, crop)


class FormatImageNode(template.Node):

    def __init__(self, photo, resolution, do_crop=False):
        self.resolution = resolution
        self.photo = template.Variable(photo)
        self.do_crop = do_crop

    def render(self, context):
        try:
            if not 'x' in self.resolution:
                return 'not correct resolution format'

            p = self.photo.resolve(context)
            complete_filename = get_filename(p)

            width, height = map(int, self.resolution.split('x'))
            return  generate_thumb(complete_filename, width, height, self.do_crop)
        except template.VariableDoesNotExist, e:
            return 'Unable to produce url for image: %s' % e