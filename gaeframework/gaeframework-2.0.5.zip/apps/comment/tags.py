from gae import template
from gae import webapp
from gae.tags import node_rule, BaseNode
from comment.models import Comment
from comment.forms import UserCommentForm

register = template.create_template_register()

@register.tag
@node_rule(BaseNode, ('for [object_instance] as [varname]', 'for [object_type] [object_id] as [varname]'))
def get_comment_count(self, context):
    '''Get total count of comments for given object'''
    obj = self.get_object(context)
    qs = Comment.all().filter("obj =", obj)
    context[self.varname] = qs.count()
    return ''

@register.tag
@node_rule(BaseNode, ('for [object_instance] as [varname]', 'for [object_type] [object_id] as [varname]'))
def get_comment_list(self, context):
    '''Get list of comments for given object'''
    obj = self.get_object(context)
    qs = Comment.all().filter("obj =", obj)
    context[self.varname] = list(qs)
    return ''

@register.tag
@node_rule(BaseNode, ('for [object_instance]', 'for [object_type] [object_id]'))
def render_comment_list(self, context):
    '''Render list of comments for given object'''
    obj = self.get_object(context)
    qs = Comment.all().filter("obj =", obj)
    return webapp.instance.render("comments/block/comment_list", {'comment_list': list(qs)})

@register.tag
@node_rule(BaseNode, ('for [object_instance] as [varname]', 'for [object_type] [object_id] as [varname]'))
def get_comment_form(self, context):
    '''Get a form object to post a new comment'''
    obj = self.get_object(context)
    context[self.varname] = UserCommentForm(initial={'object': obj.key()})
    return ''

@register.tag
@node_rule(BaseNode, ('for [object_instance]', 'for [object_type] [object_id]'))
def render_comment_form(self, context):
    '''Render the comment form (as returned by ``{% render_comment_form %}``)
    through the `comment/form.html` template'''
    obj = self.get_object(context)
    form = UserCommentForm(initial={'obj': obj.key()})
    return webapp.instance.render("comments/block/form", {'form': form})