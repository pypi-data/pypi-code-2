#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2008
"""
import cherrypy
from simplejson import dumps
from cocktail.modeling import cached_getter
from cocktail.events import event_handler
from cocktail.translations import translations
from cocktail import schema
from cocktail.schema import Reference, String, Integer, Collection
from woost.models import Item
from woost.controllers.backoffice.basebackofficecontroller \
    import BaseBackOfficeController, EditNode


class OrderController(BaseBackOfficeController):

    @cached_getter
    def handling_ajax_request(self):
        return self.rendering_format == "json"

    @cached_getter
    def edited_content_type(self):
        return self.item.__class__

    @cached_getter
    def content_type(self):
        return self.member.items.type
    
    @cached_getter
    def collection(self):
        return schema.get(self.stack_node.form_data, self.member)
    
    @cached_getter
    def member(self):
        key = self.params.read(String("member"))
        return self.edited_content_type[key] if key else None

    @cached_getter
    def item(self):
        return self.stack_node.item

    @cached_getter
    def selection(self):
        return self.params.read(
            Collection("selection",
                items = Reference(type = self.content_type)
            )
        )
    
    @cached_getter
    def position(self):
        return self.params.read(
            Integer("position",
                min = 0,
                max = len(self.collection)
            )
        )

    @cached_getter
    def action(self):
        return self.params.read(String("action"))

    @cached_getter
    def ready(self):
        return self.action == "order" \
            and self.selection \
            and self.position is not None

    def submit(self):
        
        def rearrange(collection, items, position):

            size = len(collection)
            
            if position < 0:
                position = size + position

            if position + len(items) > size:
                position = size - len(items)

            for item in items:
                collection.remove(item)
            
            for item in reversed(list(items)):
                collection.insert(position, item)
            
            return collection                   
                   
        rearrange(self.collection, self.selection, self.position)

    def handle_error(self, error):
        if self.handling_ajax_request:
            self.output["error"] = translations(error)
        else:
            BaseBackOfficeController.handle_error(self, error)
    
    @event_handler
    def handle_after_request(cls, event):
        
        controller = event.source

        if not controller.handling_ajax_request:
            if controller.action == "cancel" \
            or (controller.action == "order" and controller.successful):
                if controller.edit_stack:
                    controller.edit_stack.go(-2)
                else:
                    raise cherrypy.HTTPRedirect(controller.relative_uri())

    view_class = "woost.views.BackOfficeOrderView"

    @cached_getter
    def output(self):
        if self.handling_ajax_request:
            return {}
        else:
            output = BaseBackOfficeController.output(self)
            output.update(
                content_type = self.content_type,
                collection = self.collection,
                selection = self.selection
            )
            return output

