#coding=utf-8

import os
from django import template
from django.conf import settings
from django.core.cache import cache
register = template.Library()

from photofile import resize_image

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
            p = self.photo.resolve(context)

            if hasattr(p, 'unique_filename'):
                complete_filename = p.unique_filename
            elif hasattr(p, 'complete_filename'):
                complete_filename = p.complete_filename
            elif hasattr(p, 'filename'):
                complete_filename = p.filename
            else:
                return 'Instance is missing unique_filename/filename/complete_filename property.'

            width, height = map(int, self.resolution.split('x'))
            fname, ext = os.path.splitext(os.path.basename(complete_filename))
            resized_image = '%s_%sx%s%s%s' % (fname, width, height, self.do_crop and '_crop' or '',ext)
            cached_filename = cache.get(resized_image, None)
            if cached_filename:
                return cached_filename

            if not os.path.exists(complete_filename):
                return 'inputfile does not exists'

            if not 'x' in self.resolution:
                return 'not correct resolution format'

            static_folder = len(settings.STATICFILES_DIRS) and settings.STATICFILES_DIRS[0] or settings.STATIC_ROOT
            
            thumb_dir = os.path.join(static_folder, 'thumbs')
            if not os.path.exists(thumb_dir):
                os.makedirs(thumb_dir)

            output = os.path.join(thumb_dir, resized_image)
            final_url = "%sthumbs/%s" % (settings.STATIC_URL, resized_image)
            cache.set(resized_image, final_url, 30)
            if os.path.exists(output):
                return final_url

            resize_image(complete_filename, output, width, height, crop=self.do_crop)
            return final_url
        except template.VariableDoesNotExist:
            return 'Unable to produce url for image'