import datetime
import time
from logging import getLogger
from urllib import unquote
from urlparse import urlparse

from lxml import etree

from django.utils.datastructures import MultiValueDict

from bookreader.models import Book, Page, Link
from bookreader.harvesting.metadata import metadata_registry



log = getLogger('bookreader.harvesting.book')

etree.set_default_parser(etree.XMLParser(dtd_validation=False, load_dtd=False,
                                         no_network=False))

def load_metadata(book, **kwargs):
    kw = {}
    kwargs.setdefault('metadataPrefix', 'dim')
    
    if 'metadata_registry' in kwargs:
        kw['metadata_registry'] = kwargs.pop('metadata_registry')
    else:
        kw['metadata_registry'] = metadata_registry
    
    repo = book.collection.repository.connection(**kw)

    header, item, other = repo.getItem(identifier=book.identifier, **kwargs)
    
    book.title = item['title']
    book.creator = ', '.join(item['creator'])
    book.created = item['created']
    if item['thumbnail']:
        book.thumbnail = item['thumbnail']
    
    
    book.additional_metadata = MultiValueDict()
    
    if item['title.alternative']:
        book.additional_metadata.setlist('alternate title',map(lambda v: v.strip(), item['title.alternative']))
    
    if item['description']:
        book.additional_metadata.setlist('description',map(lambda v: v.strip(), item['description']))
    
    if item['contributor']:
        book.additional_metadata.setlist('contributor',map(lambda v: v.strip(), item['contributor']))
    
    if item['subject']:
        book.additional_metadata.setlist('subject',map(lambda v: v.strip(), item['subject']))
    
    if item['subject.other']:
        book.additional_metadata.setlist('other subject',map(lambda v: v.strip(), item['subject.other']))
    
    if item['publisher']:
        book.additional_metadata.setlist('publisher',map(lambda v: v.strip(), item['publisher']))
    
    if item['offset']:
        book.additional_metadata.setlist('offset',map(lambda v: v.strip(), item['offset']))
    
    try:
        book.issued = datetime.datetime(*time.strptime(item['issued'],
                                                       '%Y-%m-%dT%H:%M:%SZ')[:6])
    except ValueError:
        book.issued = None
    
    return True

def load_bitstream_bundles(book, **kwargs):
    """ Load item bitstreams from the OAI-PMH view of a DSPace repository using
    the 'ore' metadata format. Bundle information is contained in oreatom:triples
    and the rest of the bitstream metadata is in atom:links. """
    kw = {}
    kwargs.setdefault('metadataPrefix', 'ore')
    
    if 'metadata_registry' in kwargs:
        kw['metadata_registry'] = kwargs.pop('metadata_registry')
    else:
        kw['metadata_registry'] = metadata_registry
    
    repo = book.collection.repository.connection(**kw)
    header, item, other = repo.getItem(identifier=book.identifier, **kwargs)
    
    descriptions = {}
    bundles = {}
    
    for triple in item['triples']:
        descriptions[triple['about']] = triple['bundle']
        
    for bitstream in item['bitstreams']:
        bundle = descriptions.get(bitstream['url'], 'UNKOWN')
        bitstream.getMap()['bundle'] = bundle
        bundles.setdefault(bundle, []).append(bitstream)
    
    return bundles

