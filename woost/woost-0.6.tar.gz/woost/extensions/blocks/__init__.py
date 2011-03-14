#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Jordi Fernández <jordi.fernandez@whads.com>
"""
from cocktail.events import event_handler
from cocktail.translations import translations
from cocktail.persistence import datastore
from cocktail.html import templates
from woost.models import Extension, Template


translations.define("BlocksExtension",
    ca = u"Blocs de contingut",
    es = u"Bloques de contenido",
    en = u"Content blocks"
)

translations.define("BlocksExtension-plural",
    ca = u"Blocs de contingut",
    es = u"Bloques de contenido",
    en = u"Content blocks"
)


class BlocksExtension(Extension):

    def __init__(self, **values):
        Extension.__init__(self, **values)
        self.extension_author = u"Whads/Accent SL"
        self.set("description",
            u"""Permet la creació de contingut utilitzant blocs""",
            "ca"
        )
        self.set("description",            
            u"""Permite la creación de contenido usando bloques""",
            "es"
        )
        self.set("description",
            u"""Allows the creation of content using blocs""",
            "en"
        )

    @event_handler
    def handle_loading(cls, event):

        from woost.extensions.blocks import (
            strings, 
            block, 
            containerblock,
            imagegalleryblock,
            bannerblock,
            menublock,
            richtextblock,
            translatedrichtextblock,
            blockspage
        )

        from woost.extensions.vimeo import VimeoExtension

        if VimeoExtension.instance.enabled:
            from woost.extensions.blocks import vimeoblock

        extension = event.source

        if not extension.installed:
            template = extension._create_blocks_page_template()
            template.insert()
            datastore.commit()

        # Install an overlay for the frontend edit panel
        templates.get_class("woost.extensions.blocks.EditPanelOverlay")

    def _create_blocks_page_template(self):
        blocks_page_template = Template.get_instance(
            identifier = "woost.extensions.blocks.BlocksPageView"
        )
        if blocks_page_template is None:
            blocks_page_template = Template()
            blocks_page_template.set(
                "title", u"Plantilla pàgina de blocs", "ca"
            )
            blocks_page_template.set(
                "title", u"Plantilla página de bloques", "es"
            )
            blocks_page_template.set(
                "title", u"Blocks page template", "en"
            )
            blocks_page_template.identifier = \
                "woost.extensions.blocks.BlocksPageView"
            blocks_page_template.engine = "cocktail"

        return blocks_page_template

