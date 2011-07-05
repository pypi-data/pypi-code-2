#-*- coding: utf-8 -*-
from django import template
from contentadmin.models import TextContent, ImageContent, Page

register = template.Library()

def unusedblocks(parser, token):
    return UnusedBlocksNode()

class UnusedBlocksNode(template.Node):
    
    def render(self, context):
        for page in context.get("blocktext", []):
            names = context["blocktext"][page]["names"]
            TextContent.objects.filter(page__name=page).exclude(name__in = names).delete()
            
        for page in context.get("blockimage", []):
            names = context["blockimage"][page]["names"]
            ImageContent.objects.filter(page__name=page).exclude(name__in = names).delete()
        return ""

