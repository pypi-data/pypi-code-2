# -*- coding: utf-8 -*-

from js.jquery import jquery
from fanstatic import Library, Resource


library = Library('galleriffic', 'resources')
galleriffic = Resource(library, 'jquery.galleriffic.js', depends=[jquery])
