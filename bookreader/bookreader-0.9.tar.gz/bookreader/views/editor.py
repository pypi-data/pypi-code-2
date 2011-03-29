from logging import getLogger
from urlparse import urlparse

try:
    from uuid import uuid4
except ImportError:
    uuid4 = None
    from random import randint

from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse
from django.db.models import Max
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.simplejson import dumps
from django.views.decorators.csrf import csrf_exempt

from dspace.sword.item import SwordItem

from bookreader.forms import PageForm, ReferenceForm, AnnotationForm, BookForm
from bookreader.models import Collection, Book, Page, Annotation
from bookreader.views.book import view as book_view
from bookreader.export import bitstream_metadata


log = getLogger('bookreader.views.editor')

def generate_random_identifier():
    if uuid4 is not None:
        return '%s:%s:0000' % (str(uuid4()).replace('-',''), 
                               str(uuid4()).replace('-',''),)
    else:
        return '%08d:%08d:%04d' % (randint(0, 99999999),
                                   randint(0, 99999999),
                                   randint(0, 9999),)

@permission_required('bookreader.change_book')
def pages(request, object_id, **kwargs):
    kwargs.setdefault('template_name','bookreader/editor/pages.html')
    return book_view(request, object_id, **kwargs)

@permission_required('bookreader.change_book')
def exterior(request, object_id, **kwargs):
    kwargs.setdefault('template_name', 'bookreader/editor/exterior.html')
    kwargs.setdefault('extra_context', {})
    
    book = get_object_or_404(Book, identifier=object_id)
    exterior = list(book.external_views)
    views = ['front','back','side','spine','top','bottom']
    
    for view in tuple(exterior):
        if view.title not in views:
            exterior.remove(view)
    
    compiled = map(lambda v: v.title, exterior)
    
    for view in views:
        if view not in compiled:
            exterior.append(Page.objects.create(book=book,title=view,sequence=0,
                                               internal=False))
    
    kwargs['extra_context']['exterior'] = exterior
    
    return book_view(request, object_id, **kwargs)

@permission_required('bookreader.change_book')
@csrf_exempt
def update_page_order(request, object_id, **kwargs):
    kwargs.setdefault('redirect',reverse('bookreader-editor-pages', args=[object_id]))
    book = get_object_or_404(Book, identifier=object_id)
    
    if 'redirect' in request.GET:
        kwargs['redirect'] = request.GET['redirect']
    
    if 'page' in request.POST:
        pages = request.POST.getlist('page')
    elif 'page' in request.GET:
        pages = request.GET.getlist('page')
    else:
        if request.is_ajax():
            return ajax(request,'{"error": "No pages supplied"}')
        
        messages.add_message(request, messages.ERROR,
                             'No pages supplied when trying to update page order')
        
        return HttpResponseRedirect(kwargs['redirect'])
    
    try:
        pages = map(lambda p: Page.objects.get(pk=p,internal=True), pages)
    except Page.DoesNotExist:
        if request.is_ajax():
            return ajax(request,'{"error": "Invalid page supplied"}')
        
        messages.add_message(request, messages.ERROR,
                             'Invalid pages supplied when trying to update page order')
        
        return HttpResponseRedirect(kwargs['redirect'])
    
    if len(pages) != book.pages.filter(internal=True).count():
        if request.is_ajax():
            return ajax(request,'{"error": "Invalid number of pages supplied"}')
        
        messages.add_message(request, messages.ERROR,
                             'Invalid number of pages supplied when trying to update page order')
        
        return HttpResponseRedirect(kwargs['redirect'])
    
    for page in pages:
        if page.book != book:
            if request.is_ajax():
                return ajax(request,'{"error": "Invalid pages supplied (from another book)"}')
            
            messages.add_message(request, messages.ERROR,
                                 'Invalid pages supplied from another book when trying to update page order')
            
            return HttpResponseRedirect(kwargs['redirect'])
    
    sequence = 1
    
    for page in pages:
        if page.internal:
            page.sequence = sequence
            page.save()
            sequence += 1
    
    if request.is_ajax():
        return ajax(request,dumps({'success': True}))
    
    messages.add_message(request, messages.INFO,
                         'Page order updated for %s' % (book.title,))
    
    return HttpResponseRedirect(kwargs['redirect'])

def ajax(request, response):
    return HttpResponse(response, mimetype='application/json')

