'''
Flickr Module
=============

This handles all the interacetions with the FlickrAPI module as well as dealing
with mapping contacts <--> flickr accounts and local 
image files <--> flickr images

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

# W0232: SQLAlchemy table classes don't have init methods
# pylint: disable=W0232

from py2facer.lib.utils import InvalidConfig, InvalidState
import flickrapi
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, DateTime
from sqlalchemy.orm.exc import NoResultFound
import sqlalchemy
from sqlalchemy.orm.session import sessionmaker
import logging
from py2facer.lib.image import Image
import datetime

# Yes I know I'm not making this hard to find. 
# You can find the Flickr Uploadr key too ya know

APIKEY = "7c8119c2972b593c317c5f349943e8de"
APISECRET = "09c2db946d396121"
LOGGER = logging.getLogger('lib.flickr')

#: SQL Alchemy magic.
Base = declarative_base()

class DbProxy(object):
    
    def __init__(self, db_url, db_debug=None):
        '''Used to share the session object between classes more easily
        
        :param db_url: the URL to the database to use 
          (normally sqlite:///myfile.db)
        :type db_url: :obj:`str`
        :param db_debug: Set True to enable SQLAlchemy debugging
        :type db_debug: Boolean
        '''
        
        if db_debug is None:
            db_debug = False
        self._engine = sqlalchemy.create_engine(db_url, echo=db_debug)
        Base.metadata.bind = self._engine
        Base.metadata.create_all()
        self._sessionmkr = sessionmaker(bind=self._engine)
    
    def get_session(self):
        '''Return a SQLAlchemy session object
        
        :return: :obj:`~sqlalchemy.orm.session.Session`
        '''
        
        return self._sessionmkr()
    
class FlickrContact(Base):
    '''Linking information between Flickr contacts and google contacts
    '''

    __tablename__ = 'flickr_contact'
    #: Used as the other_id key in an Image object
    CONTACT_ID = 'flickr_nsid'
    #: Used as the other_id key in an Image object
    USERNAME = 'flickr_usename'
    
    id = Column(Integer, primary_key=True)
    #: Flickr ID
    nsid = Column(String)
    #: Flickr username
    username = Column(String)
    google_hash = Column(String)

    def __init__(self, nsid=None, username=None, google_hash=None):
        '''SQLAlchemy table for storing contact linking information between
        Google and flickr
        
        :param nsid: The flickr ID of the user
        :type nsid: :obj:`str`
        :param username: The flickr username for the user
        :type username: :obj:`str`
        :param google_hash: The hash id of the user from Google
        :type google_hash: :obj:`str`
        '''
        
        self.nsid = nsid
        self.username = username
        self.google_hash = google_hash
    
    @classmethod
    def google_to_flickr(cls, session, ghash):
        '''
        
        :param cls: The class
        :type cls: :class:`FlickrContact`
        :param session: Session connection to use for the query
        :type session: :obj:`~sqlalchemy.orm.session.Session`
        :param ghash: The hash id of the user from Google
        :type ghash: :obj:`str`
        '''
        
        query = session.query(cls).filter(cls.google_hash == ghash)
        try:
            contact = query.one()
            return contact.nsid, contact.username
        except NoResultFound:
            return None

class FlickrFace(Base):
    '''Faces that are contained in photos, with the ghash and flickr ID
    
    At this time this table is unused. It can be used for caching later to
    reduce the number of queriest to Flickr, but there's the question of
    "What happens if someone removes a face directly from the image?"
    '''
    
    __tablename__ = 'flickr_face_image'
    #: Primary key
    id = Column(Integer, primary_key=True)
    #: Flickr image ID
    image_id = Column(Integer, ForeignKey('flickr_image.id'))
    
class FlickrImage(Base):

    __tablename__ = 'flickr_image'
    id = Column(Integer, primary_key=True)
    #: Flickr image ID
    photo_id = Column(Integer)
    #: Flickr photo secret id used for generating links
    photo_secret = Column(String)
    #: Local filename of the image
    filename = Column(String)
    checksum = Column(String)
    photo_date = Column(DateTime)
    #: When flickr thinks the photo was taken
    flickr_photo_date = Column(DateTime)
    flickr_title = Column(String)

    def __init__(self, photo_id=None, photo_secret=None, filename=None,
                 checksum=None, photo_date=None, flickr_photo_date=None,
                 flickr_title=None):
        '''Linking information between a Flickr image and a local image
        
        :param photo_id: Flickr image ID
        :type photo_id: :obj:`int`
        :param photo_secret: Flickr photo secret id used for generating links
        :type photo_secret: :obj:`str`
        :param filename: Local filename of the image
        :type filename: :obj:`str`
        :param checksum: psuedo image checksum
        :type checksum: :obj:`str`
        :param photo_date: Date the photo was taken
        :type photo_date: :obj:`~datetime.datetime`
        :param flickr_photo_date: When flickr thinks the photo was taken
        :type flickr_photo_date: :obj:`~datetime.datetime`
        :param flickr_title: The title of the image on flickr
        :type flickr_title: :obj:`str`
        '''

        self.photo_id = photo_id
        self.photo_secret = photo_secret
        self.filename = filename
        self.checksum = checksum
        self.photo_date = photo_date
        self.flickr_photo_date = flickr_photo_date
        self.flickr_title = flickr_title
        
class FlickrContactManager(object):

    LOGGER = LOGGER.getChild('FlickrContactManager')

    def __init__(self, db_proxy, flickr_proxy=None):
        '''Management class for our flickr contacts. Handles the details of mapping
        e-mail addresses to flickr ids
        
        :param dburl: Database URL to use to connect
        :type dburl: :obj:`str`
        :keyword flickr_proxy: Proxy object to the FlickrAPI
        '''
        
        self.session = db_proxy.get_session()
        self.flickr_proxy = flickr_proxy

    def _add_user(self, **kwargs):
        '''Create and commit a FlickrContact to the database
        
        :params **kwargs: All args feed directly to :obj:`FlickrContact`()
        '''
        
        user = FlickrContact(**kwargs)
        self.session.add(user)
        self.session.commit()

    def sync_flickr(self, google_contacts, force_recheck=False, 
                    flickr_proxy=None):
        '''
        
        :param google_contacts: The contacts that should be synced
        :keyword force_recheck: Flag for if previously checked contacts should be
            rechecked
        :keyword flickr_proxy: Proxy object to the FlickrAPI
        '''
        
        def check_and_add(api_result, ghash, email):
            user = api_result.getchildren()
            if len(user) != 1:
                raise InvalidState('Flickr XML response in unexpected format')
            user = user[0]
            if 'nsid' not in user.attrib:
                raise InvalidState('Flickr XML response in unexpected format')
            username = user.getchildren()[0].text
            db_user = (self.session.query(FlickrContact).
                        filter(FlickrContact.google_hash == ghash))
            if db_user.count() == 0:
                self.LOGGER.info('New link %s <--> %s', email, username)
                db_user = FlickrContact(nsid=user.attrib['nsid'],
                                        username=username,
                                        google_hash=ghash)
                self.session.add(db_user)
                self.session.commit()
                return True
            elif db_user.count() == 1:
                self.LOGGER.info('Updating link %s <--> %s', email, username)
                db_user = db_user.first()
                db_user.nsid = user.attrib['nsid']
                db_user.username = username
                self.session.commit()
                return True
            return False

        if self.flickr_proxy is None and flickr_proxy is None:
            raise InvalidState('Unable to sync_contacts without a flickr_proxy')
        if flickr_proxy is None:
            flickr_proxy = self.flickr_proxy

        for ghash, gcontact in google_contacts.iteritems():
            # If we have checked for this user before, been unable to find
            # and we are not forcing a recheck
            if (not force_recheck and self.session.query(FlickrContact).
                    filter(FlickrContact.google_hash == ghash).
                    filter(FlickrContact.nsid == None).count() 
                > 0):
                self.LOGGER.debug('Skipping check for %s (previously checked '
                                  'and not forcing a recheck)', ghash)
                continue
            # If we already know the nsid skip
            if (self.session.query(FlickrContact).
                    filter(FlickrContact.google_hash == ghash).
                    filter(FlickrContact.nsid != None).count()
                > 0):
                self.LOGGER.debug('%s aleady in database', ghash)
                continue
            # else ask flickr for each e-mail the user has and if we find them
            # store the result
            found = False
            for email in gcontact.emails:
                self.LOGGER.debug('Searching flickr for: %s', email)
                try:
                    result = flickr_proxy.people_findByEmail(find_email=email)
                    if check_and_add(result, ghash, email):
                        found = True
                        break
                except flickrapi.exceptions.FlickrError, err:
                    if err.message != u'Error: 1: User not found':
                        raise
            # Else add ghash to db so we don't recheck them till later
            if not found:
                self.LOGGER.debug('Unable to find a flickr link for %s, marked in db')
                self.session.add(FlickrContact(google_hash=ghash))
                self.session.commit()

class FlickrImageManager(object):
    
    LOGGER = LOGGER.getChild('FlickrImageManager')
    
    def __init__(self, db_proxy, flickr_proxy=None):
        '''Used to manage the actual photo objects that are on flickr v.s. what is
        on the local computer
        
        :param dburl: Database URL to use to connect
        :type dburl: :obj:`str`
        :keyword flickr_proxy: Proxy object to the FlickrAPI
        '''
        
        self._photos = {}
        self.session = db_proxy.get_session()
        self.flickr_proxy = flickr_proxy

    def _get_db_photo(self, image):
        '''Quick way to grab the image out of the database
        
        :param image: Image to grab from the database
        :type image: :obj:`~lib.image.Image`
        '''
        
        query = self.session.query(FlickrImage).\
            filter(FlickrImage.photo_date == image.date_taken).\
            filter(FlickrImage.photo_id != None).\
            filter(FlickrImage.filename == image.filename)
        try:
            return query.one()
        except NoResultFound:
            return None
        
    def _find_unlinked_photos(self):
        '''Find photos in the database that do not have the flickr id associated
        
        This does the search based on all photos that have been added with
        :meth:`add_photo`
        '''
        
        max_date = max(self._photos.keys())
        min_date = min(self._photos.keys())
        query = self.session.query(FlickrImage).\
            filter(FlickrImage.photo_date <= max_date).\
            filter(FlickrImage.photo_date >= min_date).\
            filter(FlickrImage.photo_id != None)
        if query.count() == 0:
            return self._photos
        # Shallow copy since we're just returning a subset
        unlinked = self._photos.copy()
        for photo in query:
            if (photo.photo_date in unlinked and
                photo.filename == unlinked[photo.photo_date].filename):
                del unlinked[photo.photo_date]
        return unlinked
    
    def _find_linked_photos(self):
        '''Inverse of :meth:`_find_unlinked_photos`
        '''
        
        unlinked = self._find_unlinked_photos()
        photos = self._photos.copy()
        if len(unlinked) == 0:
            return photos
        for key in unlinked.iterkeys():
            del photos[key]
        return photos
    
    def _get_flickr(self, flickr_proxy):
        '''Factoring out a multiline boiler plate piece of code
        
        :param flickr_proxy: The flickr proxy passed into the calling func.
        :raises: :exp:`InvalidState` on self.flickr_proxy and flickr_proxy both
            being none.
        '''
        
        if self.flickr_proxy is None and flickr_proxy is None:
            raise InvalidState('Unable to sync_contacts without a flickr_proxy')
        if flickr_proxy is None:
            return self.flickr_proxy
        return flickr_proxy
    
    def add_photo(self, imgs):
        '''Add a single Image instance or a list/tuple of Image to the list of
        images that :obj:`FlickrImageManager` will work on 
        
        :param imgs: single :obj:`~lib.image.Image` instance or a 
            :obj:`list` of :obj:`~lib.image.Image` instances
        '''

        def add_img(img):
            date = img.date_taken
            if date is None:
                raise InvalidState('Photos must have exif data for this '
                                   'program to work (error caused by: %s)' % 
                                   img)
            if date in self._photos:
                raise InvalidState('Two photos should not have the same date '
                                   'taken value')
            self._photos[date] = img
            # link the google_id and the flickr_id if we can
            self.LOGGER.debug('Linking people in img "%s" to flickr ids', img)
            for person in img.people:
                flickr_contact = FlickrContact.google_to_flickr(self.session,
                                                      person.google_id)
                if flickr_contact is not None and person.has_id(FlickrContact.CONTACT_ID) is False:
                    nsid, username = flickr_contact
                    person.add_id(FlickrContact.CONTACT_ID, nsid)
                    person.add_id(FlickrContact.USERNAME, username)
                    
        if isinstance(imgs, Image):
            add_img(imgs)
        elif isinstance(imgs, (list, tuple)):
            for img in imgs:
                if not isinstance(img, Image):
                    raise InvalidState('Expected an instance of Image, got %s' %
                                       type(img))
                add_img(img)
        else:
            raise InvalidState('Expected an instance of Image, got %s' % 
                               type(imgs))

    def link_photos(self, flickr_proxy=None):
        '''Find the corresponding photos in flickr that match this set of photos
        
        For now this is done by matching exactly the EXIF time of the photo, so
        if the user has modified this even slightly it will throw off the 
        matching
        
        :param flickr_proxy: The flickr proxy passed into the calling func.
        '''
        
        def get_photos_element(resp):
            photos = resp.getchildren()
            if len(photos) != 1:
                raise InvalidState('Flickr XML response in unexpected format')
            photos = photos[0]
            for key in ('page', 'pages', 'total'):
                if key not in photos.attrib:
                    raise InvalidState('Flickr XML response in unexpected format')
            return photos
        
        def add_photos(photos):
            '''Add a photo to the database cache
            
            :param photos: image to add to the db
            :type photos: :obj:`~lib.image.Image`
            '''
            
            for photo in photos.getiterator():
                if photo.tag != 'photo':
                    continue
                taken = datetime.datetime.strptime(photo.attrib['datetaken'],
                                                   '%Y-%m-%d %H:%M:%S')
                self.LOGGER.debug('Trying to match: %s', photo.attrib)
                if taken in self._photos:
                    self.LOGGER.debug('Matched to: %s', self._photos[taken])
                    img = FlickrImage(photo_id=photo.attrib['id'], 
                                      photo_secret=photo.attrib['secret'], 
                                      filename=self._photos[taken].filename, 
                                      checksum=self._photos[taken].checksum, 
                                      photo_date=taken, 
                                      flickr_photo_date=taken,
                                      flickr_title=photo.attrib['title'])
                    self.session.add(img)
                    self.session.commit()
        
        def run_search(**kwargs):
            self.LOGGER.debug('photos_search : %s', kwargs)
            resp = flickr_proxy.photos_search(**kwargs)
            photos = get_photos_element(resp)
            add_photos(photos)
            if photos.attrib['pages'] != '1':
                self.LOGGER.info('Flickr image search returned %s pages of '
                                 'results...', photos.attrib['pages'])
            for idx in xrange(2,int(photos.attrib['pages']) + 1):
                resp = flickr_proxy.photos_search(page=idx, **kwargs)
                photos = get_photos_element(resp)
                add_photos(photos)
                
        unlinked = self._find_unlinked_photos()
        if len(unlinked) == 0:
            # Nothing to do!
            return
        max_date = max(unlinked.keys())
        min_date = min(unlinked.keys())
        # Find the list of possible photos
        flickr_proxy = self._get_flickr(flickr_proxy)
        run_search(min_taken_date=min_date,
                   max_taken_date=max_date,
                   user_id='me',
                   extras='date_taken')
    
    def sync_faces(self, flickr_proxy=None):
        '''Sync facial data for the :obj:`~lib.image.Image` objects for which 
        we know the linking information.
        
        .. note:: This does not attempt to generate that linking information.
            That means it's possible to just run the sync form linking 
            information that has been cached in the DB w/o querying flickr.
            
        :param flickr_proxy: The flickr proxy passed into the calling func.
        '''
        
        def get_faces_to_sync(photo, db_image, flickr_proxy):
            # This is a copy of the people list so we can safely modify it here
            photo_peeps = photo.people
            edit_coords = []
            if len(photo_peeps) == 0: 
                return photo_peeps, edit_coords
            resp = flickr_proxy.photos_people_getList(photo_id=db_image.photo_id)
            people = resp.getchildren()[0]
            if people.attrib['total'] == '0':
                return photo.people, edit_coords
            for person in people.getchildren():
                nsid = person.attrib['nsid']
                for idx in xrange(0, len(photo_peeps)):
                    if photo_peeps[idx].get_id(FlickrContact.CONTACT_ID) == nsid:
                        if photo_peeps[idx].has_position and 'x' not in person.attrib:
                            self.LOGGER.debug('Will push bounding box info for %s to "%s"', photo_peeps[idx].get_id(FlickrContact.USERNAME), db_image.flickr_title)
                            edit_coords.append(photo_peeps[idx])
                        self.LOGGER.debug('%s already in photo "%s"', photo_peeps[idx].get_id(FlickrContact.USERNAME), db_image.flickr_title)
                        del photo_peeps[idx]
                        break
            return photo_peeps, edit_coords
        
        def push_faces(func, photo, db_image, people):
            '''Push the facial location data up to flickr
            
            :param func: The flickr api call to make (photos_people_add or 
                photos_people_editCoords)
            :param photo: :obj:`~lib.image.Image` object
            :param db_image: Database instance of the image
            :param people: Collection of 
                :obj:`~lib.image.Image.ContainedPerson` objects to add
            :type people: :obj:`list`
            '''
            
            # Convert facial coords to 500px based image
            ratio = 500.0 / max(photo.width, photo.height) 
            for person in people:
                nsid = person.get_id(FlickrContact.CONTACT_ID)
                username = person.get_id(FlickrContact.USERNAME)
                if nsid is None:
                    continue
                self.LOGGER.debug('Adding %s to photo %s', username, db_image.filename)
                func(photo_id=db_image.photo_id, 
                     user_id=nsid,
                     person_x=person.x_pos * ratio,
                     person_y=person.y_pos * ratio,
                     person_w=person.width * ratio,
                     person_h=person.height * ratio)
        
        flickr_proxy = self._get_flickr(flickr_proxy)
        linked = self._find_linked_photos()
        self.LOGGER.info('Pushing facial location data to flickr')
        for photo in linked.itervalues():
            db_image = self._get_db_photo(photo)
            ppl_to_sync, ppl_to_edit = get_faces_to_sync(photo, db_image, flickr_proxy)
            push_faces(flickr_proxy.photos_people_add, photo, db_image, ppl_to_sync)
            push_faces(flickr_proxy.photos_people_editCoords, photo, db_image, ppl_to_edit)
            
class FlickrAPIManager(object):

    LOGGER = LOGGER.getChild('FlickrAPIManager')

    def __init__(self):
        '''Used as a proxy to the FlickrAPI objects. This is for unit testing the
        rest of the system
        
        :ivar flickr: :obj:`~flickrapi.FlickrAPI` instance that does the heavy
            lifting of actually talking to flickr.
        :ivar logged_in: Boolean for if we're already logged into flickr
        '''
        
        self.flickr = flickrapi.FlickrAPI(APIKEY, APISECRET, cache=True)
        self.logged_in = False

    def login(self):
        '''Setup the :attr:`flickr` object and perform the login to flickr
        
        It is safe to call this function several times. Subsequent calls have no
        effect.
        '''
        
        if self.logged_in:
            return
        (token, frob) = self.flickr.get_token_part_one(perms='write')
        if not token:
            raw_input('Press ENTER after you have authorized this program')
        self.flickr.get_token_part_two((token, frob))
        self.logged_in = True

    def __getattr__(self, name):
        '''Make this class act as a proxy to the :obj:`~flickrapi.FlickrAPI`
        '''
        
        return self.flickr.__getattr__(name)
