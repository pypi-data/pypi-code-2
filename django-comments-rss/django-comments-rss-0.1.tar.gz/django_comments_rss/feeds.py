from django.contrib.syndication.views import Feed
from django.contrib.comments.models import Comment
from django.utils.translation import gettext as _


class CommentsFeed(Feed):
    title = _('User comments RSS')
    link = ''
    description = _('Comments RSS.')

    def items(self):
        return Comment.objects.filter(is_public=True) \
                              .order_by('-submit_date').all()[:5]

    def item_title(self, item):
        return item.content_object.title

    def item_description(self, item):
        if item.user_url:
            return '<a href="%s">%s</a></b>: %s' % (item.user_url,
                                                    item.user_name,
                                                    item.comment)
        else:
            return '<b>%s</b>: %s' % (item.user_name, item.comment)

    def item_link(self, item):
        return item.content_object.get_absolute_url()

    def item_pubdate(self, item):
        return item.submit_date
