#!/usr/bin/python
# -*- coding: utf-8 -*-

from fanstatic import Library, Resource
from js.jquery_slimbox import slimbox


ImageLibrary = Library('menhir.contenttype.image', 'resources')
ImagePopup = Resource(ImageLibrary, "popup.js", depends=[slimbox])
