# -*- coding: utf-8 -*-

from fanstatic import Resource, Library
from js.jquery import jquery
from js.tinymce import tinymce


DolmenTinyLibrary = Library('dolmen.tinymce', 'resources')
JqueryTinyMCE = Resource(
    DolmenTinyLibrary, 'jquery_tiny_mce.js', depends=[tinymce, jquery])
