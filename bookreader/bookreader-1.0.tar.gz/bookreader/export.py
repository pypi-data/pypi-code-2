from lxml import etree

from bookreader.models import Page



_exterior_views = ('front','top','bottom','spine','side','back',)

def bitstream_metadata(book):
    root = etree.Element('book')
    if book.canonical and book.canonical.published:
        root.set('canonicalHandle',book.canonical.repository_url)
    
    if book.work and book.work.published:
        root.set('workHandle', book.work.repository_url)
    
    root.set('type', book.type)
    
    root.set('length', str(book.pages.filter(internal=True).count()))
    structure = etree.SubElement(root,'structure')
    exterior = etree.SubElement(root,'exterior')
    interior = etree.SubElement(root,'interior')
    
    if book.type == 'work':
        return etree.tostring(root, pretty_print=True, encoding=unicode)
    
    for annotation in book.annotations.order_by('offset'):
        #offset, length, structural, text
        annotationElem = etree.Element('annotation',
                                       {'offset': str(annotation.offset),
                                        'length': str(annotation.length),
                                        'isStructural': str(annotation.structural)})
        annotationElem.text = annotation.text
        structure.append(annotationElem)
    
    for view in _exterior_views:
        try:
            page = book.pages.get(title=view)
        except Page.DoesNotExist:
            page = None
        
        e = etree.SubElement(exterior,view)
        
        if not page or not page.jp2:
            e.set('missing','true')
            continue
        
        e.extend(create_handles(page))
    
    missing = 0
    
    for page in book.pages.exclude(title__in=_exterior_views).order_by('sequence'):
        if not page.jp2 and not page.title:
            missing += 1
            continue
        
        if missing > 0:
            interior.append(etree.Element('chunk',
                                          {'missing': 'true',
                                           'length': str(missing),}))
            missing = 0
        
        if not page.jp2:
            interior.append(etree.Element('chunk',
                                          {'missing': 'true',
                                           'title': page.title}))
        else:
            e = etree.SubElement(interior,'chunk')
            if page.title:
                e.set('title',page.title)
            e.extend(create_handles(page))
    
    if missing > 0:
        interior.append(etree.Element('chunk',
                                      {'missing': 'true',
                                       'length': str(missing),}))
    
    return etree.tostring(root, pretty_print=True, encoding=unicode)

def create_handles(page):
    h = [etree.Element('handle', {'mimetype':'image/jp2'})]
    h[0].text = page.jp2
    
    if page.thumbnail:
        h.append(etree.Element('handle',
                               {'mimetype':'image/jpeg','type':'thumbnail'}))
        h[1].text = page.thumbnail
    
    return h
