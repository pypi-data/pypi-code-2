from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from models import DiscussionPlugin, Discussion
from django.utils.translation import ugettext as _
from django.contrib.comments.models import Comment
from django.contrib.contenttypes.models import ContentType

class CMSDiscussionPlugin(CMSPluginBase):
        model = DiscussionPlugin
        name = _("Comments")
        render_template = "comments/list.html"

        def render(self, context, instance, placeholder):
            
            comments = Comment.objects.filter (
                content_type=ContentType.objects.get_for_model(Discussion),
                object_pk = instance.discussion.id)
            
            context.update({'instance':instance.discussion,
                            'placeholder':placeholder,
                            'comments':comments})
            return context

plugin_pool.register_plugin(CMSDiscussionPlugin)
