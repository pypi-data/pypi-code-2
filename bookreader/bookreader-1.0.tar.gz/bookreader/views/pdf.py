from tempfile import TemporaryFile
from urllib import urlencode
from django.core.mail import send_mail
from django.core.mail import mail_admins
from django.core.files import File

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.template import loader, RequestContext
from django.views.generic import list_detail, simple

import os
import threading
import urllib
import json
import logging

try:
    from reportlab.pdfgen.canvas import Canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
    _REPORTLAB = True
except ImportError:
    _REPORTLAB = False

from bookreader.models import Book, Page

from django.contrib.auth.models import User
from django.contrib.sessions.models import Session


logger = logging.getLogger(__name__)


def get_djatoka_url(jp2, **extras):
    kwargs = settings.DJATOKA_ARGUMENTS.copy()
    kwargs.update(extras)
    kwargs['rft_id'] = jp2
    return '%s?%s' % (settings.DJATOKA_BASE_URL, urlencode(kwargs, True),)


def get_djatoka_metadata(jp2):
    kwargs = {'url_ver':'Z39.88-2004',
              'svc_id':'info:lanl-repo/svc/getMetadata',
              'svc_val_fmt':'info:ofi/fmt:kev:mtx:jpeg2000'}
    kwargs['rft_id'] = jp2
    
    return json.loads(urllib.urlopen(settings.DJATOKA_BASE_URL + '?' + urlencode(kwargs, True)).read())


def set_image_params(jp2, djatokaArgs, imageArgs, size):
    # Step 1: Get image metadata for the real image height and width (in pixels)
    metadata = get_djatoka_metadata(jp2)
    height = int(metadata['height'])
    width = int(metadata['width'])
    
    # Step 2: Figure out the new pixel height and width via multiplying by the scaling factor (assume 400ppi)
    # DPI's, in order: 50, 72, 300, 600, orig
    
    dummy_dict = djatokaArgs.copy()
        
    if size == 'mobile':
        dummy_dict['svc.scale'] = str(width*50/400) + ',' + str(height*50/400)
    elif size == 'small':
        dummy_dict['svc.scale'] = str(width*72/400) + ',' + str(height*72/400)
    elif size == 'medium':
        dummy_dict['svc.scale'] = str(width*300/400) + ',' + str(height*300/400)
    elif size == 'original':
        dummy_dict['svc.scale'] = '1.000'
    elif size != None:
        dummy_dict['svc.scale'] = size
        
    djatokaArgs.update(dummy_dict)
    
    dummy_dict = imageArgs.copy()
    dummy_dict = {'x': 0, 'y': 0, 'height': int(djatokaArgs['svc.scale'].split(',')[1]), 'width': int(djatokaArgs['svc.scale'].split(',')[0]),
                 'preserveAspectRatio': False, 'anchor': 'c'}
    imageArgs.update(dummy_dict)
    
    
    

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
    
    
def landing_page(request, object_id, **kwargs):
    kwargs.setdefault('template_object_name','book')
    kwargs.setdefault('template_name', 'bookreader/compiled_pdfs.html')
    kwargs.setdefault('queryset', Book.objects.all())
    kwargs['object_id'] = object_id
    
    return list_detail.object_detail(request, **kwargs)
    
    '''    
    t = kwargs['template_loader'].get_template(kwargs['template_name'])
    return HttpResponse(t.render(c), mimetype=kwargs['mimetype'])
    '''
    

def handle_request(request, object_id, size=None):

    book = get_object_or_404(Book, pk=object_id)
    
    if size is None:
        size = request.REQUEST.get('size',None)
    
    handle_number = book.identifier.split(':')[2].replace('/', '_')
    file_name_complete = settings.MEDIA_ROOT + '/' + handle_number + '_' + size + '.pdf'
    file_name_inprogress = settings.MEDIA_ROOT + '/' + handle_number + '_' + size

    if os.path.exists(file_name_complete):
        #logger.error("found complete PDF")
        PDF_file = open(file_name_complete, 'r')
        return HttpResponse(File(PDF_file).readlines(), mimetype='application/pdf')
    elif os.path.exists(file_name_inprogress):
        #logger.error("found PDF in progress")
        tempfile = TemporaryFile()
        tempfile.write('PDF compilation in progress, please check back later...')
        tempfile.seek(0);
        return HttpResponse(tempfile.readlines(), mimetype='text/plain')
    else:
        # Fire the missiles
        #logger.error("generating fresh PDF")
        f = open(file_name_inprogress, 'w')
        PDF_file = File(f)
        t = threading.Thread(target=compile_PDF,
                             args=[request, book, PDF_file, size])
        t.setDaemon(True)
        t.start()
        tempfile = TemporaryFile()
        tempfile.write('PDF compilation initiated, please check back later...')
        tempfile.seek(0);
        return HttpResponse(tempfile.readlines(), mimetype='text/plain')
    


