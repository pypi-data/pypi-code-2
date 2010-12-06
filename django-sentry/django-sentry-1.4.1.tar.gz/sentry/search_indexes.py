import datetime
from haystack.indexes import *
from haystack import site
from sentry.models import GroupedMessage


class GroupedMessageIndex(SearchIndex):
    message = CharField(document=True, use_template=True)
    last_seen = DateTimeField(model_attr='last_seen')

    def get_queryset(self):
        """Used when the entire index for model is updated."""
        return GroupedMessage.objects.all()

site.register(GroupedMessage, GroupedMessageIndex)