@permission_required('bookreader.add_book')
def add_book(request, **kwargs):
    """ Add a new book to a collection """
    kwargs.setdefault('template_name', 'bookreader/editor/add_book.html')
    kwargs.setdefault('form_class', BookForm)
    kwargs.setdefault('identifier_generator', generate_random_identifier)        
    
    if request.method == 'POST':
        form = kwargs['form_class'](request.POST)
        if form.is_valid():
            book = form.save(commit=False)
            book.identifier = kwargs['identifier_generator']()
            book.published = False
            book.save()
            
            messages.add_message(request, messages.INFO,
                                 'Added a new book, %s, to the collection %s.' % 
                                 (book.title, book.collection.name,))
            
            return HttpResponseRedirect(reverse('bookreader-book',
                                                args=[book.identifier]))
    else:
        form = kwargs['form_class']()
    
    return render_to_response(kwargs['template_name'], {'form': form},
                              RequestContext(request))
    
@permission_required('bookreader.add_page')
@csrf_exempt
def add_page(request, object_id, **kwargs):
    kwargs.setdefault('template_name','bookreader/editor/add_page.html')
    kwargs.setdefault('redirect',reverse('bookreader-editor-pages', args=[object_id]))
    kwargs.setdefault('form_class', PageForm)
    
    book = get_object_or_404(Book, identifier=object_id)
    
    if 'redirect' in request.GET:
        kwargs['redirect'] = request.GET['redirect']
    
    if request.method == 'POST':
        form = kwargs['form_class'](request.POST)
        if form.is_valid():
            log.debug('Add page form is valid')
            pages = []
            page = form.save(commit=False)
            
            if page.sequence:
                log.debug('Page sequence from form')
                base_sequence = page.sequence
            elif book.pages.count() > 0:
                log.debug('Page sequence from max + 1')
                base_sequence = book.pages.aggregate(Max('sequence')).get('sequence__max',0) + 1
            else:
                log.debug('Page sequence set to 1')
                base_sequence = 1
            
            try:
                count = int(request.POST.get('count',1))
                log.debug('Number of pages to add: %d' % (count,))
            except:
                log.debug('Number of pages to add set to 1')
                count = 1
            
            for sequence in range(base_sequence, base_sequence + count):
                log.debug('Adding sequence #%d' % (sequence,))
                temp = Page.objects.create(book=book, internal=page.internal,
                                           title=page.title, sequence=sequence,
                                           jp2=page.jp2,
                                           thumbnail=page.thumbnail)
                
                pages.append(temp.pk)
            
            if request.is_ajax():
                return ajax(request, dumps({'added': pages}))
            
            messages.add_message(request, messages.INFO, 'Added a new page to ' % (book.title,))
            
            return HttpResponseRedirect(kwargs['redirect'])
        if request.is_ajax():
            return ajax(request, dumps({'errors': unicode(form.errors)}))
    else:
        if request.is_ajax():
            page = Page(book=book)
            if book.pages.count() > 0:
                page.sequence = book.pages.aggregate(Max('sequence')).get('sequence__max',1)
            page.save()
            return ajax(request,'{"added": %d}' % (page.pk,))
        
        form = kwargs['form_class']()
    
    return render_to_response(kwargs['template_name'], {'form': form},
                              RequestContext(request))
    
@permission_required('bookreader.change_page')
@csrf_exempt
def edit_page(request, object_id, **kwargs):
    kwargs.setdefault('template_name','bookreader/editor/edit_page.html')
    kwargs.setdefault('form_class', PageForm)
    
    page = get_object_or_404(Page, pk=object_id)
    book = page.book
    
    kwargs.setdefault('redirect',reverse('bookreader-editor-pages', args=[book.identifier]))
    
    if 'redirect' in request.GET:
        kwargs['redirect'] = request.GET['redirect']
    
    if request.method == 'POST':
        form = kwargs['form_class'](request.POST, instance=page)
        if form.is_valid():
            form.save()
            
            if request.is_ajax():
                return ajax(request,'{"updated": %d}' % (page.pk,))
            
            messages.add_message(request, messages.INFO, 'Updated a page for %s' % (book.title,))
            
            return HttpResponseRedirect(kwargs['redirect'])
        if request.is_ajax():
            return ajax(request, dumps({'errors': unicode(form.errors)}))
    else:
        form = kwargs['form_class'](instance=page)
        
    if request.is_ajax():
        return HttpResponse(form.as_p())
    
    return render_to_response(kwargs['template_name'], {'form': form, 'page': page},
                              RequestContext(request))

