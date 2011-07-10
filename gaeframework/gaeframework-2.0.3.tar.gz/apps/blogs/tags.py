from gae import template, webapp
from gae.markup import Wiki
from gae.tags import node_rule, BaseNode
from blog.models import Blog, Entity

register = template.create_template_register()

@register.tag
@node_rule(BaseNode, ("", "as [varname]"))
def get_recent_blogs(self, context):
    '''Get list of latest blog posts'''
    collection = Blog.all().filter("active", True).order("-created").fetch(10)
    if hasattr(self, "varname"):
        context[self.varname] = collection
        return ""
    return webapp.instance.render("blog/block/blogs_list", {"blogs": collection})

@register.tag
@node_rule(BaseNode, ("", "for [blog]", "as [varname]", "for [blog] as [varname]"))
def get_recent_entities(self, context):
    '''Get list of latest blog posts'''
    collection = Entity.all().filter("active", True).order("-changed")
    if hasattr(self, "blog"):
        collection.filter("blog", self.get_var(context, self.blog))
    collection.fetch(10)
    if hasattr(self, "varname"):
        context[self.varname] = collection
        return ""
    return webapp.instance.render("blog/block/entities_list", {"entities": collection})

@register.filter
def wiki(raw_data):
    return Wiki().parse(raw_data)