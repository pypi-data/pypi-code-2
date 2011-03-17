'''
Picasa Module
========================

Use to parse the contacts.xml and .picasa.ini files which are geneterated by
Picasa

.. note:: This version is tested against Picasa 3.8

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

# W0142 Yes we're making use of ** magic on purpose here...
# pylint: disable=W0142

import os
import xml.parsers.expat
import logging
from ConfigParser import SafeConfigParser
from py2facer.lib.utils import InvalidConfig, ParseError

LOGGER = logging.getLogger('lib.picasa')

class ContactParser(object):
    LOGGER = LOGGER.getChild('ContactParser')
    
    def __init__(self):
        '''Used to load and parse a contacts.xml file from Picasa.
        
        :ivar _contacts: :obj:`dict` of Google hash values :obj:`Contact` 
            objects.
        '''
        
        self._contacts = {}
    
    def __getitem__(self, idx):
        '''Allows the ContactParser to pretend it's a dictionary
        
        :rtype: :obj:`Contact`
        '''
        
        return self._contacts[idx]
    
    def __contains__(self, key):
        '''Allows the ContactParser to pretend it's a dictionary
        
        :rtype: Boolean
        '''
        
        return key in self._contacts
    
    def parse_xml(self, in_stream):
        '''Used to actually do the parsing of the contacts.xml file
        
        :param :obj:`File` in_stream: A file-like object that can be iterated 
            over
        '''
        
        REQUIRED_FIELDS = ('id', 'name', 'email0')
        
        def start_element(name, attrs):                                                                                                                                  
            if name != 'contact':
                return
            self.LOGGER.debug('New contact: %s' % attrs)
            for field in REQUIRED_FIELDS:
                if field not in attrs:
                    self.LOGGER.info('Invalid contact data (missing %s): %s',
                                     field, attrs)
                    return
            options = {'name' : attrs['name'],
                       'emails' : [],
                       'google_hash' : attrs['id']}
            for key, val in attrs.iteritems():
                if key.startswith('email'):
                    options['emails'].append(val)
            self._contacts[attrs['id']] = Contact(**options)
            
        if in_stream is None:
            return
        self.LOGGER.debug('Parsing contact information')
        p = xml.parsers.expat.ParserCreate()
        p.StartElementHandler = start_element
        for line in in_stream:
            p.Parse(line)
        p.Parse('', 1)
    
    def has_key(self, key):
        '''Allows the ContactParser to pretend it's a dictionary
        
        :rtype: Boolean
        '''
        
        return self._contacts.has_key(key)
    
    def iteritems(self):
        '''Allows the ContactParser to pretend it's a dictionary
        
        :rtype: iterator
        '''
        
        return self._contacts.iteritems() 
    
class Contact(object):
    def __init__(self, name, emails, google_hash):
        '''An individual Google contact
        
        :param name: Full name of the contact
        :type name: :obj:`str`
        :param emails: List of e-mails associated with this contact
        :type emails: A :obj:`list` or :obj:`tuple` of :obj:`str` objects or a 
            single :obj:`str`
        :param google_hash: The hash value of this :obj:`Contact`
        :type google_hash: :obj:`str`
        
        :ivar name: :obj:`str` name of the contact
        :ivar emails: :obj:`list` of the e-mails associated with this contact
        :ivar google_hash: :obj:`str` Google hash value of the contact 
        '''
        
        self.name = name
        # A user can have several e-mail addresses
        if type(emails) in (str, unicode):
            self.emails = [emails, ]
        elif type(emails) in (list, tuple):
            if len(emails) == 0:
                raise AttributeError('emails cannot be an empty list')
            self.emails = list(emails)
        else:
            raise InvalidConfig('emails must be str, unicode, or iterable')
        self.google_hash = google_hash

class FaceParser(object):
    LOGGER = LOGGER.getChild('FaceParser')
    
    def __init__(self):
        '''Class used to parse .picasa.ini files.
        
        The .picasa.ini files contain (among other things) the facial data
        for all the images in the directory the .picasa.ini file is in.
        
        :ivar _ini_files: A :obj:`dict` object of path --> parsed data 
        '''
         
        self._ini_files = {}
    
    def add_people_to_image(self, image, bounding_box=True):
        '''Add people to an image based on the Picasa ini
        
        :param image: An :obj:`lib.Image` object to add facial data to
        :type image: :obj:`lib.Image`
        :keyword bounding_box: Should the bounding box for individual faces be 
            parsed.
        :type bounding: Boolean
        '''
        
        if type(image) not in (list, tuple):
            image = [image,]
        self.LOGGER.info('Adding facial data to Image objects') 
        for img in image:
            if img.path not in self._ini_files:
                self._parse_directory(img.path)
            if img.filename not in self._ini_files[img.path]:
                continue
            if img.filename in self._ini_files[img.path]:
                for idx in range(0, len(self._ini_files[img.path][img.filename])):
                    face = self._ini_files[img.path][img.filename][idx]
                    if bounding_box:
                        (top, left, width, height) = self._parse_location(
                                  face['pos'], img)
                        face['y_pos'] = top
                        face['x_pos'] = left
                        face['width'] = width
                        face['height'] = height
                    del face['pos']
                    img.add_face(**face)
    
    def _parse_directory(self, path):
        '''Parse the .picasa.ini file in a directory and cache it.
        
        .. note:: If a path does not exist, it is silently skipped
         
        :param paths: A single path to check
        :type paths: :obj:`str`
        :keyword parse_location: Parse the location of the face in the picture 
            (Default: True)
        :type parse_location: Boolean
        '''
        
        if not os.path.exists(path):
            self.LOGGER.warn('%s does not exist, skipping', path)
            return
        if not os.path.exists('%s%s.picasa.ini' % (path, os.path.sep)):
            self.LOGGER.warn('Unable to find %s%s.picasa.ini in %s. '
                             'Perhaps this directory has not been parsed '
                             'by Picasa? Skipping it for now.' % 
                             (path, os.path.sep, path))
            return
        self._ini_files[path] = self._parse_ini(open('%s%s.picasa.ini' % 
                                                     (path, os.path.sep)), path)
    
    def _parse_location(self, pos, image):
        '''Parse the rect64 data from the .picasa ini file to absolute 
        coordinates in the image
        
        :param pos: The position information from the .picasa.ini file
        :type pos: :obj:`str` in the form `rect64(hex)`
        :return: Bounding box info in (top, left, width, height)
        :type: :obj:`tuple`
        '''
        
        lft = int(pos[7:11], 16)/65535.0
        top = int(pos[11:15], 16)/65535.0
        right = int(pos[15:19], 16)/65535.0
        bottom = int(pos[19:23], 16)/65535.0
        top = int(image.height * top)
        lft = int(image.width * lft)
        right = int(image.width * right)
        bottom = int(image.height * bottom)
        return (top, lft, right - lft, bottom - top)
        
    def _parse_ini(self, in_stream, base_path):
        '''Parse the actual .picasa.ini file and load the facial data
        
        :param in_stream: An input stream (:obj:`File` like object) 
        '''
        
        self.LOGGER.debug('Parsing the .picasa.ini file for: %s', base_path)
        files = os.listdir(base_path)
        parser = SafeConfigParser()
        parser.readfp(in_stream)
        parsed_images = {}
        for section in parser.sections():
            if section == 'Contacts':
                continue
            if section not in files:
                continue
            if not parser.has_option(section, 'faces'):
                continue
            normalized = os.path.normcase(section)
            parsed_images[normalized] = []
            faces = parser.get(section, 'faces').split(';')
            for face in faces:
                pos, google_id = face.split(',')
                parsed_images[normalized].append({'google_id' : google_id,
                                               'pos' : pos})
        return parsed_images
