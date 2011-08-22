from gae import template
from gae.tags import node_rule, BaseNode

register = template.create_template_register()

@register.tag
@node_rule(BaseNode, ("[obj] [attr]", "[obj] [attr] as [varname]"))
def get_attr(self, context):
    '''Return given attribute in given object'''
    obj  = self.get_var(context, self.obj)
    attr = self.get_var(context, self.attr)
    value = getattr(obj, attr)
    if callable(value):
        value = value()
    if hasattr(self, "varname"):
        varname = self.get_var(context, self.varname)
        context[varname] = value
        return ""
    return value

#@register.tag
#@node_rule(BaseNode, ("", "for [blog]", "as [varname]", "for [blog] as [varname]"))
#def get_recent_entities(self, context):
#    '''Get list of latest blog posts'''
#    collection = Entity.all().filter("active", True).order("-changed")
#    if hasattr(self, "blog"):
#        collection.filter("blog", self.get_var(context, self.blog))
#    collection.fetch(10)
#    if hasattr(self, "varname"):
#        context[self.varname] = collection
#        return ""
#    return webapp.instance.render("blog/block/entities_list", {"entities": collection})
#
#@register.filter
#def wiki(raw_data):
#    return Wiki().parse(raw_data)