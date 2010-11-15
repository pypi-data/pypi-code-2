import datetime
import time
from logging import getLogger
from urllib import unquote
from urlparse import urlparse

from lxml import etree

from django.utils.datastructures import MultiValueDict

from bookreader.models import Book, Page, Annotation, Link
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
        if len(item['issued']) == 20:
            book.issued = datetime.datetime(*time.strptime(item['issued'],
                                                           '%Y-%m-%dT%H:%M:%SZ')[:6])
        elif len(item['issued']) == 10:
            book.issued = datetime.datetime(*time.strptime(item['issued'],
                                                           '%Y-%m-%d')[:6])
    except ValueError:
        pass
    
    if not book.issued:
        book.issued = datetime.datetime.now()
    
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
    Annotation.objects.filter(book=book).delete()
    
    sequence = 1
    
    canonical = metadata.getroot().attrib.get('canonicalHandle', None)
    
    # Handle a canonical version reference
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
                log.debug('Canonical object does not exist for %s' % (str(book.identifier),))
    
    # harvest and save the structural annotation elements
    for annotation in metadata.iterfind('.//structure/annotation'):
        try:     
            #offset
            offset = annotation.get('offset')
            #length
            length = annotation.get('length', 1)
            #structural
            isStructural = annotation.get('isStructural', '').lower() in ('true', 'yes', '1')        
            #text
            text = annotation.text
            #save annotation
            Annotation.objects.create(book=book, offset=offset, length=length, structural=isStructural, text=text)
        except:
            pass
        
        
    # harvest and save the 6 exterior elements
    for exteriorElementName in ('front', 'top', 'bottom', 'spine', 'side', 'back'):
        element = metadata.find('.//exterior/%s' % (exteriorElementName,))
        
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
        
        # Create the page (exterior)
        Page.objects.create(book=book, jp2=jp2, thumbnail=thumbnail,
                            sequence=0, title=exteriorElementName,
                            internal=False)
    
    # harvest the chunk elements (internal pages)
    for chunk in metadata.iterfind('.//chunk'):
        jp2 = chunk.find('handle[@mimetype="image/jp2"]')
        thumbnail = chunk.find('handle[@mimetype="image/jpeg"]')
        
        # handle a possibly missing page
        if chunk.get('missing','').lower() in ('true','yes','1') or jp2 is None:
            Page.objects.create(book=book, sequence=sequence,
                                title=chunk.get('title',None))
            sequence += 1
            try:
                count = int(chunk.get('length',1)) - 1
            except:
                count = 0
            
            for sequence in range(sequence,sequence+count):
                Page.objects.create(book=book, sequence=sequence)
            
            if count > 0:
                sequence += 1
            
            continue # Don't continue processing this chunk
        
        # Set the jp2 to be the text contents
        jp2 = jp2.text
        
        # If the thumbnail handle is found, set the thumbnail to be the text contents
        if thumbnail is not None:
            thumbnail = thumbnail.text
        
        # Set the title to the title attribute of the chunk or None
        title = chunk.get('title',None)
        
        # no title attribute, calculate a title from the jp2 location
        if title is None:
            try:
                title = jp2.rsplit('.',1)[0].rsplit('/',1)[1]
            except:
                title = jp2
        
        # create the page with the calculated values
        Page.objects.create(book=book, sequence=sequence, title=title, jp2=jp2,
                            thumbnail=thumbnail)
        
        sequence += 1
    
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
        
        page.internal = True
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