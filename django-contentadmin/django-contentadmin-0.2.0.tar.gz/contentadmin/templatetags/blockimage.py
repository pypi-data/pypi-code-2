#-*- coding: utf-8 -*-
import os
from django import template
from django.conf import settings
from django.core.files import File
from contentadmin.models import ImageContent, Page
from easy_thumbnails.files import get_thumbnailer

register = template.Library()

def blockimage(parser, token):
    args = token.split_contents()
    if not len(args) in [5, 6]:
        raise template.TemplateSyntaxError("""Block image must contains 4 or 5 arguments "page_name", "var_name", width, height and "admin_label" 
            {% blockimage contact header_text 150 150 "Let us a message" %}
        """)
    page, var_name, width, height = args[1], args[2], args[3], args[4]
    admin_label = args[5][1:-1] if len(args) == 6 else var_name
    
    nodelist = parser.parse(('endblockimage',))
    parser.delete_first_token()
    return BlockImageNode(nodelist, page, var_name, width, height, admin_label)
    
class BlockImageNode(template.Node):
    
    def __init__(self, nodelist, page, var_name, width, height, admin_label):
        self.nodelist = nodelist
        self.page = page
        self.var_name = var_name
        self.admin_label = admin_label
        self.width = width
        self.height = height
        
    def render(self, context):
        output = self.nodelist.render(context)
        page, created = Page.objects.get_or_create(name=self.page)
        image_content, created = ImageContent.objects.get_or_create(name=self.var_name, page=page)
        
         # create a context dict to check var_name, new position and new admin label.
        context["blockimage"] = context.get("blockimage", {self.page: {"names": [], "position": 0}})
        context["blockimage"][self.page]["names"].append(self.var_name)
        context["blockimage"][self.page]["position"] += 1
        
        current_page = context["blockimage"][self.page]
            
        if image_content.admin_label != self.admin_label or image_content.width != self.width or image_content.height != self.height or image_content.position != current_page["position"]:
            image_content.admin_label = self.admin_label
            image_content.width = self.width
            image_content.height = self.height
            image_content.position = current_page["position"]
            image_content.save()
            
        if created or not image_content.image:
            if output.startswith(settings.MEDIA_URL):
                output = output.replace(settings.MEDIA_URL, u"", 1)    
            url = os.path.join(settings.MEDIA_ROOT, output)
            try:
                image_content.image.save(os.path.basename(url), File(open(url)))
            except:
                pass 
            
        return get_thumbnailer(image_content.image).get_thumbnail({"size": (image_content.width, image_content.height)}).url if image_content.image else ""
    