def load_detailed_pages(book, metadata):
    log.debug('load_detailed_pages(%s, %s)' % (str(book), str(metadata),))
    
    Page.objects.filter(book=book).delete()
    
    sequence = 1
    
    canonical = metadata.getroot().attrib.get('canonical', None)
    
    if canonical and canonical != book.repository_url:
        canonical = urlparse(canonical)
        path = canonical.path
        
        if path.startswith('/handle/'):
            path = path[8:]
        
        canonical = 'oai:%s:%s' % (canonical.hostname,
                                   path)
        
        if canonical != book.identifier:
            try:
                canonical = Book.objects.get(identifier=canonical)
                if book.canonical != canonical:
                    book.canonical = canonical
                    book.save()
            except Book.DoesNotExist:
                log.error('Canonical object does not exist for %s' % (str(book.identifier),))
    
    for chunk in metadata.iterfind('.//chunk'):
        jp2 = chunk.find('handle[@mimetype="image/jp2"]')
        thumbnail = chunk.find('handle[@mimetype="image/jpeg"]')
        
        attrib = dict(chunk.attrib)
        
        if jp2 is not None:
            page = Page(book=book, jp2=jp2.text)
        else:
            page = Page(book=book)

        if thumbnail is not None:
            page.thumbnail = thumbnail.text
        
        page.sequence = sequence
        sequence += 1
        
        if attrib.get('type') == 'exterior' and attrib.get('view'):
            attrib.setdefault('title', attrib['view'])
        
        if attrib.get('missing','false').lower() in ('true','yes','1') or page.jp2 is None:
            page.jp2 = None
            page.title = attrib.get('title',None)
            page.save()
            
            try:
                count = int(attrib.get('length',1))
            except:
                count = 1
            
            for missing in range(1,count):
                page = Page(book=book, sequence=sequence)
                page.save()
                sequence += 1
            
            continue
        
        try:
            attrib.setdefault('title', page.jp2.rsplit('.',1)[0].rsplit('/',1)[1])
        except:
            attrib.setdefault('title', page.jp2)
        
        page.title = attrib['title']
        page.save()
    
    return (book.pages.count(),0)
    

def load_pages(book, **kwargs):
    """ Grab all jp2 files in the 'ORIGINAL' bitstream bundle. Also try to 
    parse thumbnail information from the 'THUMBNAIL' bundle and use filename 
    matching """
    log.debug('load_pages(%s, **%s)' % (str(book), str(kwargs),))
    created = 0
    updated = 0
    
    parser = kwargs.pop('parser', etree.parse)
    bundles = load_bitstream_bundles(book, **kwargs)
    
    metadata = filter(lambda b: b['url'].rsplit('?',1)[0].endswith('bitstream_metadata.xml'),
                      bundles.get('METADATA',[]))
    
    if len(metadata) > 0:
        try:
            return load_detailed_pages(book, parser(metadata[0]['url']))
        except IOError:
            log.debug('Error opening detailed page metadata file: %s' % (metadata[0]['url'],))
        except:
            log.exception('Error loading detailed page metadata file')
    
    pages = filter(lambda b: b['mimetype'] == 'image/jp2', bundles.get('ORIGINAL',[]))
    pages.sort(key=lambda p: p['url'].rsplit('.',1)[0].rsplit('_',1)[1])
    
    thumbnails = dict(map(lambda t: (t['url'].rsplit('.',1)[0].rsplit('%2f',1)[-1],
                                     t['url'],),
                          filter(lambda t: t['url'].find('.jpg') != -1,
                                 bundles.get('THUMBNAIL',[]))))
    
    sequence = 1
    
    for page in pages:
        title = page['title'].rsplit('.',1)[0]
        thumbnail = thumbnails.get(page['url'].rsplit('.',1)[0].rsplit('/',1)[-1],
                                   None)
        try:
            page = book.pages.get(jp2=page['url'])
        except Page.DoesNotExist:
            page = Page(book=book, jp2=page['url'])
            created += 1
        else:
            updated += 1
        
        if thumbnail:
            page.thumbnail = unquote(thumbnail)
        
        page.title = title
        page.sequence = sequence
        sequence += 1
        page.save()
    
    return (created, updated,)

def load_links(book, excluded_mimetypes=('image/jp2','image/jpeg',),
               bundles=('ORIGINAL',), **kwargs):
    created = 0
    updated = 0
    
    loaded_bundles = load_bitstream_bundles(book, **kwargs)
    links = []
    
    for b in bundles:
        links.extend(filter(lambda b: b['mimetype'] not in excluded_mimetypes,
                            loaded_bundles.get(b,[])))
    
    for h_link in links:
        try:
            link = book.links.get(url=h_link['url'])
        except Link.DoesNotExist:
            link = Link(book=book, url=h_link['url'])
            created += 1
        else:
            updated += 1
        
        link.title = h_link['title'].split('.')[0]
        link.mimetype = h_link['mimetype']
        link.size = h_link['size']
        link.bundle = h_link['bundle']
        link.save()
    
    return (created, updated,)