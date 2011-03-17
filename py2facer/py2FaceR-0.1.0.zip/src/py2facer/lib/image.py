'''
Image Module
============

Used to work with jpg images. 
'''

license = ''' Copyright (C) 2011  <see AUTHORS file>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

from PIL import IptcImagePlugin, ExifTags
from py2facer.lib.utils import InvalidConfig, InvalidState
import datetime
import logging
import md5
import os.path

LOGGER = logging.getLogger('lib.image')

class Image(object):
    
    LOGGER = LOGGER.getChild('Image')
    
    class ContainedPerson(object):
        LOGGER = LOGGER.getChild('Image')
        
        def __init__(self, google_id, x_pos=None, y_pos=None, width=None, 
                     height=None):
            '''A generic contained person inside an image
            
            .. note:: Bounding box coordinates are in pixels relative to the 
                absolute size of the image and where the top left corner is 0,0
            
            :param google_id: The Google hash of the contained person
            :type google_id: :obj:`str`
            :keyword x_pos: The top left x-coord of the bounding box
            :type x_pos: :obj:`int`
            :keyword y_pos: The top left y-coord of the bounding box
            :type y_pos: :obj:`int`
            :keyword width: The width of the bounding box in pixels
            :type width: :obj:`int`
            :keyword height: The height of the bounding box in pixels
            :type height: :obj:`int`
            
            :ivar google_id: :obj:`str` The Google hash of the contact
            '''
            
            self.google_id = google_id
            self.__other_id = {}
            self.__x_pos = x_pos
            self.__y_pos = y_pos
            self.__width = width
            self.__height = height
        
        def add_id(self, id, val):
            '''This is used to add extra linking information to a 
            :obj:`Image.ContainedPerson`. The :mod:`flickr` module uses it to attach
            the flickr_id as well as the flickr_username.
            
            Before adding your id, it's probably a good idea to check
            :meth:`has_id` first. 
            
            :param id: Hashable key
            :param val: Any object
            
            :raises: :exc:`InvalidState` if a non-unique ID is being used
            '''
            
            if id in self.__other_id:
                raise InvalidState('A linking ID can only be set once')
            self.__other_id[id] = val

        def get_id(self, id):
            '''Return the value associated with an ID or :obj:`None` if that ID 
            does not exist.
            
            .. note:: A return value of :obj:`None` is not the same as checking the ID 
                for existence. It is entirely possible to have an ID associated 
                with :obj:`None`, which may have some special meaning.
            
            :param id: The key to lookup
            :returns: The object stored with the ID or :obj:`None`
            '''
            
            if id not in self.__other_id:
                return None            
            return self.__other_id[id]
        
        def has_id(self, id):
            '''Returns the :obj:`dict` equivalent of ``key in dict``
            
            :returns: True or False
            '''
            
            return id in self.__other_id
        
        @property
        def x_pos(self):
            '''Property for getting the top left x coord for the bounding box
            '''
            
            return self.__x_pos
        
        @property
        def y_pos(self):
            '''Property for getting the top left y coord for the bounding box
            '''
            
            return self.__y_pos
        
        @property
        def width(self):
            '''Property for getting the width of the bounding box in pixels
            '''
            
            return self.__width
        
        @property
        def height(self):
            '''Property for getting the height of the bounding box in pixels
            '''
            
            return self.__height
        
        @property
        def has_position(self):
            '''A Boolean property to determine if the 
            :obj:`Image.ContainedPerson` has a bounding box.
            '''
            
            return (self.__x_pos is not None and
                    self.__y_pos is not None and
                    self.__height is not None and
                    self.__width is not None)
            
    def __init__(self, image_path):
        '''A lazy Image object to make working with JPG images a bit easier.
        Image data is only read when it is actually required.
        
        The Image object is iterable, but yields :obj:`Image.ContainedPerson`
        instances
        
        :param image_path: A path to the image file
        :type image: :obj:`str`
        
        :raises: :exc:`InvalidConfig` if the image_path does not exist
        '''
        
        if not os.path.exists(image_path):
            raise InvalidConfig('%s does not exist!' % image_path)
        self._image_path = os.path.abspath(image_path)
        self._people = []
        self._exif = None
        self._iptc = None
        self._checksum = None
        self._width = None 
        self._height = None
    
    def __iter__(self):
        for person in self._people:
            yield person
        raise StopIteration
    
    @property
    def people(self):
        '''Get a shallow copy of the people contained in the photo that is safe
        for modification.
        
        :returns: :obj:`list` of :obj:`Image.ContainedPerson`
        :rtype: :obj:`list`
        '''
        
        return self._people[:]
    
    def __str__(self):
        return self._image_path
    
    def __unicode__(self):
        return u'%s' % self._image_path
    
    def _readimg(self, get_md5=False):
        '''Do the actual reading of the image data.
        
        
        :keyword get_md5: Generate a psuedo-fingerprint for the image
        :type get_md5: Boolean
        '''
        
        self.LOGGER.debug('Reading image data: %s', self._image_path)
        img = IptcImagePlugin.Image.open(self._image_path, 'r')
        if self._exif is None:
            self._exif = {}
            img_exif = img._getexif()
            if img_exif is not None:
                for key, val in img_exif.iteritems():
                    mapped_key = ExifTags.TAGS.get(key, key)
                    self._exif[mapped_key] = val
        if self._iptc is None:
            self._iptc = IptcImagePlugin.getiptcinfo(img)
        if self._width is None:
            self._width, self._height = img.size
        if get_md5 and self._checksum is None:
            self.LOGGER.debug('Calculating psuedo-checksum for image.')
            checksum = md5.new()
            # While not a guarantee of uniqueness, the MD5 of the histogram and 
            # the filename should be enough to give us a "good enough" image id
            checksum.update(str(img.histogram()))
            self._checksum = checksum.hexdigest()
        self.LOGGER.debug('Image data loaded.')
    
    def add_face(self, google_id, x_pos=None, y_pos=None, width=None, 
                 height=None):
        '''
        
        :param google_id: The Google hash of the contained person
        :type google_id: :obj:`str`
        :keyword x_pos: The top left x-coord of the bounding box
        :type x_pos: :obj:`int`
        :keyword y_pos: The top left y-coord of the bounding box
        :type y_pos: :obj:`int`
        :keyword width: The width of the bounding box in pixels
        :type width: :obj:`int`
        :keyword height: The height of the bounding box in pixels
        :type height: :obj:`int`
        '''
        
        # If any keyword arg is not none, then ALL must be not none
        if (x_pos is not None or y_pos is not None or
            width is not None or height is not None):
            if not (x_pos is not None and y_pos is not None and
                    width is not None and height is not None):
                raise InvalidConfig('If any keyword arg is not None, then ALL must not be none')
            if x_pos > self.width or (x_pos + width) > self.width:
                raise InvalidState('Face (%s) in image %s X boundry or boundry+'
                                   'width is > total image width' % (google_id, self))
        self._people.append(Image.ContainedPerson(google_id, x_pos=x_pos, 
                                           y_pos=y_pos, width=width, 
                                           height=height))
    
    @property
    def exif(self):
        '''Easy access to the EXIF data for an image
        '''
        
        if self._exif is None:
            self._readimg()
        return self._exif
    
    @property
    def iptc(self):
        '''Easy access to the IPTC data for an image
        '''
        
        if self._iptc is None:
            self._readimg()
        return self._iptc
    
    @property
    def date_taken(self):
        '''A :obj:`datetime.datetime` based on the DateTimeOriginal field of
        the exif data
        '''
        
        if 'DateTimeOriginal' in self.exif:
            return datetime.datetime.strptime(self.exif['DateTimeOriginal'],
                                              '%Y:%m:%d %H:%M:%S')
        return None
    
    @property
    def checksum(self):
        '''The psuedo-fingerprint of the image
        '''
        
        if self._checksum is None:
            self._readimg(get_md5=True)
        return self._checksum
    
    
    @property
    def height(self):
        '''The height of the image in pixels
        '''
        
        if self._height is None:
            self._readimg()
        return self._height
    
    @property
    def path(self):
        '''The absolute directory of the image
        '''
        
        return os.path.dirname(self._image_path)
    
    @property
    def filename(self):
        '''The normalized form of the filename for the image
        '''
        
        return os.path.normcase(os.path.basename(self._image_path))
    
    @property
    def width(self):
        '''The width of the image in pixels
        '''
        
        if self._width is None:
            self._readimg()
        return self._width

def dir_images(path):
    '''Return a list of :obj:`Image` instances for all images in a path
    
    :param path: Path to return image instances for
    :type path: :obj:`str`
    :return: :obj:`list` of :obj:`Image` instances
    :rtype: :obj:`list`
    '''
    
    LOGGER.info('Loading images from: %s', path)
    images = []
    for filename in os.listdir(path):
        #TODO: This will need updating if we ever handle more than just jpg 
        if os.path.splitext(filename)[1].lower() == '.jpg':
            images.append(Image(image_path='%s%s%s' % 
                                (path, os.path.sep, filename)))
    return images