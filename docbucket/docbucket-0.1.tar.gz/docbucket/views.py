#!/usr/bin/env python
#coding=utf8
#
#       Copyright 2010 Antoine Millet <antoine@inaps.org>
#
#       This file is part of DocBucket.
#       
#       Foobar is free software: you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation, either version 3 of the License, or
#       (at your option) any later version.
#       
#       Foobar is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

import os
from PIL import Image
from math import log
from whoosh import index
from whoosh.filedb.filestore import FileStorage
from whoosh.qparser import MultifieldParser
from shutil import move
from datetime import datetime

from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.http import HttpResponse
from django.conf import settings
from django.core.paginator import Paginator, InvalidPage, EmptyPage

from models import Document, DocumentClass, Thumbnail
from helpers import assemble, make_thumbnails, list_incomings
from forms import CreateDocumentForm, CreateDocumentClassForm

def home(request):
	last_created = Document.objects.order_by('-created')[:5]
	last_accessed = Document.objects.order_by('-access')[:5]
	
	cntx = {'last_created': last_created, 'last_accessed': last_accessed}
	return render_to_response('docbucket/home.html', cntx, 
							  context_instance=RequestContext(request))

def create(request):	
	if request.method == 'POST':
		form = CreateDocumentForm(request.POST)
		if form.is_valid():
			name = form.cleaned_data.get('name')
			pages = form.cleaned_data.get('pages')
			doc_class = form.cleaned_data.get('document_class')
			
			# Get the document class:
			doc_class = DocumentClass.objects.get(slug=doc_class)
			
			# Create the document
			doc = Document()
			doc.name = name
			doc.document_class = doc_class
			
			# Assemble files in single hocr-ed PDF:
			pdf, outputs = assemble(pages)
			
			# Insert document in database:
			doc.attachment = open(pdf, 'r')
			doc.attachment.content_type = 'application/pdf'
			
			# Set number of pages of documents in database:
			doc.page_number = len(outputs)
			
			# Generate the thumbnails:
			cover = os.path.join(settings.INCOMING_DIRECTORY, pages[0])
			for size, image in make_thumbnails(cover).iteritems():
				thumb = Thumbnail()
				thumb.size = size
				thumb.image.put(image)
				doc.thumbnails.append(thumb)
			
			# Save the readed (ocr) content into database for later
			# re-indexing:
			doc.content = outputs
			
			# Save the new document
			doc.save()
			
			# Index the document:
			ix = index.open_dir(settings.WHOOSH_INDEX)
			writer = ix.writer()
			writer.add_document(name=name,
								content='\n'.join(outputs.values()).decode('utf-8'),
								doc_id=unicode(doc.id))
			writer.commit()
			
			# Finally, backup the documents:
			for f in pages:
				full = os.path.join(settings.INCOMING_DIRECTORY, f)
				imported_dir = os.path.join(settings.INCOMING_DIRECTORY, '.imported')
				if not os.path.exists(imported_dir):
					os.mkdir(imported_dir)
				move(full, os.path.join(imported_dir, '%s_%s' % (f, doc.id)))
			
			return redirect('show', doc_id=doc.id)
	else:
		form = CreateDocumentForm()
	
	empty = not bool(list_incomings())
	
	return render_to_response('docbucket/create.html', {'form': form, 'empty': empty}, 
							  context_instance=RequestContext(request))

def list(request, doc_class=None):
	if doc_class is None:
		documents = Document.objects
	else:
		doc_class = DocumentClass.objects.get(slug=doc_class)
		documents = Document.objects.filter(document_class=doc_class)

	pages = Paginator(documents, 30)
	try:
		page = int(request.GET.get('page', '1'))
	except ValueError:
		page = 1

	try:
		documents = pages.page(page)
	except (EmptyPage, InvalidPage):
		documents = pages.page(pages.num_pages)
	
	classes = DocumentClass.objects.order_by('name')
	
	cntx = {'documents': documents.object_list, 'paginator': documents,
	        'classes': classes}
	return render_to_response('docbucket/list.html', cntx, 
							  context_instance=RequestContext(request))

def manage(request):
	doc_classes = DocumentClass.objects.order_by('name')
	if request.method == 'POST':
		doc_class_form = CreateDocumentClassForm(request.POST)
		if doc_class_form.is_valid():
			doc_class = DocumentClass()
			doc_class.name = doc_class_form.cleaned_data['name']
			doc_class.slug = doc_class_form.cleaned_data['slug']
			doc_class.save()
			return redirect('manage')
	else:
		doc_class_form = CreateDocumentClassForm()
		
	cntx = {'doc_class_form': doc_class_form, 'doc_classes': doc_classes}
	return render_to_response('docbucket/manage.html', cntx, 
							  context_instance=RequestContext(request))

def show(request, doc_id):
	doc = Document.objects.get(id=doc_id)
	doc.access = datetime.now()
	doc.save()
	return render_to_response('docbucket/show.html', {'doc': doc}, 
							  context_instance=RequestContext(request))

def download(request, doc_id):
	doc = Document.objects.get(id=doc_id)
	doc_filename = doc.name.encode('ascii', 'replace').replace('/', '_')
	response = HttpResponse(mimetype='application/pdf')
	response['Content-Disposition'] = 'filename=%s.pdf' % doc_filename
	response.write(doc.attachment.read())
	return response

def search(request):
	ix = index.open_dir(settings.WHOOSH_INDEX)
	query = request.GET.get('query', None)
	page = request.GET.get('page', 1)
	if isinstance(page, unicode) and page.isdigit():
		page = int(page)
	else:
		page = 1
	found = None
		
	if query is not None and query != u'':
		query = query.replace('+', ' AND ').replace(' -', ' NOT ')
		parser = MultifieldParser(('name', 'content', 'doc_id'), 
								  schema=ix.schema)
		try:
			parsed_query = parser.parse(query)
		except:
			parsed_query = None

		if query is not None:
			searcher = ix.searcher()
			found = searcher.search_page(parsed_query, page, pagelen=30)

	found_docs = []
	for i, found_doc in enumerate(found):
		doc = Document.objects.get(id=found_doc['doc_id'])
		found_docs.append({'doc': doc, 'score': found.score(i)})

	cntx = {'documents': found_docs, 'search': found, 'query': query, 
			'page_results': len(found_docs), 'next_page': page + 1,
			'previous_page': page - 1, 'page': page, 
			'max_pages': found.pagecount}

	return render_to_response('docbucket/search.html', cntx, 
							  context_instance=RequestContext(request))

def document_thumb(request, doc_id, size='small'):
	doc = Document.objects.get(id=doc_id)
	thumbnail = doc.get_thumbnail(size)
	
	if thumbnail is None:
		return '404'
	else:
		response = HttpResponse(mimetype='image/png')
		response.write(thumbnail.read())
		return response
		
def thumb(request, filename):
	filename = os.path.join(settings.INCOMING_DIRECTORY, filename)
	image = Image.open(filename)
	image.thumbnail((190, 270), Image.ANTIALIAS)
	
	response = HttpResponse(mimetype='image/png')
	image.save(response, 'PNG')
	
	return response
