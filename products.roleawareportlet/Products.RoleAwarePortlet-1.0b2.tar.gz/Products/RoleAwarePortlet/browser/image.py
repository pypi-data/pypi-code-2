from Products.Five.browser import BrowserView
import mimetypes
import os.path
import StringIO
from PIL import Image
from plone.memoize.ram import cache

def cache_key(fun, self, file, size):
    return (file.data, size[0], size[1])

class ImageView(BrowserView):

    def __call__(self, w=100, h=100):
        file = self.context.image
        if file.filename:
            extension = os.path.splitext(file.filename)[1].lower()
            contenttype = mimetypes.types_map.get(extension,
                                                  "application/octet-stream")
        elif file.contentType:
            contenttype = file.contentType
        else:
            contenttype = "application/octet-stream"
        self.request.response.setHeader("Content-Type", contenttype)
        return self.thumb(file, (int(w),int(h)))

    @cache(cache_key)
    def thumb(self, file, size):
        data = StringIO.StringIO(file.data)
        image = Image.open(data)
        original_mode = image.mode
        format = image.format
        if original_mode == '1':
            image = image.convert('L')
        elif original_mode == 'P':
            image = image.convert('RGBA')
        image.thumbnail(size, Image.ANTIALIAS)
        if original_mode == 'P' and format in ('GIF', 'PNG'):
            image = image.convert('P')
        thumb = StringIO.StringIO()
        image.save(thumb, format, quality=100)
        thumb.seek(0)
        img = thumb.read()
        thumb.close()
        data.close()
        return img

