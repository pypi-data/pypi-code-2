from datetime import datetime
from time import strptime
from logging import getLogger
from urllib import unquote
from urllib2 import urlopen
from urlparse import urlparse

from lxml import etree

from oaipmh.metadata import MetadataRegistry

from django.utils.datastructures import MultiValueDict

from bookreader.models import Book, Page, Annotation, Link
from bookreader.harvesting.metadata import metadata_registry



log = getLogger('bookreader.harvesting.book')

etree.set_default_parser(etree.XMLParser(dtd_validation=False, load_dtd=False,
                                         no_network=False))

class BookHarvester(object):
    def __init__(self, book, metadata_registry=metadata_registry, bundle_prefix='ore'):
        assert isinstance(book, Book)
        assert isinstance(metadata_registry, MetadataRegistry)
        
        self.book = book
        self.repository = book.collection.repository.connection(metadata_registry=metadata_registry)
        self._bundle_prefix = bundle_prefix
    
    def _set_additional_metadata(self, field, value):
        """ If a value does not equate to false, set the field in the 
        additional_metadata multi-valued dictionary"""
        if not value:
            return
        self.book.additional_metadata.setlist(field, map(lambda v: isinstance(v, basestring) and v.strip() or v,
                                                         value))
    
    def _set_reference_handle(self, field, handle):
        if not handle:
            setattr(self.book, field, None)
            return True
            
        if handle == self.book.repository_url:
            raise ValueError('Invalid handle supplied for %s on %s, circular '
                             'references not allowed' % 
                             (field, str(self.book.identifier),))
        
        handle = urlparse(handle)
        path = handle.path
    
        if path.startswith('/handle/'):
            path = path[8:]
    
        handle = 'oai:%s:%s' % (handle.hostname, path)
        
        if handle == self.book.identifier:
            raise ValueError('Invalid handle supplied for %s on %s, circular '
                             'references not allowed' % 
                             (field, str(self.book.identifier),))
        
        try:
            reference = Book.objects.get(identifier=handle)
        except Book.DoesNotExist:
            raise ValueError('Referenced book, %s, does not exist to be '
                             'referenced by %s on %s' % 
                             (str(handle), field, str(self.book.identifier),))
        
        if getattr(self.book, field) != reference:
            setattr(self.book, field, reference)
            return True
        
        return False
    
    def update_metadata(self, metadataPrefix='dim'):
        """ Load the book metadata from the repository and store it in the 
        appropriate fields in the Book Model """
        book = self.book
        item = self.repository.getItem(identifier=book.identifier,
                                       metadataPrefix=metadataPrefix)[1]
        
        book.title = item['title']
        book.creator = ', '.join(item['creator'])
        book.created = item['created']
        if item['thumbnail']:
            book.thumbnail = item['thumbnail']
        
        book.additional_metadata = MultiValueDict()
        
        self._set_additional_metadata('alternate title', item['title.alternative'])
        self._set_additional_metadata('description', item['description'])
        self._set_additional_metadata('contributor', item['contributor'])
        self._set_additional_metadata('subject', item['subject'])
        self._set_additional_metadata('other subject', item['subject.other'])
        self._set_additional_metadata('publisher', item['publisher'])
        
        try:
            if len(item['issued']) == 20:
                book.issued = datetime(*strptime(item['issued'],
                                                 '%Y-%m-%dT%H:%M:%SZ')[:6])
            elif len(item['issued']) == 10:
                book.issued = datetime(*strptime(item['issued'],
                                                 '%Y-%m-%d')[:6])
        except ValueError:
            pass
        
        if not book.issued:
            book.issued = datetime.datetime.now()
        
        return True
    
    @property
    def bundles(self):
        """ Get the item bitstream bundles with default values """
        if not hasattr(self, '_bundles'):
            self._bundles = self.get_bundles()
        
        return self._bundles
    
    def get_bundles(self, **kwargs):
        """ Load item bitstreams from the OAI-PMH view of a DSPace repository 
        using the 'ore' metadata format. Bundle information is contained in 
        oreatom:triples and the rest of the bitstream metadata is in
        atom:links. """
        kwargs.setdefault('metadataPrefix', self._bundle_prefix)
        item = self.repository.getItem(identifier=self.book.identifier,
                                       **kwargs)[1]
        
        descriptions = {}
        bundles = {}
        
        for triple in item['triples']:
            descriptions[triple['about']] = triple['bundle']
            
        for bitstream in item['bitstreams']:
            bundle = descriptions.get(bitstream['url'], 'UNKOWN')
            bitstream.getMap()['bundle'] = bundle
            bundles.setdefault(bundle, []).append(bitstream)
        
        return bundles
    
    def create_pages(self):
        """ Grab all JPEG2000 files in the 'ORIGINAL' bitstream bundle. Also 
        try to parse thumbnail information from the 'THUMBNAIL' bundle and use 
        filename matching. If the pages do not exist, create them; otherwise, 
        do not make any modifications. """
        created = 0
        
        pages = filter(lambda b: b['mimetype'] == 'image/jp2',
                       self.bundles.get('ORIGINAL',[]))
        
        pages.sort(key=lambda p: p['url'].rsplit('.',1)[0].rsplit('_',1)[1])
        
        thumbnails = dict(map(lambda t: (t['url'].rsplit('.',1)[0].rsplit('%2f',1)[-1],
                                         t['url'],),
                              filter(lambda t: t['url'].find('.jpg') != -1,
                                     self.bundles.get('THUMBNAIL',[]))))
        
        for page in pages:
            try:
                self.book.pages.get(jp2=page['url'])
                continue
            except Page.DoesNotExist:
                pass
            
            created += 1
            thumbnail = thumbnails.get(page['url'].rsplit('.',1)[0].rsplit('/',1)[-1],
                                       None)
            if thumbnail:
                thumbnail = unquote(thumbnail)
            
            Page.objects.create(book=self.book, jp2=page['url'],
                                thumbnail=thumbnail, internal=True,
                                title=page['title'].rsplit('.',1)[0])
        
        return created
    
    def update_structure(self, parser=etree.parse):
        """ Update structure from the bitstream metadata bitstream """
        log.info('Updating structure of %s' % (str(self.book.identifier),))
        metadata = filter(lambda b: b['url'].rsplit('?',1)[0].endswith('bitstream_metadata.xml'),
                          self.bundles.get('METADATA',[]))
        
        if len(metadata) == 0:
            log.error('No bitstream metadata bitstream located for %s' % (str(self.book.identifier),))
            return
        
        if len(metadata) > 1:
            log.error('Too many bitstream metadata bitstreams located for %s, %d' % (str(self.book.identifier),len(metadata),))
            return
        
        try:
            # maybe should only use urlopen when encountering https (to ignore cert errors)
            document = parser(urlopen(metadata[0]['url']))
        except IOError:
            log.exception('Error opening the bitstream metadata bitstream, %s, for %s' % (metadata[0]['url'],
                                                                                          str(self.book.identifier),))
            return
        except:
            log.exception('Error loading bitstream metadata bitstream, %s, for %s' % (metadata[0]['url'],
                                                                                      str(self.book.identifier),))
            return
        
        root = document.getroot()
        
        if 'canonicalHandle' in root.keys():
            try:
                self._set_reference_handle('canonical',
                                           root.get('canonicalHandle', None))
            except Exception, e:
                log.error(str(e))
        
        if 'workHandle' in root.keys():
            try:
                self._set_reference_handle('work',root.get('workHandle', None))
            except Exception, e:
                log.error(str(e))
        
        type = root.get('type','extant').lower()
        
        # Set the book type
        if type in ('canonical','work','frankenbook','extant'):
            self.book.type = type
            self.book.save()
        else:
            log.error('Invalid book type for %s (%s)' % (str(self.book.identifier), str(type),))    
        
        if not self.book.type == 'work':        
            self.create_annotations(document)
        
        if not self.book.type in ('work','canonical',):
            self.update_exterior(document)
        
        if not self.book.type == 'work':
            self.update_interior(document)
    
    
    def update_exterior(self, document):
        for tag in ('front', 'top', 'bottom', 'spine', 'side', 'back'):
            try:
                element = document.find('.//exterior/%s' % (tag,))
                
                # If the element doesn't exist, set jp2 and thumbnail to None
                if element is None or element.get('missing', '').lower() in ('true', 'yes', '1'):
                    jp2 = None
                    thumbnail = None
                # Attempt to extract the jp2 and thumbnail handles
                else:
                    jp2 = element.find('handle[@mimetype="image/jp2"]')        
                    thumbnail = element.find('handle[@mimetype="image/jpeg"]')
                    
                    # If the jp2 handle is found, set the jp2 to be the text contents
                    if jp2 is not None:
                        jp2 = jp2.text
                    
                    # If the thumbnail handle is found, set the thumbnail to be the text contents
                    if thumbnail is not None:
                        thumbnail = thumbnail.text
                
                page = Page.objects.get_or_create(book=self.book, title=tag,
                                                  internal=False)[0]
                
                page.jp2 = jp2
                page.thumbnail = thumbnail
                page.sequence = 0
                page.save()
            except:
                log.exception('Error updating/creating the exterior view, %s, for %s' % (tag, str(self.book.identifier),))
    
    def update_interior(self, document):
        sequence = 1
        
        log.info('Removing all missing pages from %s' % (str(self.book.identifier),))
        self.book.pages.filter(internal=True, jp2__isnull=True).delete()
        
        log.info('Resetting all page sequence numbers on %s' % (str(self.book.identifier),))
        # In the future, move all pages to 'extra' bucket as well
        self.book.pages.filter(internal=True).update(sequence=99999)
        
        for chunk in document.iterfind('.//chunk'):
            try:
                jp2 = chunk.find('handle[@mimetype="image/jp2"]')
                thumbnail = chunk.find('handle[@mimetype="image/jpeg"]')
                
                # handle a missing page
                if chunk.get('missing','').lower() in ('true','yes','1') or jp2 is None:
                    Page.objects.create(book=self.book, sequence=sequence,
                                        title=chunk.get('title',None))
                    sequence += 1
                    try:
                        count = int(chunk.get('length',1)) - 1
                    except:
                        count = 0
                    
                    for sequence in range(sequence, sequence+count):
                        Page.objects.create(book=self.book, sequence=sequence)
                    
                    if count > 0:
                        sequence += 1
                    
                    continue # Don't continue processing this chunk
                
                # Set the jp2 to be the text contents
                jp2 = jp2.text
                
                # Set the title to the title attribute of the chunk or None
                title = chunk.get('title',None)
                
                page = Page.objects.get_or_create(book=self.book,
                                                  jp2=jp2)[0]
                
                # no title attribute, calculate a title from the jp2 location
                if title is None and not page.title:
                    try:
                        page.title = jp2.rsplit('.',1)[0].rsplit('/',1)[1]
                    except:
                        page.title = jp2
                else:
                    page.title = title
                
                page.sequence = sequence
                
                if thumbnail is not None:
                    page.thumbnail = thumbnail.text
                
                page.save()
            except:
                log.exception('Error updating/creating interior page #%d' % (sequence,))
            
            sequence += 1
    
    def create_annotations(self, document):
        """ Re-create all annotations from bitstream metadata bitstream """
        log.info('Create annotations from the bitstream metadata bitstream')
        
        log.info('Removing %d annotations from %s' % (self.book.annotations.count(),
                                                      str(self.book.identifier),))
        
        Annotation.objects.filter(book=self.book).delete()
        
        try:
            # Harvest and save the structural annotation elements
            for annotation in document.iterfind('.//structure/annotation'):
                try:
                    Annotation.objects.create(book=self.book,
                                              offset=annotation.get('offset'),
                                              length=annotation.get('length', 1),
                                              structural=annotation.get('isStructural', '').lower() in ('true', 'yes', '1'),
                                              text=annotation.text)
                except Exception:
                    log.exception('Error creating an annotation for %s' % (str(self.book.identifier),))
        except:
            log.exception('Error iterating over annotations for %s' % (str(self.book.identifier),))
        
        log.info('Created %d annotations for %s' % (self.book.annotations.count(),
                                                    str(self.book.identifier),))
    
    def create_links(self, excluded_mimetypes=('image/jp2','image/jpeg',),
                     bundles=('ORIGINAL',)):
        log.info('Creating links for %s' % (str(self.book.identifier),))
        links = []
        
        for bundle in bundles:
            links.extend(filter(lambda b: b['mimetype'] not in excluded_mimetypes,
                                self.bundles.get(bundle,[])))
        
        for bitstream in links:
            try:
                link = self.book.links.get(url=bitstream['url'])
                log.info('Creating a new link, %s, for %s' % (bitstream['url'],
                                                              str(self.book.identifier),))
            except Link.DoesNotExist:
                link = Link(book=self.book, url=bitstream['url'])
                log.info('Updating a link, %s, for %s' % (bitstream['url'],
                                                          str(self.book.identifier),))
            
            link.title = bitstream['title'].split('.')[0]
            link.mimetype = bitstream['mimetype']
            link.size = bitstream['size']
            link.bundle = bitstream['bundle']
            link.save()
