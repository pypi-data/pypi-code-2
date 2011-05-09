#coding=utf-8
from PIL import Image
from PIL.ExifTags import TAGS


def get_exif(fn):
    ret = {}
    i = Image.open(fn)
    info = i._getexif()
    for tag, value in info.items():
        decoded = TAGS.get(tag, tag)
        ret[decoded] = value
    return ret


def resize_image(source_file, target_file, width, height, crop=False):
    """
    Resizes an image specified by source_file and writes output to target_file.
    Will read EXIF data from source_file, look for information about orientation
    and rotate photo if such info is found.
    """
    image = Image.open(source_file)

    orientation = None
    try:
        d = get_exif(image._getexif())
        orientation = d.get('Orientation')
    except:
        pass

    if image.mode not in ('L', 'RGB'):
        image = image.convert('RGB')

    if not crop:
        image.thumbnail((width, height), Image.ANTIALIAS)
    else:
        src_width, src_height = image.size
        src_ratio = float(src_width) / float(src_height)
        dst_width, dst_height = width, height
        dst_ratio = float(dst_width) / float(dst_height)

        if dst_ratio < src_ratio:
            crop_height = src_height
            crop_width = crop_height * dst_ratio
            x_offset = int(float(src_width - crop_width) / 2)
            y_offset = 0
        else:
            crop_width = src_width
            crop_height = crop_width / dst_ratio
            x_offset = 0
            y_offset = int(float(src_height - crop_height) / 3)
        image = image.crop((x_offset, y_offset, x_offset+int(crop_width), y_offset+int(crop_height)))
        image = image.resize((int(dst_width), int(dst_height)), Image.ANTIALIAS)

    # rotate according to orientation stored in exif-data:
    if orientation:
        if orientation == 2:
            # Vertical Mirror
            image = image.transpose(Image.FLIP_LEFT_RIGHT)
        elif orientation == 3:
            # Rotation 180°
            image = image.transpose(Image.ROTATE_180)
        elif orientation == 4:
            # Horizontal Mirror
            image = image.transpose(Image.FLIP_TOP_BOTTOM)
        elif orientation == 5:
            # Horizontal Mirror + Rotation 270°
            image = image.transpose(Image.FLIP_TOP_BOTTOM).transpose(Image.ROTATE_270)
        elif orientation == 6:
            # Rotation 270°
            image = image.transpose(Image.ROTATE_270)
        elif orientation == 7:
            # Vertical Mirror + Rotation 270°
            image = image.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.ROTATE_270)
        elif orientation == 8:
            # Rotation 90°
            image = image.transpose(Image.ROTATE_90)

    image.save(target_file)
