import datetime

from django.db import models
from django.db.models.query import QuerySet
from django.contrib.auth.models import User

class EntryQuerySet(QuerySet):
    """
    Adds several convenience methods to the ``QuerySet`` returned by the
    ``Entry`` manager so that chained method calls will preserve these
    methods.
    
    """

    def published(self):
        """
        Return all published entries.

        """
        return self.filter(
            status__exact = self.model.PUBLISH_STATUS,
            publish__lte = datetime.datetime.now(),
        )

    def drafts(self):
        """
        Return all draft entries.

        """
        return self.filter(
            status__exact = self.model.DRAFT_STATUS
        )

    def removed(self):
        """
        Returns all removed entries.
        
        """
        return self.filter(
            status__exact = self.model.REMOVED_STATUS
        )

    def on_date(self, date):
        """
        Returns the set of all entries published for the given
        date object.

        """
        next = date + datetime.timedelta(days = 1)
        return self.filter(
            publish__gt = date,
            publish__lt = next
        )

    def by_author(self, author):
        """
        Returns the set of all entries where the ``author`` is the given
        ``django.contrib.auth.models.User``.

        """
        return self.filter(
            author = author
        )

class EntryManager(models.Manager):
    """
    A manager for ``Entry`` objects that returns ``EntryQuerySet``s and
    allows the use of ``EntryQuerySet`` methods.

    """
    def get_query_set(self):
        return EntryQuerySet(self.model)

    def __getattr__(self, name):
        return getattr(self.get_query_set(), name)
