from cgi import escape
from cStringIO import StringIO
import logging

from plone.app.blob.field import BlobField, BlobWrapper
from plone.app.blob.interfaces import IBlobImageField
from plone.app.blob.mixins import ImageFieldMixin
from zope.event import notify
from zope.interface import implements

from AccessControl import ClassSecurityInfo
import PIL.Image
from ZODB.POSException import ConflictError

from Products.Archetypes.utils import shasattr
from Products.Archetypes.Registry import registerField
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName

from Products.RichImage.widget import RichImageWidget
from Products.RichImage.events import CropModifiedEvent

_marker = []
logger = logging.getLogger('Products.RichImage')

HAS_LINGUA = True
try:
    import Products.LinguaPlone
except ImportError:
    HAS_LINGUA = False


class RichImageField(BlobField, ImageFieldMixin):
    """ """
    implements(IBlobImageField)

    _properties = ImageFieldMixin._properties.copy()
    _properties.update({
        'crops': {'header':(0, 0, 400, 100)},
        'createCropsOnSet': True, # Either True, False or an iterable of crop ids
        'ui_crop_scale': 'large',
        'swallowCropExceptions': False,
        'widget': RichImageWidget,})

    security = ClassSecurityInfo()

    security.declarePrivate('set')
    def set(self, instance, value, **kwargs):
        super(RichImageField, self).set(instance, value, **kwargs)
        if value=="DELETE_IMAGE":
            # XXX This method doesn't exist
            # raise LazyImplementorError
            self.removeCrops(instance, **kwargs)
            return
        if self.createCropsOnSet:
            self.createCrops(instance, value)

    security.declarePrivate('removeScales')
    def removeScales(self, instance, **kwargs):
        """Remove the scaled image
        """
        super(RichImageField, self).removeScales(instance, **kwargs)
        crops = self.getAvailableCrops(instance)
        if crops:
            for name, crop in crops.items():
                id = self.getName() + "_" + name
                try:
                    # the following line may throw exceptions on types, if the
                    # type-developer add sizes to a field in an existing
                    # instance and a user try to remove an image uploaded before
                    # that changed. The problem is, that the behavior for non
                    # existent keys isn't defined. I assume a keyerror will be
                    # thrown. Ignore that.
                    self.getStorage(instance).unset(id, instance, **kwargs)
                except KeyError:
                    pass

    security.declareProtected(permissions.View, 'getAvailableCrops')
    def getAvailableCrops(self, instance):
        """ """
        return self.crops

    security.declareProtected(permissions.ModifyPortalContent, 'createCrops')
    def createCrops(self, instance, value):
        """creates the crops and save them
        """
        crops = self.getAvailableCrops(instance)

        # Let createCropsOnSet limits the number of crops to create
        if isinstance(self.createCropsOnSet, (set, tuple, list)):
            available = crops
            crops = {}
            for crop in self.createCropsOnSet:
                if crop in available:
                    crops[crop] = available[crop]

        if not crops:
            return
        if value is _marker:
            img = self.getRaw(instance)
            if not img:
                return
            data = str(img.data)
        else:
            data = value
        if not data:
            return

        canonical = None
        if HAS_LINGUA:
            if not instance.isCanonical():
                canonical = instance.getCanonical()
                canon_field = canonical.getField(self.getName())

        filename = self.getFilename(instance)
        for n, crop in crops.items():
            if crop == (0, 0, 0, 0):
                continue
            x1, y1, x2, y2 = crop
            id = self.getName() + "_" + n
            __traceback_info__ = (self, instance, id, x1, y1, x2, y2)

            try:
                if canonical is not None and self.languageIndependent:
                    imgdata = canon_field.getCrop(canonical,
                                                  n, unwrapped=True).data
                    format = canon_field.getContentType(canonical)
                else:
                    imgdata, format = self._crop(data,
                                                 x1, y1, x2, y2,
                                                 initialize=True)
            except (ConflictError, KeyboardInterrupt):
                raise
            except:
                if not self.swallowCropExceptions:
                    raise
                else:
                    logger.exception()
                    # crop failed, don't create a croped version
                    continue

            mimetype = 'image/%s' % format.lower()
            image = self._make_image(id, title=self.getName(), file=imgdata,
                                     content_type=mimetype, instance=instance)
            image.filename = filename
            try:
                delattr(image, 'title')
            except (KeyError, AttributeError):
                pass
            # manually use storage
            self.getStorage(instance).set(id,
                                          instance,
                                          image,
                                          mimetype=mimetype,
                                          filename=filename)


    security.declareProtected(permissions.ModifyPortalContent, 'editCrop')
    def editCrop(self, instance, id, x1, y1, x2, y2, scale=1, forced_size = False):
        """creates the crops and save them
        """
        self._createCrop(instance, id, x1, y1, x2, y2, scale=scale)

    def _createCrop(self, instance, id, x1, y1, x2, y2, scale=None, forced_size = False):
        #Calculate scale
        selectedWidth = float(int(x2)-int(x1))

        if forced_size:
            force_width = cropWidth = self.crops[id][2]
            force_height = cropHeight = self.crops[id][3]
        else:
            force_width = None
            force_height = None

        id = self.getName() + '_' + id
        img = self.getRaw(instance)
        if not img:
            return
        data = str(img.data)
        if not data:
            return

        filename = self.getFilename(instance)
        __traceback_info__ = (self, instance, id, x1, y1, x2, y2)
        try:
            imgdata, format = self._crop(data,
                                        int(x1),
                                        int(y1),
                                        int(x2),
                                        int(y2),
                                        scale=scale,
                                        force_width = force_width,
                                        force_height = force_height,)
        except (ConflictError, KeyboardInterrupt):
            raise
        except:
            if not self.swallowCropExceptions:
                raise
            else:
                logger.exception()
        mimetype = 'image/%s' % format.lower()
        image = self._make_image(id, title=self.getName(), file=imgdata,
                                 content_type=mimetype, instance=instance)
        image.filename = filename
        try:
            delattr(image, 'title')
        except (KeyError, AttributeError):
            pass
        # manually use storage
        self.getStorage(instance).set(id,
                                      instance,
                                      image,
                                      mimetype=mimetype,
                                      filename=filename)
        notify(CropModifiedEvent(self.getName(), id, instance, image))


    #security.declarePrivate('crop')
    def _crop(self, data, x1, y1, x2, y2,
             scale=None, initialize=False,
             default_format = 'JPEG', force_width = None, force_height = None):
        """ crop image """
        crop = (int(x1), int(y1), int(x2), int(y2))
        if isinstance(data, str):
            original_file=StringIO(data)
        elif isinstance(data, BlobWrapper):
            original_file = StringIO(data.data)
        else:
            data.seek(0)
            original_file=StringIO(data.read())
        image = PIL.Image.open(original_file)
        original_format = image.format and image.format or default_format
        original_mode = image.mode
        if original_mode == '1':
            image = image.convert('L')
        elif original_mode == 'P':
            image = image.convert('RGBA')
        destx, desty = image.size

        if scale:
            scale = float(scale)
            # the image is cropped manually
            x1 = int(x1*scale)
            x2 = int(x2*scale)
            y1 = int(y1*scale)
            y2 = int(y2*scale)

            crop = (x1, y1, x2, y2)
            newwidth = int(destx*scale)
            newheight = int(desty*scale)
            image = image.resize((newwidth,newheight), PIL.Image.ANTIALIAS)

        else:
            # scale up if needed
            if x2 > destx or y2 > desty:
                if x2 > destx: destx = x2
                if y2 > desty: desty = y2
                maxsize = (destx, desty)
                imaspect = float(image.size[0])/float(image.size[1])
                outaspect = float(maxsize[0])/float(maxsize[1])
                if imaspect < outaspect:
                    image = image.resize((maxsize[0],
                                      int((float(maxsize[0])/imaspect) + 0.5)),
                                     PIL.Image.ANTIALIAS)
                else:
                    image = image.resize((int((float(maxsize[1])*imaspect) + 0.5),
                                      maxsize[1]),
                                     PIL.Image.ANTIALIAS)
            # scale down if needed
            if x2 < destx and y2 < desty:
                destx = x2
                desty = y2
                maxsize = (destx, desty)
                imaspect = float(image.size[0])/float(image.size[1])
                outaspect = float(maxsize[0])/float(maxsize[1])
                if imaspect < outaspect:
                    image = image.resize((maxsize[0],
                                      int((float(maxsize[0])/imaspect) + 0.5)),
                                     PIL.Image.ANTIALIAS)
                else:
                    image = image.resize((int((float(maxsize[1])*imaspect) + 0.5),
                                      maxsize[1]),
                                     PIL.Image.ANTIALIAS)


        # force an accurate crop width and height
        x1, y1, x2, y2 = crop
        if force_width:
           width_diff = x2 - x1 - force_width
           x1 =  x1 + width_diff
           if x1 < 0:
              # reset x
              x1 = 0
              x2 = force_width
        if force_height:
           height_diff = y2 - y1 - force_height
           y1 =  y1 + height_diff
           if y1 < 0:
              # reset y
              y1 = 0
              y2 = force_height

        # one more check ...
        if x2 > image.size[0]: x2 = image.size[0]
        if y2 > image.size[1]: y2 = image.size[1]
        crop = (x1, y1, x2, y2)

        # the first time we want crop from the center
        if initialize == True:
            x1, y1, x2, y2 = crop
            imgx, imgy = image.size
            xt1 = imgx/2 - (x2-x1)/2
            yt1 = imgy/2 - (y2-y1)/2
            xt2 = imgx/2 + (x2-x1)/2
            yt2 = imgy/2 + (y2-y1)/2
            crop = xt1, yt1, xt2, yt2

        # does the actual crop
        image = image.crop(crop)
        format = original_format
        if original_mode == 'P' and format in ('GIF', 'PNG'):
            image = image.convert('P')
        thumbnail_file = StringIO()
        # quality parameter doesn't affect lossless formats
        image.save(thumbnail_file, format, quality=self.pil_quality)
        thumbnail_file.seek(0)
        return thumbnail_file, format.lower()

    security.declareProtected(permissions.View, 'getCrop')
    def getCrop(self, instance, crop=None, **kwargs):
        """Get crop
        """
        if crop is None:
            return self.get(instance, **kwargs)
        else:
            assert(crop in self.getAvailableCrops(instance).keys(),
                   'Unknown crop %s for %s' % (crop, self.getName()))
            id = self.getScaleName(scale=crop)
            try:
                image = self.getStorage(instance).get(id, instance, **kwargs)
            except AttributeError:
                return ''
            image = self._wrapValue(instance, image, **kwargs)
            if shasattr(image, '__of__', acquire=True) and not kwargs.get('unwrapped', False):
                return image.__of__(instance)
            else:
                return image

    security.declarePublic('get_size')
    def get_size(self, instance):
        """Get size of the stored data including crops
        """
        size = super(RichImageField, self).get_size(instance)
        crops = self.getAvailableCrops(instance)
        original = self.get(instance)

        if crops:
            for crop in crops.keys():
                id = self.getScaleName(scale=crop)
                try:
                    data = self.getStorage(instance).get(id, instance)
                except AttributeError:
                    pass
                else:
                    size+=data and data.get_size() or 0
        return size

    security.declareProtected(permissions.View, 'getSize')
    def getSize(self, instance, scale=None):
        """ get size of scale, crop or original """
        if scale is not None:
            crops = self.getAvailableCrops(instance)
            if scale in crops:
                x1, y1, x2, y2 = crops[scale]
                return abs(x2 - x1), abs(y2 - y1)
        return super(RichImageField, self).getSize(instance, scale)

    security.declarePublic('tag')
    def tag(self, instance, scale=None, height=None, width=None, alt=None,
            css_class=None, title=None, **kwargs):
        """Create a tag including crop
        """
        available_crops = self.getAvailableCrops(instance)
        if scale in available_crops:
            image = self.getCrop(instance, crop=scale)
            membership = getToolByName(instance, 'portal_membership')
            allowed = membership.checkPermission(
                permissions.ModifyPortalContent, instance)
            if not image:
                if allowed:
                    x1, y1, x2, y2 = available_crops[scale]
                    self._createCrop(instance, scale, x1, y1, x2, y2)
                    image = self.getCrop(instance, scale=scale)
                else:
                    image = self.getScale(instance, scale=scale)
        else:
            image = self.getScale(instance, scale=scale)

        if image:
            img_width, img_height = self.getSize(instance, scale=scale)
        else:
            img_height=0
            img_width=0

        if height is None:
            height=img_height
        if width is None:
            width=img_width

        url = instance.absolute_url()
        if scale:
            url+= '/' + self.getScaleName(scale)
        else:
            url+= '/' + self.getName()

        values = {'src' : url,
                  'alt' : escape(alt and alt or instance.Title(), 1),
                  'title' : escape(title and title or instance.Title(), 1),
                  'height' : height,
                  'width' : width,
                 }

        result = '<img src="%(src)s" alt="%(alt)s" title="%(title)s" '\
                 'height="%(height)s" width="%(width)s" id="thumbnail"' % values

        if css_class is not None:
            result = '%s class="%s"' % (result, css_class)

        for key, value in kwargs.items():
            if value:
                result = '%s %s="%s"' % (result, key, value)

        return '%s />' % result

    security.declarePublic('crop_tag')
    def crop_tag(self, instance, crop_id):
        """Return the proper tag"""
        img=self.tag(instance)
        if not img:
            return None
        if not self.getCrop(instance, crop=crop_id):
            return None
        return self.tag(instance, scale=crop_id)

    def cropEditRatio(self, instance):
        """Return the width and height ratio for the edit crop template"""
        ui_image = self.getScale(instance, self.ui_crop_scale)
        full_image = self.getRaw(instance)

        ui_width = float(ui_image.width)
        ui_height = float(ui_image.height)
        full_width = float(full_image.width)
        full_height = float(full_image.height)

        return (full_width / ui_width, full_height / ui_height)

registerField(
    RichImageField, title='Image with crop',
    description='An image field with parametric scales and cropping')
