from gae import template, webapp
from gae.markup import Wiki
from gae.tags import node_rule, BaseNode
from apps.blog.models import Entity

register = template.create_template_register()

@register.tag
@node_rule(BaseNode, ("", "as [varname]"))
def get_recent_entries(self, context):
    '''Get list of latest blog posts'''
    collection = Entity.all().filter("active", True).order("-changed")
    collection.fetch(10)
    if hasattr(self, "varname"):
        context[self.varname] = collection
        return ""
    return webapp.instance.render("blog/block/entries_list", {"entries": collection})

@register.filter
def wiki(raw_data):
    return Wiki().parse(raw_data)