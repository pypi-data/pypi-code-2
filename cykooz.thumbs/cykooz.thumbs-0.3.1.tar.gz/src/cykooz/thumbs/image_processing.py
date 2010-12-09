# -*- coding: utf-8 -*-
'''
Created on 12.10.2010

@author: cykooz
'''
import os
import Image

def render_to_cache(path, mtime, data, size_info):
    image = Image.open(data)
    image = image.convert('RGB')
    size = size_info['size']
    if size != image.size:
        if size[0] == 0:
            size = (image.size[0], size[1])
        elif size[1] == 0:
            size = (size[0], image.size[1])
    if size_info['scale_method'] == 'crop':
        image = crop(image, size)
    elif size_info['scale_method'] == 'stretch':
        image = resize(image, size, False)
    elif size_info['scale_method'] == 'squash':
        if size[0] < image.size[0] or size[1] < image.size[1]:
            image = resize(image, size, False)
    elif size_info['scale_method'] == 'fit_stretch':
        image = resize(image, size, True)
    elif size_info['scale_method'] == 'fit_squash':
        if size[0] < image.size[0] or size[1] < image.size[1]:
            image = resize(image, size, True)
    else:
        raise Exception('Unknown scale method')

    if size_info['quality'] == 'png':
        image.save(path, 'PNG')
    else:
        image.save(path, 'JPEG', quality=size_info['quality'])

    os.utime(path, (mtime, mtime))


def crop(image, size):
    orig_w, orig_h = image.size
    wh = float(size[0]) / float(size[1])
    d1 = orig_h - orig_w / wh
    d2 = orig_w - orig_h * wh
    d = min(d1, d2)
    if d < 0:
        d = max(d1, d2)
    if d > 0:
        if d == d1:
            y1 = int(d1 / 2)
            y2 = int(y1 + orig_w / wh)
            box = (0, y1, orig_w, y2)
        else:
            x1 = int(d2 / 2)
            x2 = int(x1 + orig_h * wh)
            box = (x1, 0, x2, orig_h)
        image = image.crop(box)
    return image.resize(size, Image.ANTIALIAS)


def resize(image, size, original_aspect_ratio=True):
    if original_aspect_ratio:
        r = min(map(lambda x, y: float(x)/y, size, image.size))
        size = map(lambda x: int(x*r), image.size)
    return image.resize(size, Image.ANTIALIAS)