@permission_required('bookreader.delete_page')
@csrf_exempt
def delete_page(request, object_id, **kwargs):
    kwargs.setdefault('template_name','bookreader/editor/delete_page.html')
    
    page = get_object_or_404(Page, pk=object_id)
    book = page.book
    
    kwargs.setdefault('redirect',reverse('bookreader-editor-pages', args=[book.identifier]))
    
    id = page.pk
    
    page.delete()
    
    if request.is_ajax():
        return ajax(request,'{"deleted": %d}' % (id,))
    
    return render_to_response(kwargs['template_name'], {'page': page},
                              RequestContext(request))

@permission_required('bookreader.change_book')
def references(request, object_id, **kwargs):
    kwargs.setdefault('template_name', 'bookreader/editor/references.html')
    kwargs.setdefault('form_class', ReferenceForm)
    
    kwargs.setdefault('redirect',reverse('bookreader-editor-pages', args=[object_id]))
    
    book = get_object_or_404(Book, identifier=object_id)
    
    if book.type == 'work':
        messages.add_message(request, messages.ERROR, 'Cannot set references on a work')
        
        return HttpResponseRedirect(kwargs['redirect'])
    
    if book.type == 'canonical':
        class TempClass(kwargs['form_class']):
            class Meta:
                exclude = ('canonical',)
        
        kwargs['form_class'] = TempClass
    
    if request.method == 'POST':
        form = kwargs['form_class'](request.POST, instance=book)
        if form.is_valid():
            book = form.save()
            
            if request.is_ajax():
                return ajax(request,'{"updated": %d}' % (book.pk,))
            if book.canonical:
                messages.add_message(request, messages.INFO, 'Set canonical reference for %s to %s ' % (book.title,book.canonical.title,))
            if book.work:
                messages.add_message(request, messages.INFO, 'Set work reference for %s to %s' % (book.title,book.work.title,))
            
            return HttpResponseRedirect(kwargs['redirect'])
        if request.is_ajax():
            return ajax(request, dumps({'errors': unicode(form.errors)}))
    else:
        form = kwargs['form_class'](instance=book)
    
    if request.is_ajax():
        return HttpResponse(form.as_p())
    
    return render_to_response(kwargs['template_name'], {'form': form, 'book': book},
                              RequestContext(request))

@permission_required('bookreader.change_book')
def copy_annotations(request, object_id, **kwargs):
    kwargs.setdefault('redirect',reverse('bookreader-editor-pages', args=[object_id]))
    book = get_object_or_404(Book, identifier=object_id)
    
    if book.type == 'canonical':
        if request.is_ajax():
            return ajax(request, dumps({'error': 'Cannot copy annotations to a canonical book'}))
        messages.add_message(request, messages.ERROR, 'Cannot copy annotations to a canonical book')
        return HttpResponseRedirect(kwargs['redirect'])
    
    if not book.canonical:
        if request.is_ajax():
            return ajax(request, dumps({'error': 'No canonical book set to copy from'}))
        messages.add_message(request, messages.ERROR, 'No canonical book set')
        return HttpResponseRedirect(kwargs['redirect'])
    
    added = 0
    
    for annotation in book.canonical.annotations.all():
        Annotation.objects.create(book=book, offset=annotation.offset,
                                  length=annotation.length,
                                  structural=annotation.structural,
                                  text=annotation.text)
        added += 1
    
    if request.is_ajax():
        return ajax(request, dumps({'success': '%d annotations copied' % (added,)}))
    
    messages.add_message(request, messages.INFO, '%d annotations copied' % (added,))
    return HttpResponseRedirect(kwargs['redirect'])


@permission_required('bookreader.add_annotation')
@csrf_exempt
def add_annotation(request, object_id, **kwargs):
    kwargs.setdefault('template_name','bookreader/editor/add_annotation.html')
    kwargs.setdefault('redirect',reverse('bookreader-editor-pages', args=[object_id]))
    kwargs.setdefault('form_class', AnnotationForm)
    
    book = get_object_or_404(Book, identifier=object_id)
    
    if 'redirect' in request.GET:
        kwargs['redirect'] = request.GET['redirect']
    
    if request.method == 'POST':
        form = kwargs['form_class'](request.POST)
        if form.is_valid():
            annotation = form.save(commit=False)
            annotation.book = book
            annotation.save()
            
            if request.is_ajax():
                return ajax(request,'{"added": %d}' % (annotation.pk,))
            
            messages.add_message(request, messages.INFO, 'Added a new annotation to %s' % (book.title,))
            
            return HttpResponseRedirect(kwargs['redirect'])
        if request.is_ajax():
            return ajax(request, dumps({'errors': unicode(form.errors)}))
    else:
        form = kwargs['form_class']()    
    
    if request.is_ajax():
        return HttpResponse(form.as_p())
    
    return render_to_response(kwargs['template_name'], {'form': form},
                              RequestContext(request))

