#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2010
"""
from cocktail.events import event_handler
from cocktail.translations import translations
from cocktail.persistence import datastore
from woost.models import Extension

translations.define("SitemapExtension",
    ca = u"Refinament de l'indexat web",
    es = u"Refinamiento del indexado web",
    en = u"Web crawler hints"
)

translations.define("SitemapExtension-plural",
    ca = u"Refinament de l'indexat web",
    es = u"Refinamiento del indexado web",
    en = u"Web crawler hints"
)


class SitemapExtension(Extension):

    def __init__(self, **values):
        Extension.__init__(self, **values)
        self.extension_author = u"Whads/Accent SL"
        self.set("description",
            u"""Genera un mapa de documents per optimitzar l'indexat del lloc
            web, seguint l'estàndard sitemap.org.""",
            "ca"
        )
        self.set("description",            
            u"""Genera un mapa de documentos para optimizar el indexado del
            sitio, siguiendo el estándard sitemap.org.""",
            "es"
        )
        self.set("description",
            u"""Generates a document map to optimize the indexing of the site
            by web crawlers, following the sitemap.org standard.""",
            "en"
        )

    @event_handler
    def handle_loading(cls, event):    
        from woost.models import (
            Site,
            Publishable,
            Document,
            Controller
        )
        from woost.extensions.sitemap import publishable, strings
        
        # Sitemap controller
        sitemap_controller = Controller.get_instance(
            qname = "woost.extensions.sitemap.sitemap_controller"
        )
        if sitemap_controller is None:
            sitemap_controller = Controller()
            sitemap_controller.set("title", u"Controlador de mapa web", "ca")
            sitemap_controller.set("title", u"Controlador de mapa web", "es")
            sitemap_controller.set("title", u"Sitemap controller", "en")
            sitemap_controller.python_name = \
                "woost.extensions.sitemap.sitemapcontroller.SitemapController"
            sitemap_controller.qname = \
                "woost.extensions.sitemap.sitemap_controller"
            sitemap_controller.insert()

        # Sitemap document
        sitemap_doc = Document.get_instance(
            qname = "woost.extensions.sitemap.sitemap_document"
        )
        if sitemap_doc is None:
            sitemap_doc = Document()
            sitemap_doc.set("title", u"Mapa XML del lloc web", "ca")
            sitemap_doc.set("title", u"Mapa XML del sitio web", "es")
            sitemap_doc.set("title", u"XML sitemap", "en")
            sitemap_doc.parent = Site.main.home
            sitemap_doc.path = "sitemap_xml"
            sitemap_doc.per_language_publication = False
            sitemap_doc.mime_type = "text/xml"
            sitemap_doc.hidden = True
            sitemap_doc.sitemap_indexable = False
            sitemap_doc.qname = \
                "woost.extensions.sitemap.sitemap_document"
            sitemap_doc.controller = sitemap_controller
            sitemap_doc.insert()

        # Force indexing of the 'sitemap_indexable' member
        # (can't rely on defaults when executing queries)
        for item in Publishable.select():
            if not hasattr(item, "_sitemap_indexable"):
                item.sitemap_indexable = \
                    item.sitemap_indexable \
                    and not item.hidden

        datastore.commit()

