#!/usr/bin/env python
# encoding: utf-8
"""
helpers.py

Created by Keith Fahlgren on Mon Oct  5 17:26:55 PDT 2009
Copyright (c) 2009 O'Reilly Media. All rights reserved.
"""

import datetime
import logging
import uuid

import pytz

import mock_http

from atompiglet.server import Server

log = logging.getLogger(__name__)

ENTRY_COLLECTION_URL = 'newentry'
PDF_COLLECTION_URL = 'newpdf'
PDF_ENTRY_EDIT_URL = '/edit'
PDF_ENTRY_EDIT_MEDIA_URL = '/media'

def fake_server(port, url, auth):
    mock = mock_http.MockHTTP(port)
    mock.server.wsgi_app.apps.values()[0].log.access_log.setLevel(logging.WARNING) # Shut up, Cherrypy

    service_doc ='''
<service xmlns="http://www.w3.org/2007/app" xmlns:atom="http://www.w3.org/2005/Atom" xml:base="%s">
  <workspace>
    <atom:title type="text">O'Reilly Media</atom:title>
    <collection href="%s">
        <atom:title type="text">Web PDFs</atom:title>
        <accept>application/pdf</accept>
    </collection>
    <collection href="%s">
        <atom:title type="text">Entries</atom:title>
        <accept>application/atom+xml</accept>
    </collection>
  </workspace>
</service>''' % (url, PDF_COLLECTION_URL, ENTRY_COLLECTION_URL)
    mock.expects('GET', '/', times=mock_http.once).will(http_code=200, body=service_doc)
    server = Server(url, auth=auth)
    mock.verify()
    return server

def fake_new_pdf_entry(hostname, port, url, server, test_pdf):
    hostname = hostname
    mock = mock_http.MockHTTP(port)
    mock.server.wsgi_app.apps.values()[0].log.access_log.setLevel(logging.WARNING) # Shut up, Cherrypy
    wksp = server.workspaces["O'Reilly Media"]
    webpdfs_coll = wksp.collections["Web PDFs"]

    pdf_entry = fake_entry(edit_url=PDF_ENTRY_EDIT_URL, edit_media_url=PDF_ENTRY_EDIT_MEDIA_URL)
    new_etag = str(uuid.uuid4())
    mock.expects('POST', '/' + PDF_COLLECTION_URL, times=mock_http.once).will(http_code=201, 
                                                                                body=pdf_entry,
                                                                                headers={'Location': url + PDF_ENTRY_EDIT_URL,
                                                                                        'Content-Location': url + PDF_ENTRY_EDIT_URL, 
                                                                                        'ETag': new_etag},
                                                                                )
    pdf_mimetype = 'application/pdf' 
    new_entry = webpdfs_coll.add_from_file(test_pdf, pdf_mimetype)
    mock.verify()
    return new_entry

def fake_entry(edit_url=PDF_ENTRY_EDIT_URL, 
               edit_media_url=PDF_ENTRY_EDIT_MEDIA_URL, 
               summary='SUMMARY_TEXT', 
               title='TITLE_TEXT', 
               updated=datetime.datetime.now(pytz.utc)):
    content_url = edit_media_url + '/content'
    entry = '''
<entry xmlns:app="http://www.w3.org/2007/app" 
    xmlns="http://www.w3.org/2005/Atom">
<author>
<name>Web PDFs</name>
</author>
<content type="application/pdf" src="%s"/>
<app:edited>2009-10-02T20:48:12.848Z</app:edited>
<id>tag:oreilly.com,2009-10-02:/oreilly/webpdfs/327605</id>
<link rel="edit" href="%s"/>
<link rel="edit-media" href="%s"/>

<summary type="text">%s</summary>
<title type="text">%s</title>
<updated>%s</updated>
</entry>
''' % (content_url, edit_url, edit_media_url, summary, title, updated.isoformat())
    return entry

def fake_feed(url, length=9, next=False):
    feed = '''
<feed xmlns="http://www.w3.org/2005/Atom">
<title type="text">Web PDFs</title>
<link href="%s" rel="self"/>
<id>%s</id>
<updated>2009-10-02T22:31:24.289Z</updated>
'''
    if next:
        feed = feed + '\n<link href="%s" rel="next"/>\n' % next
    for i in range(0, length):
        eu = '%s/edit/%s' % (url, i)
        emu = '%s/editmedia/%s' % (url, i)
        feed = feed + fake_entry(edit_url=eu, edit_media_url=emu)
    feed = feed + '</feed>'
    return feed

def fake_atom_feed(url, length=9, next=False):
    feed = '''
<feed xmlns="http://www.w3.org/2005/Atom">
<title type="text">Web PDFs</title>
<link href="%s" rel="self"/>
<id>%s</id>
<updated>2009-10-02T22:31:24.289Z</updated>
'''
    if next:
        feed = feed + '\n<link href="%s" rel="next"/>\n' % next
    for i in range(0, length):
        content = str(uuid.uuid4())
        feed = feed + fake_atom_entry(content=content)
    feed = feed + '</feed>'
    return feed

def fake_atom_entry(content='CONTENT_TEXT',
               title='TITLE_TEXT', 
               updated=datetime.datetime.now(pytz.utc)):
    entry = '''
<entry xmlns:app="http://www.w3.org/2007/app" 
    xmlns="http://www.w3.org/2005/Atom">
<author>
    <name>Pure Atom Entry</name>
</author>
<content type="text">%s</content>
<id>tag:oreilly.com,2009-10-02:/oreilly/webpdfs/327605</id>
<title type="text">%s</title>
<updated>%s</updated>
</entry>
''' % (content, title, updated.isoformat())
    return entry