def compile_PDF(request, book, PDF_file, size=None):
    
    print "The selected size pre is:"
    print size
    
    if size is None:
        size = request.REQUEST.get('size',None)
        
    limit = request.REQUEST.get('limit',None)
    if limit:
        limit = int(limit)
        
    print "The selected size post is:"
    print size
        
    canvas = Canvas(PDF_file, pagesize=letter)
    canvas.setAuthor(book.creator)
    canvas.setTitle(book.title)
    
    djatokaArgs = {'svc.scale':'612,792'}
    imageArgs = {'x': 0, 'y': 0, 'height': letter[1], 'width': letter[0],
                 'preserveAspectRatio': False, 'anchor': 'c'}
    
    try:
        page = book.pages.get(internal=False,title='front',jp2__isnull=False)
        set_image_params(page.jp2, djatokaArgs, imageArgs, size)
        
        canvas.drawImage(get_djatoka_url(page.jp2, **djatokaArgs), **imageArgs)
        canvas.showPage()
    except Page.DoesNotExist:
        pass
    
    pages = book.pages.filter(internal=True).order_by('sequence')
    
    if limit and len(pages) > limit:
        pages = pages[:limit]
    
    start = None
    length = 1
    
    count = 0
    
    for page in pages:
        if page.jp2:
            if start is not None:
                add_blank_page_range(canvas, book, start, length)
                start = None
            '''
            print "In pdf.py, here are the djatokaArgs:"
            for x in djatokaArgs.items():
                print x
            print "In pdf.py, here are the imageArgs:"
            for x in imageArgs.items():
                print x
            ''' 
            count += 1
            print count
            '''print page.jp2
            print get_djatoka_url(page.jp2, **djatokaArgs)
            metadata = get_djatoka_metadata(page.jp2)
            height = int(metadata['height'])
            width = int(metadata['width'])'''
            
            set_image_params(page.jp2, djatokaArgs, imageArgs, size)
            
            #height_prime = int(djatokaArgs['svc.scale'].split(',')[1])
            
            print "width:height prime is:"
            print imageArgs['width']
            print imageArgs['height']
            
            #imageArgs['width'] = int((width * height_prime) / height)
            #imageArgs['height'] = height_prime
            
            canvas.setPageSize((imageArgs['width'], imageArgs['height']))
                
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
    
    PDF_file.seek(0)
    
    # Once completed send out the completion emails
    # Rename file to .pdf
    
    os.rename(PDF_file.name, PDF_file.name + ".pdf")
    
    uid = request.session.get('_auth_user_id')
    if uid is not None:
        user = User.objects.get(pk=uid)
        print user.username, user.get_full_name(), user.email
        send_mail('PDF Compilation completed', 'Dear ' + user.get_full_name() + ',\n\nYour PDF has been completed and is now available here: \n\n' + 
                  request.build_absolute_uri(), 'system@libros.dev', [user.email], fail_silently=True)
    
    
    
'''
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
    
    #send_mail('Test Subject', 'You are getting test messaged', 'system@libros.dev', ['alexey@library.tamu.edu'], fail_silently=False)
    
    print "here are some items"
    print request.session.items();
    
    uid = request.session.get('_auth_user_id')
    user = User.objects.get(pk=uid)
    
    print user.username, user.get_full_name(), user.email
    
    print "book thing"
    print book.identifier
    handle_number = book.identifier.split(':')[2].replace('/', '_')
    print handle_number
    
    
    f = open('var/media/' + handle_number + '.pdf', 'w')
    PDFFile = File(f)
    
    print "here is a fake file"
    print os.path.exists('blah')
    
    print "here is a real file"
    print os.path.exists('var/media/' + handle_number + '.pdf')
    
    
    ''
    for page in pages:
        if page.jp2:
            if start is not None:
                add_blank_page_range(canvas, book, start, length)
                start = None
            
            print "In pdf.py, here are the djatokaArgs:"
            for x in djatokaArgs.items():
                print x
            print "In pdf.py, here are the imageArgs:"
            for x in imageArgs.items():
                print x
                
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
    
    ''
    
    canvas.save()
    
    tempfile.seek(0)
    
    return HttpResponse(tempfile.readlines(), mimetype='application/pdf')
''' 

if not _REPORTLAB:
    def compiled(request, *args, **kwargs):
        """ Return a bad request response when reportlab is not installed """
        return HttpResponseBadRequest(u'reportlab must be installed compile '
                                      'PDF documents')