@permission_required('bookreader.change_annotation')
@csrf_exempt
def edit_annotation(request, object_id, **kwargs):
    kwargs.setdefault('template_name','bookreader/editor/edit_annotation.html')
    kwargs.setdefault('form_class', AnnotationForm)
    
    annotation = get_object_or_404(Annotation, pk=object_id)
    book = annotation.book
    
    kwargs.setdefault('redirect',reverse('bookreader-editor-pages', args=[book.identifier]))
    
    if 'redirect' in request.GET:
        kwargs['redirect'] = request.GET['redirect']
    
    if request.method == 'POST':
        form = kwargs['form_class'](request.POST, instance=annotation)
        if form.is_valid():
            annotation = form.save()
            
            if request.is_ajax():
                return ajax(request,'{"updated": %d}' % (annotation.pk,))
            
            messages.add_message(request, messages.INFO, 'Updated the annotation: %s' % (annotation.text,))
            
            return HttpResponseRedirect(kwargs['redirect'])
        if request.is_ajax():
            return ajax(request, dumps({'errors': unicode(form.errors)}))
    else:
        form = kwargs['form_class'](instance=annotation)
    
    if request.is_ajax():
        return HttpResponse(form.as_p())
    
    return render_to_response(kwargs['template_name'], {'form': form,
                                                        'annotation': annotation},
                              RequestContext(request))

@permission_required('bookreader.delete_annotation')
def delete_annotation(request, object_id, **kwargs):
    kwargs.setdefault('template_name','bookreader/editor/delete_annotation.html')
    
    annotation = get_object_or_404(Annotation, pk=object_id)
    book = annotation.book
    
    kwargs.setdefault('redirect',reverse('bookreader-editor-pages', args=[book.identifier]))
    
    id = annotation.pk
    
    annotation.delete()
    
    if request.is_ajax():
        return ajax(request,'{"deleted": %d}' % (id,))
    
    return render_to_response(kwargs['template_name'], {'annotation': annotation},
                              RequestContext(request))

@permission_required('bookreader.change_book')
def publish(request, object_id, **kwargs):
    book = get_object_or_404(Book, pk=object_id)
    
    if book.published:
        messages.add_message(request, messages.ERROR,
                             '%s is already published' % (book.title,))
        return HttpResponseRedirect(reverse('bookreader-book',
                                            args=[book.identifier]))
    
    if not book.collection.repository.sword_enabled:
        messages.add_message(request, messages.ERROR,
                             'SWORD is not enabled on the repository for %s' % 
                             (book.title,))
    
    item = SwordItem()
    item.add_file(bitstream_metadata(book), 'bitstream_metadata.xml',
                  'METADATA')
    
    item.add_descriptive_metadata(
        '''<mdWrap MDTYPE="OTHER" OTHERMDTYPE="DIM">
             <xmlData>
                 <dim:dim xmlns:dim="http://www.dspace.org/xmlns/dspace/dim">
                     <dim:field mdschema="dc" element="title">%s</dim:field>
                 </dim:dim>
             </xmlData>
         </mdWrap>''' % (book.title,))
    
    repository = book.collection.repository.connection()
    
    handle = repository.sword.deposit(book.collection.handle,
                                      item.get_package())
    
    if handle is None:
        messages.add_message(request, messages.ERROR,
                             'Error performing the SWORD deposit for %s' % 
                             (book.title,))
        return HttpResponseRedirect(reverse('bookreader-book',
                                            args=[book.identifier]))
    
    old = Book.objects.get(identifier=book.identifier)
    
    book.identifier = repository.getOAIItemIdentifier(handle)
    book.published = True
    book.save()
    
    for page in old.pages.all():
        page.book = book
        page.save()
    
    for annotation in old.annotations.all():
        annotation.book = book
        annotation.save()
    
    for manifestation in old.manifestations.all():
        log.info('Updating work reference on %s' % (manifestation.title,))
        manifestation.work = book
        manifestation.save()
    
    for copy in old.copies.all():
        log.info('Updating canonical reference on %s' % (copy.title,))
        copy.canonical = book
        copy.save()
    
    old.delete()
    
    messages.add_message(request, messages.INFO, 
                         'Published the book, %s' % (book.title,))
    return HttpResponseRedirect(reverse('bookreader-book',
                                            args=[book.identifier]))
    