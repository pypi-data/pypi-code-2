import re

from django import template
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse

from green_comments.models import Comment
from green_comments.forms import CommentForm

register = template.Library()

@register.inclusion_tag('green_comments/comment_tree.html', takes_context=True)
def comment_tree(context, object):
    ct = ContentType.objects.get_for_model(object)
    comments = Comment.objects.filter(content_type=ct, object_id=object.pk)\
                      .select_related(depth=1)\
                      .order_by('created')

    mapping = {}
    tree = []

    for comment in comments:
        item = {'comment': comment, 'children': []}
        mapping[comment.pk] = item

    for comment in comments:
        if comment.parent is None:
            tree.append(mapping[comment.pk])
        else:
            mapping[comment.parent.pk]['children'].append(mapping[comment.pk])

    flat_tree = []

    def process(item, depth):
        flat_tree.append(item['comment'])
        if item['children']:
            flat_tree.append(1)
            for child in item['children']:
                process(child, depth + 1)
            flat_tree.append(-1)

    for item in tree:
        process(item, 1)

    context['tree'] = flat_tree
    context['object'] = object
    return context


@register.inclusion_tag('green_comments/_comment_form.html', takes_context=True)
def comment_form(context, object):
    user = context['user']
    if user.is_authenticated():
        instance = Comment(content_object=object, user=user)
        form = CommentForm(instance=instance)
    else:
        form = None
    return {'form': form,
            'object': object,
            'parent': None,
            'request': context['request'],
            'user': context['user'],
            }


@register.tag()
def get_comment_count(parser, token):
    match = re.search(r'(\w+) (\S+) as (\S+)', token.contents)
    tag_name, object_name, var_name = match.groups()
    return GetCommentCountNode(object_name, var_name)


class GetCommentCountNode(template.Node):
    def __init__(self, object_name, var_name):
        self.object = template.Variable(object_name)
        self.var_name = var_name

    def render(self, context):
        obj = self.object.resolve(context)
        ct = ContentType.objects.get_for_model(obj)
        context[self.var_name] = Comment.objects.filter(content_type=ct,
                                                        object_id=obj.pk).count()
        return ''


@register.simple_tag
def comment_form_action(object, parent=None):
    if parent:
        return reverse('comment_reply', args=[parent.pk])
    else:
        ct = ContentType.objects.get_for_model(object)
        return reverse('comment_create', args=[ct.pk, object.pk])
