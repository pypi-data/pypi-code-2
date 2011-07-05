#-*- coding: utf-8 -*-
from django import template
from contentadmin.models import TextContent, Page

register = template.Library()

def blocktext(parser, token):
    args = token.split_contents()
    if not len(args) in [3, 4]:
        raise template.TemplateSyntaxError("""Block text must contains 2 or 3 arguments "page_name", "var_name" and "admin_label" 
            {% blocktext contact header_text "Let us a message" %}
        """)
        
    page, var_name = args[1], args[2]
    admin_label = args[3][1:-1] if len(args) == 4 else var_name
    
    nodelist = parser.parse(('endblocktext',))
    parser.delete_first_token()
    return BlockTextNode(nodelist, page, var_name, admin_label)

class BlockTextNode(template.Node):
    
    def __init__(self, nodelist, page, var_name, admin_label):
        self.nodelist = nodelist
        self.page = page
        self.var_name = var_name
        self.admin_label = admin_label
        
    def render(self, context):
        output = self.nodelist.render(context)
        page, created = Page.objects.get_or_create(name=self.page)
        text_content, created = TextContent.objects.get_or_create(name=self.var_name, page=page)
        
        # create a context dict to check var_name, new position and new admin label.
        context["blocktext"] = context.get("blocktext", {self.page: {"names": [], "position": 0}})
        context["blocktext"][self.page]["names"].append(self.var_name)
        context["blocktext"][self.page]["position"] += 1
        
        current_page = context["blocktext"][self.page]
        changed = False
        
        if text_content.position != current_page["position"]:
            text_content.position = current_page["position"]
            changed = True
            
        if text_content.admin_label != self.admin_label:
            text_content.admin_label = self.admin_label
            changed = True
            
        if created:
            text_content.text = output
            changed = True
            
        if changed:    
            text_content.save()
            
        return text_content.text
    

