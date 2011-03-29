from tempfile import TemporaryFile
from urllib import urlencode

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404

try:
    from reportlab.pdfgen.canvas import Canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
    _REPORTLAB = True
except ImportError:
    _REPORTLAB = False

from bookreader.models import Book, Page



def get_djatoka_url(jp2, **extras):
    kwargs = settings.DJATOKA_ARGUMENTS.copy()
    kwargs.update(extras)
    kwargs['rft_id'] = jp2
    return '%s?%s' % (settings.DJATOKA_BASE_URL, urlencode(kwargs, True),)

def add_annotation(canvas, book, annotation, level=0, closed=0):
    try:
        print 'adding annotation: %s at level %d' % (str(annotation),level,)
        canvas.addOutlineEntry(annotation.text, str(annotation.pk),
                               level=level, closed=closed)
        
        for child in annotation.children:
            print 'adding a child: %s' % (str(child),)
            add_annotation(canvas, book, child, level+1, 1)
    except Page.DoesNotExist:
        pass

def add_blank_page_range(canvas, book, start, length):
    if length > 1:
        text = 'Pages %d-%d' % (start, start + length - 1,)
    else:
        text = 'Page %d' % (start,)
    
    for annotation in book.annotations.filter(offset__range=(start, start+length)):
        canvas.bookmarkPage(str(annotation.pk))
    
    canvas.drawCentredString(4.25 * inch, 5.5*inch, text)
    canvas.showPage()
    

def compiled(request, object_id, size=None):
    book = get_object_or_404(Book, pk=object_id)
    
    if size is None:
        size = request.REQUEST.get('size',None)
    limit = request.REQUEST.get('limit',None)
    
    if limit:
        limit = int(limit)
    
    tempfile = TemporaryFile()
    
    canvas = Canvas(tempfile, pagesize=letter)
    canvas.setAuthor(book.creator)
    canvas.setTitle(book.title)
    
    imageArgs = {'x': 0, 'y': 0, 'height': letter[1], 'width': letter[0],
                 'preserveAspectRatio': True, 'anchor': 'c'}   
    
    djatokaArgs = {'svc.scale':'612,792'}
    
    if size == 'mobile':
        djatokaArgs['svc.scale'] = '425,550'
    elif size == 'small':
        djatokaArgs['svc.scale'] = '612,792'
    elif size == 'medium':
        djatokaArgs['svc.scale'] = '2550,3300'
    elif size == 'large':
        djatokaArgs['svc.scale'] = '5100,6600'
    elif size == 'original':
        djatokaArgs['svc.scale'] = '1.000'
    elif size != None:
        djatokaArgs['svc.scale'] = size
    
    try:
        page = book.pages.get(internal=False,title='front',jp2__isnull=False)
        canvas.drawImage(get_djatoka_url(page.jp2, **djatokaArgs), **imageArgs)
        canvas.showPage()
    except Page.DoesNotExist:
        pass
    
    pages = book.pages.filter(internal=True).order_by('sequence')
    
    if limit and len(pages) > limit:
        pages = pages[:limit]
    
    start = None
    length = 1
    
    for page in pages:
        if page.jp2:
            if start is not None:
                add_blank_page_range(canvas, book, start, length)
                start = None
            
            canvas.drawImage(get_djatoka_url(page.jp2, **djatokaArgs),
                             **imageArgs)
            
            for annotation in book.annotations.filter(offset=page.sequence):
                canvas.bookmarkPage(str(annotation.pk))
            canvas.showPage()
        else:
            if start is None:
                start = page.sequence
                length = 1
            else:
                length += 1
    
    if start is not None:
        add_blank_page_range(canvas, book, start, length)
    
    if limit:
        for annotation in book.annotations.filter(offset__gt=limit):
            canvas.bookmarkPage(str(annotation.pk))
    
    for external in ('back', 'top', 'bottom', 'side', 'spine', ):
        try:
            page = book.pages.get(internal=False,
                                  title=external,jp2__isnull=False)
            canvas.drawImage(get_djatoka_url(page.jp2, **djatokaArgs),
                             **imageArgs)
            canvas.showPage()
        except Page.DoesNotExist:
            pass
    
    for annotation in book.top_level_structure:
        add_annotation(canvas, book, annotation)
    
    canvas.save()
    
    tempfile.seek(0)
    
    return HttpResponse(tempfile.readlines(), mimetype='application/pdf')
    

if not _REPORTLAB:
    def compiled(request, *args, **kwargs):
        """ Return a bad request response when reportlab is not installed """
        return HttpResponseBadRequest(u'reportlab must be installed compile '
                                      'PDF documents')
