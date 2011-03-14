#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2010
"""
from __future__ import with_statement
import os
import re
import datetime
from time import time, sleep
from subprocess import Popen, PIPE
from tempfile import mkdtemp
from shutil import rmtree
from threading import Lock
from cStringIO import StringIO
from mimetypes import guess_type
from time import mktime, strptime
from httplib import HTTPConnection
from urlparse import urlsplit
from urllib import urlopen
import rfc822
import cherrypy
from cherrypy.lib.cptools import validate_since
import Image
import ImageDraw
import ImageFont
import ImageEnhance
import ImageFilter
from cocktail.modeling import (
    cached_getter,
    abstractmethod,
    OrderedDict,
    ListWrapper
)
from cocktail import schema
from cocktail.controllers import (
    context,
    get_parameter,
    Location,
    serve_file
)
from woost.models import (
    Item,
    Publishable,
    File,
    URI,
    User,
    get_current_user,
    ReadPermission,
    ModifyPermission
)
from woost.controllers.basecmscontroller import BaseCMSController

default_format = "PNG"

formats_by_mime_type = {
    "image/jpeg": "JPEG",
    "image/pjpeg": "JPEG",
    "image/png": "PNG",
    "image/x-png": "PNG",
    "image/gif": "GIF",
    "image/tiff": "TIFF"
}

mime_types_by_format = dict(
    (v, k)
    for k, v in formats_by_mime_type.iteritems()
)

class ImagesController(BaseCMSController):

    def __call__(self, id, *processing, **kwargs):

        # Get the requested item or content type, validate access
        item = None

        try:
            id = int(id)
        except ValueError:
            for cls in Item.schema_tree():
                if cls.full_name == id:
                    item = cls
                    break
        else:
            item = Item.get_instance(int(id))

        if item is None:
            raise cherrypy.NotFound()

        return serve_image(item, *processing, **kwargs)

def serve_image(item, *processing, **kwargs):
    
    is_type = isinstance(item, type)
        
    # Determine the rendering format
    format = kwargs.pop("format", None)
    if format:
        format = format.upper()

    # Find a content renderer that can handle the requested item
    renderer = None
    kind = kwargs.pop("kind", "icon" if is_type else "image").split(",")
    is_icon = False
    
    if "image" in kind:
        if is_type:
            raise ValueError(
                "Can't set 'kind' to 'image' when rendering a content type"
            )

        for renderer in content_renderers:
            if renderer.can_render(item):
                break
        else:
            renderer = None

    apply_effects = kwargs.pop("apply", "on")
    item_effects = []

    if isinstance(item, File) and item.image_effects:
        
        if apply_effects == "off":
            get_current_user().require_permission(ModifyPermission, target = item)
        else:
            item_effects = item.image_effects.split("/")
            processing = item_effects + list(processing)

    if renderer is None and "icon" in kind:
        for renderer in icon_renderers:
            if renderer.can_render(item):
                is_icon = True
                processing = []
                break
        else:
            renderer = None

    if renderer is None:
        raise RuntimeError("No content renderer can render %s" % item)

    if not is_type and not is_icon:
        get_current_user().require_permission(ReadPermission, target = item)

    # Caching:
    cache_enabled_param = kwargs.pop("cache", "on")
    if cache_enabled_param == "on":
        cache_enabled = not is_icon
    elif cache_enabled_param == "off":
        cache_enabled = False
    else:
        raise ValueError(
            "Unknown value for the 'cache' parameter: %s"
            % cache_enabled_param
        )

    if cache_enabled:
    
        # Client side cache
        mtime = renderer.last_change_in_appearence(item)
        cherrypy.response.headers["Last-Modified"] = rfc822.formatdate(mtime)
        validate_since()

        # Server side cache            
        extension = format or default_format
        file_name = str(item.id)
        
        if processing:
            file_name += "-" + "-".join(processing[len(item_effects):])

        if kwargs:
            file_name += "?"
            for key in sorted(kwargs):
                value = kwargs[key]
                file_name += "%s=%s" % (key, value) 

        file_name = file_name.replace("/", "-") + "." + extension.lower()

        cached_file = os.path.join(
            context["cms"].application_path,
            "thumbnails",
            file_name
        )

        if os.path.exists(cached_file) \
        and os.stat(cached_file).st_mtime >= mtime:
            mime_type = mime_types_by_format[extension]
            cherrypy.response.headers["Content-Type"] = mime_type
            return serve_file(cached_file, mime_type)

    # Read rendering parameters
    params = {}
    rendering_schema = renderer.rendering_schema
    
    if rendering_schema:
        
        if not rendering_schema.name:
            raise ValueError("All rendering schemas must have a name")

        get_parameter(
            rendering_schema,
            target = params,
            prefix = rendering_schema.name + ".",
            implicit_booleans = False
        )

    # Render the image
    image = renderer.render(item, **params)

    # The renderer designated an image file as its return value: either
    # serve it unmodified, or load it into memory for further processing
    if isinstance(image, tuple):

        file_name, file_mime_type = image
        file_format = formats_by_mime_type[file_mime_type]

        # Image processing or re-encoding requested
        if processing or (format and format != file_format):
            image = Image.open(file_name)
            if not format:
                format = file_format

        # Unmodified image requested; serve it straight away
        else:
            return serve_file(file_name, file_mime_type)

    # Image processing
    for processor in processing:
        pfunc, pargs, pkwargs = parse_processor(processor)
        image = pfunc(image, *pargs, **pkwargs)

    # Encode the resulting image
    buffer = StringIO()

    if not format:
        format = default_format

    if format == "JPEG" and image.mode != "RGB":
        image = image.convert("RGB")               

    # Store the resulting image in the server side cache
    if cache_enabled:
        image.save(cached_file, format)

    # Serve the image
    cherrypy.response.headers["Content-Type"] = \
        mime_types_by_format[format]
    image.save(buffer, format)
    return buffer.getvalue()

def parse_processor(processor_string):

    pos = processor_string.find("(")
    if pos == -1:
        proc_name = processor_string
    else:
        proc_name = processor_string[:pos]

    try:
        func = image_processors[proc_name]
    except:
        raise ValueError("Unknown image processor: %s" % proc_name)

    args = []
    kwargs = {}
    
    if pos != -1:
        if processor_string[-1] != ")":
            raise ValueError(
                "Invalid image processor string: %s" % processor_string
            )

        for arg in processor_string[pos + 1:-1].split(","):
            parts = arg.split("=")
            
            # Positional parameters
            if len(parts) == 1:
                value = _parse_value(arg)
                args.append(value)

            # Keyword parameters
            elif len(parts) == 2:
                key, value = parts
                value = _parse_value(value)
                kwargs[key] = value
            else:
                raise ValueError(
                    "Invalid image processor string: %s" % processor_string
                )

    return func, args, kwargs

def _parse_value(value):

    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'\""):
        return value[1:-1]

    if value in ("True", "False"):
        return bool(value)
    
    if "." in value:
        try:
            value = float(value)
        except ValueError:
            pass
        else:
            return value

    try:
        value = int(value)
    except ValueError:
        pass
    else:
        return value

    raise ValueError(
        "Invalid value for image processor parameter: %s" % value
    )

# Content renderers
#------------------------------------------------------------------------------

class ContentRenderersRegistry(ListWrapper):

    def __init__(self, items = None):
        ListWrapper.__init__(self, items)
        self.__lock = Lock()

    def register(self, renderer, after = None, before = None):
        """Add a new content renderer to the registry.

        By default, renderers are appended at the end of the registry. The
        L{after} or L{before} parameters can be used to specify the position in
        the registry where the renderer should be inserted. This can be
        important, since renderer are tried in registration order

        @param renderer: The renderer to register.
        @type renderer: L{ContentRenderer}

        @param after: 
        """

        with self.__lock:

            marker = after or before

            if marker is None:
                self._items.append(renderer)            
            else:
                if after and before:
                    raise ValueError(
                        "Can't register content renderer '%s' specifying both "
                        "'after' and 'before' parameters"
                        % renderer
                    )

                # Find the requested position
                if isinstance(marker, type):

                    # Find the first instance of the given type
                    for pos, registered_renderer in enumerate(self._items):
                        if isinstance(registered_renderer, marker):
                            break
                    else:
                        pos = -1
                else:
                    # Find an specific instance
                    try:
                        pos = self._items.index(marker)
                    except IndexError:
                        pos = -1

                if pos == -1:
                    raise IndexError(
                        "Trying to register content renderer '%s' %s %s, "
                        "which hasn't been registered yet"
                        % (renderer, "after" if after else "before", marker)
                    )

                if before:
                    self._items.insert(pos, renderer)
                else:
                    self._items.insert(pos + 1, renderer)  


class ContentRenderer(object):

    @abstractmethod
    def can_render(self, item):
        """Indicates if the renderer is able to render the given item.

        @param item: The item to evaluate.
        @type item: L{Item<woost.models.item.Item>}

        @return: True if the renderer claims to be able to render the item,
            False otherwise.
        @rtype: bool
        """

    @cached_getter
    def rendering_schema(self):
        """A schema describing additional parameters for the rendering process.
        @type: L{Schema<cocktail.schema.schema.Schema>}        
        """

    @abstractmethod
    def render(self, item, **kwargs):
        """Produces an image for the given item.

        @param item: The item to render.
        @type item: L{Item<woost.models.item.Item>}

        @param kwargs: Additional parameters that can modify the image produced
            by the renderer. These are implementation dependant, and should
            be described by L{rendering_schema}.

        @return: The image for the given item. If a suitable image file
            exists, the method should return a tuple consisting of a string
            pointing to its path and its MIME type. Otherwise, the method
            should craft the image in-memory and return it as an instance of
            the L{Image<Image.Image>} class.
        @rtype: tuple(str, str) or L{Image<Image.Image>}
        """

    def last_change_in_appearence(self, item):
        """Determines the last time an item was modified in a way that may
        alter its rendering.

        This method is mostly used to check wether cached images are still
        current.

        @param item: The item to evaluate.
        @type item: L{Item<woost.models.item.Item>}

        @return: The timestamp of the last change to the item that could alter
            the resulting image produced by the L{render} method of this
            renderer.
        @rtype: float
        """
        return mktime(item.last_update_time.timetuple())


class ImageFileRenderer(ContentRenderer):
    """A content renderer that handles image files."""

    def can_render(self, item):
        return isinstance(item, File) \
        and item.resource_type == "image" \
        and item.mime_type in formats_by_mime_type

    def render(self, item):
        return (item.file_path, item.mime_type)

    def last_change_in_appearence(self, item):
        return max(
            os.stat(item.file_path).st_mtime,
            ContentRenderer.last_change_in_appearence(self, item)
        )


class ImageURIRenderer(ContentRenderer):

    def can_render(self, item):
        return isinstance(item, URI) and item.resource_type == "image"

    def get_item_uri(self, item):
        return item.uri

    def render(self, item):
        
        # Open the remote resource
        uri = self.get_item_uri(item)
        http_resource = urlopen(uri)

        # Wrap image data in a buffer
        # (the object returned by urlopen() doesn't support seek(), which is
        # required by PIL)
        buffer = StringIO()
        buffer.write(http_resource.read())
        buffer.seek(0)

        return Image.open(buffer)

    def last_change_in_appearence(self, item):
        uri = self.get_item_uri(item)
        urlparts = urlsplit(uri)
        host = urlparts[1]
        path = urlparts[2] + urlparts[3] + urlparts[4]
        http_conn = HTTPConnection(host)
        http_conn.request("HEAD", path)
        http_date = http_conn.getresponse().getheader("last-modified")
        http_conn.close()
        return mktime(strptime(http_date, "%a, %d %b %Y %H:%M:%S %Z"))


class HTMLRenderer(ContentRenderer):
    """A content renderer that handles XHTML/HTML pages."""

    mime_types = set([
        "text/html",
        "text/xhtml",
        "application/xhtml"
    ])

    def can_render(self, item):
        return (
            isinstance(item, Publishable)
            and item.mime_type in self.mime_types            
            and item.is_accessible(
                user = User.get_instance(qname = "woost.anonymous_user")
            )
        )

    @cached_getter
    def rendering_schema(self):
        return schema.Schema("html", members = [
            schema.Integer("window_width", min = 0),
            schema.Integer("window_height", min = 0)
        ])

    def render(self, item, window_width = None, window_height = None):

        temp_path = mkdtemp()

        try:
            temp_image_file = os.path.join(temp_path, "thumbnail.png")
            
            location = Location.get_current_host()
            location.path_info = context["cms"].uri(item)
            
            command = "python -m woost.models.renderurl %s %s" \
                % (unicode(location), temp_image_file)
            
            if window_width is not None:
                command += " --min-width %d" % window_width
            
            if window_height is not None:
                command += " --min-width %d" % window_height 

            Popen(command, shell = True).wait()
            return Image.open(temp_image_file)

        finally:
            rmtree(temp_path)


class IconRenderer(ContentRenderer):

    @cached_getter
    def rendering_schema(self):
        return schema.Schema("icon", members = [
            schema.Integer("size", default = 16)
        ])

    def can_render(self, item):
        return True

    def render(self, item, size):
        icon_file = context["cms"].icon_resolver.find_icon(item, size)
        return (icon_file, guess_type(icon_file)[0])


class VideoRenderer(ContentRenderer):
    """A content renderer that handles video files."""

    try:                                                                                                                                                                                                       
        p = Popen(["which", "ffmpeg"], stdout=PIPE)
        ffmpeg_path = p.communicate()[0].replace("\n", "") or None
    except:
        ffmpeg_path = None
    try:
        p = Popen(["which", "grep"], stdout=PIPE)
        grep_path = p.communicate()[0].replace("\n", "") or None
    except:
        grep_path = None
    try:
        p = Popen(["which", "cut"], stdout=PIPE)
        cut_path = p.communicate()[0].replace("\n", "") or None
    except:
        cut_path = None
    try:
        p = Popen(["which", "sed"], stdout=PIPE)
        sed_path = p.communicate()[0].replace("\n", "") or None
    except:
        sed_path = None

    def _secs2time(self, s):
        ms = int((s - int(s)) * 1000000)
        s = int(s)
        # Get rid of this line if s will never exceed 86400
        while s >= 24*60*60: s -= 24*60*60
        h = s / (60*60)
        s -= h*60*60
        m = s / 60
        s -= m*60
        return datetime.time(h, m, s, ms)
    
    def _time2secs(self, d):
        return d.hour*60*60 + d.minute*60 + d.second + \
            (float(d.microsecond) / 1000000)

    @cached_getter
    def rendering_schema(self):
        return schema.Schema("video", members = [
            schema.Integer("position")
        ])

    def can_render(self, item):
        return (
            self.ffmpeg_path 
            and self.grep_path 
            and self.cut_path
            and self.sed_path 
            and isinstance(item, File) 
            and item.resource_type == "video"
        )

    def render(self, item, position = None):
        
        temp_path = mkdtemp()

        try:

            temp_image_file = os.path.join(temp_path, "thumbnail.png")
            
            command1 = "%s -i %s" % (self.ffmpeg_path, item.file_path)
            command2 = "%s Duration | %s -d ' ' -f 4 | %s 's/,//'" % (
                self.grep_path,
                self.cut_path,
                self.sed_path
            )
            p1 = Popen(command1, shell=True, stderr=PIPE)
            p2 = Popen(command2, shell=True, stdin=p1.stderr, stdout=PIPE)
            duration = p2.communicate()[0]

            duration_list = re.split("[.:]", duration)
            video_length = datetime.time(
                int(duration_list[0]), int(duration_list[1]),
                int(duration_list[2]), int(duration_list[3])
            )   

            if position:
                time = self._secs2time(position)
            else:
                seconds = self._time2secs(video_length)
                time = self._secs2time(seconds / 2)
    
            if time > video_length:
                raise ValueError(
                    "Must specify a smaller position than the video duration."
                )
    
            command = u"%s -y -i %s -vframes 1 -ss %s -an -vcodec png -f rawvideo %s " % (
                self.ffmpeg_path, 
                item.file_path, 
                time.strftime("%H:%M:%S"),
                temp_image_file
            )
    
            p = Popen(command.split(), stdout=PIPE)
            p.communicate()
    
            return Image.open(temp_image_file)

        finally:
            rmtree(temp_path)


    def last_change_in_appearence(self, item):
        return os.stat(item.file_path).st_mtime


class PDFRenderer(ContentRenderer):
    """A content renderer that handles pdf files."""

    try:
        p = Popen(["which", "convert"], stdout=PIPE)
        convert_path = p.communicate()[0].replace("\n", "") or None
    except:
        convert_path = None

    @cached_getter
    def rendering_schema(self):
        return schema.Schema("pdf", members = [
            schema.Integer("page", default = 0)
        ])

    def can_render(self, item):
        return (
            self.convert_path 
            and isinstance(item, File) 
            and item.resource_type == "document"
            and item.file_name.split(".")[-1].lower() == "pdf"
        )

    def render(self, item, page):
        
        TIMEOUT = 10
        RESOLUTION = 0.25
        temp_path = mkdtemp()

        try:

            temp_image_file = os.path.join(temp_path, "thumbnail.png")

            command = u'%s -type TrueColor "%s[%d]" %s' % ( 
                self.convert_path, item.file_path, page, temp_image_file
            )
            p = Popen(command, shell=True, stdout=PIPE)
            start = time()

            while p.poll() is None:
                if time() - start > TIMEOUT:
                    p.terminate()
                    raise IOError("Timeout was reached")
                sleep(RESOLUTION)

            return Image.open(temp_image_file)

        finally:
            rmtree(temp_path)

    def last_change_in_appearence(self, item):
        return os.stat(item.file_path).st_mtime


content_renderers = ContentRenderersRegistry()
content_renderers.register(ImageFileRenderer())
content_renderers.register(ImageURIRenderer())
content_renderers.register(VideoRenderer())
content_renderers.register(PDFRenderer())

# Disabled for performance reasons
# TODO: Provide preferences to enable/disable content renderers?
if False:
    try:
        import PyQt4.QtWebKit
    except ImportError:
        pass
    else:
        content_renderers.register(HTMLRenderer())

icon_renderers = ContentRenderersRegistry()
icon_renderers.register(IconRenderer())

# Image processors
#------------------------------------------------------------------------------
def resolve_px(value, size):
    if isinstance(value, float):        
        value = int(size * value)
    if value < 0:
        value = size + value
    return value

def resolve_color(value):

    if isinstance(value, basestring):

        if len(value) in (3, 4):
            value = tuple(int(d * 2, 16) for d in value)
        elif len(value) == 6:
            value = (
                int(value[0:2], 16),
                int(value[2:4], 16),
                int(value[4:6], 16)
            )
        elif len(value) == 8:
            value = (
                int(value[0:2], 16),
                int(value[2:4], 16),
                int(value[4:6], 16),
                int(value[6:8], 16)
            )
        else:
            raise ValueError("Invalid color: " + value)

    return value

image_processors = OrderedDict()

def image_processor(func):
    image_processors[func.func_name] = func
    return func

@image_processor
def thumbnail(image, width = None, height = None, filter = Image.ANTIALIAS):
    
    im_width, im_height = image.size

    if width is None:
        width = im_width

    if height is None:
        height = im_height

    image.thumbnail(
        (resolve_px(width, im_width),
         resolve_px(height, im_height)),
        filter
    )
    return image

@image_processor
def crop(image, x1, y1, x2, y2):

    width, height = image.size
    return image.crop((
        resolve_px(x1, width),
        resolve_px(y1, height),
        resolve_px(x2, width),
        resolve_px(y2, height)
    ))

@image_processor
def fill(image, width, height, crop = "center", filter = Image.ANTIALIAS):

    source_width, source_height = image.size
    source_ratio = float(source_width) / source_height
    target_ratio = float(width) / height

    if source_ratio > target_ratio:
        target_width = int(height * source_ratio)
        target_height = height
    else:
        target_width = width
        target_height = int(width * (1 / source_ratio))

    image = image.resize((target_width, target_height), filter)

    if crop:
        if crop == "center":
            offset_x = (target_width - width) / 2
            offset_y = (target_height - height) / 2
            image = image.crop((
                offset_x,
                offset_y,
                width + offset_x,
                height + offset_y
            ))
        else:
            raise ValueError("crop = %s not implemented" % crop)

    return image

@image_processor
def rotate(image, angle, expand = True, filter = Image.BICUBIC):
    return image.rotate(angle, filter, expand)

@image_processor
def color(image, level):
    return ImageEnhance.Color(image).enhance(level)

@image_processor
def brightness(image, level):
    return ImageEnhance.Brightness(image).enhance(level)

@image_processor
def contrast(image, level):
    return ImageEnhance.Contrast(image).enhance(level)

@image_processor
def sharpness(image, level):
    return ImageEnhance.Sharpness(image).enhance(level)

@image_processor
def frame(
    image,
    edge = 1,
    edge_color = (0,0,0),
    padding = 0,
    padding_color = (255,255,255)
):
    edge_color = resolve_color(edge_color)
    padding_color = resolve_color(padding_color)

    # Create the canvas
    width, height = image.size
    offset = edge + padding
    canvas = Image.new("RGBA", (width + offset * 2, height + offset * 2))    

    # Paint the border
    if edge:
        canvas.paste(edge_color, None)

    # Paint the padding color
    canvas.paste(
        padding_color,
        (edge,
         edge,
         width + offset * 2 - edge,
         height + offset * 2 - edge)
    )
    
    # Paste the original image over the frame
    canvas.paste(
        image,
        (offset, offset),
        image if image.mode in ("1", "L", "RGBA") else None
    )

    return canvas

@image_processor
def shadow(
    image,
    offset = 5,
    color = (70,70,70),
    padding = 8,
    iterations = 3):   
    
    # Create the backdrop image -- a box in the background colour with a 
    # shadow on it.
    total_width = image.size[0] + abs(offset) + 2 * padding
    total_height = image.size[1] + abs(offset) + 2 * padding
    back = Image.new("RGBA", (total_width, total_height))

    # Place the shadow, taking into account the offset from the image
    shadow_left = padding + max(offset, 0)
    shadow_top = padding + max(offset, 0)
    color = resolve_color(color)
    back.paste(color, [
        shadow_left,
        shadow_top,
        shadow_left + image.size[0], 
        shadow_top + image.size[1]
    ])

    # Apply the filter to blur the edges of the shadow.  Since a small kernel
    # is used, the filter must be applied repeatedly to get a decent blur.
    for n in range(iterations):
        back = back.filter(ImageFilter.BLUR)

    # Paste the input image onto the shadow backdrop
    image_left = padding - min(offset, 0)
    image_top = padding - min(offset, 0)
    back.paste(
        image,
        (image_left, image_top),
        image if image.mode in ("1", "L", "RGBA") else None
    )

    return back

def reduce_opacity(image, opacity):
    # Returns an image with reduced opacity.
    assert opacity >= 0 and opacity <= 1
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    else:
        image = image.copy()
    alpha = image.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
    image.putalpha(alpha)
    return image

@image_processor
def watermark(image, markid, position = "middle", opacity=1):
    
    mark = File.require_instance(int(markid))

    mark_image = Image.open(mark.file_path)

    # Adds a watermark to an image.
    if opacity < 1:
        mark_image = reduce_opacity(mark_image, opacity)
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    
    # create a transparent layer the size of the image and draw the
    # watermark in that layer.
    layer = Image.new('RGBA', image.size, (0,0,0,0))
    if position == 'tile':
        for y in range(0, image.size[1], mark_image.size[1]):
            for x in range(0, image.size[0], mark_image.size[0]):
                layer.paste(mark_image, (x, y), mark_image)
    elif position == 'scale':
        # scale, but preserve the aspect ratio
        ratio = min(
            float(image.size[0]) / mark_image.size[0],
            float(image.size[1]) / mark_image.size[1]
        )
        w = int(mark_image.size[0] * ratio)
        h = int(mark_image.size[1] * ratio)
        mark_image = mark_image.resize((w, h))
        layer.paste(
            mark_image,
            ((image.size[0] - w) / 2, (image.size[1] - h) / 2),
            mark_image
        )
    elif position == 'middle':        
        layer.paste(
            mark_image,
            (
                (image.size[0] - mark_image.size[0]) / 2,
                (image.size[1] - mark_image.size[1]) / 2
            ),
            mark_image
        )
    else:
        raise ValueError(
            "Must specify position parameter [tile,scale,middle]."
        )
    #TODO
    # top-left      top         top-right
    # left          middle      right
    # bottom-left   bottom      bottom-right
    # margin

    # composite the watermark with the layer
    return Image.composite(layer, image, layer)

@image_processor
def flip(image, direction):
    return image.transpose(direction)

@image_processor
def fit(image, width, height, crop = "center", filter = Image.ANTIALIAS):

    if image.size[0] > width or image.size[1] > height:
        if image.size[0] >= image.size[1]:
            image = fill(image, width, height, crop, filter)
        else:
            image.thumbnail((width, height), filter)

    return image

@image_processor
def align(
    image, 
    width = None, 
    height = None, 
    halign = "center", 
    valign = "center", 
    background = None):

    needs_halign = (width and image.size[0] < width)
    needs_valign = (height and image.size[1] < height)

    if needs_halign or needs_valign:
        
        if background:
            background = resolve_color(background)
        elif image.mode == "RGBA":
            background = (0,0,0,0)

        copy = Image.new(
            "RGBA" if background and len(background) == 4 else image.mode,
            (
                width or image.size[0],
                height or image.size[1]
            ), 
            background
        )

        x = 0
        y = 0
            
        if needs_halign:
            if halign == "left":
                pass
            elif halign == "center":
                x = width / 2 - image.size[0] / 2
            elif halign == "right":
                x = width - image.size[0]
            else:
                raise ValueError(
                    "Invalid parameter: align(halign = %r)" % halign
                )

        if needs_valign:
            if valign == "top":
                pass
            elif valign == "center":
                y = height / 2 - image.size[1] / 2
            elif valign == "bottom":
                y = height - image.size[1]
            else:
                raise ValueError(
                    "Invalid parameter: align(valign = %r)" % valign
                )       

        copy.paste(image, (x, y))
        return copy

    return image

