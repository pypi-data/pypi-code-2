from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.contrib.syndication.feeds import Feed
from django.utils.feedgenerator import Atom1Feed, get_tag_uri
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse, NoReverseMatch
from django import get_version as get_django_version

from birdland.models import Entry
from birdland.conf import settings
from birdland import get_version

if settings.TAGGING_ENABLED:
    from tagging.models import Tag, TaggedItem

published_entries = Entry.objects.published()
blog_name = settings.BLOG_NAME

class BirdlandFeed(Feed):
    """
    A base feed class which supplies common attributes for all feeds.
    """
    generator = u'birdland %s / django %s' % (get_version(), get_django_version())
    title = blog_name
    link = '/blog/'

    def item_pubdate(self, item):
        return item.publish

    def item_author_name(self, item):
        return item.author.get_full_name() or item.author.username

    def item_guid(self, item):
        return get_tag_uri(self.item_link(item), self.item_pubdate(item))


class LatestEntriesFeed(BirdlandFeed):
    """
    A feed of the latest published entries.
    """
    description = _(u'Latest blog entries on %s') % (blog_name)
    title =  _(u'%s latest') % BirdlandFeed.title

    def items(self):
        return published_entries.all()[:settings.NUM_ENTRIES_IN_FEEDS]

class LatestEntriesAtomFeed(LatestEntriesFeed):
    feed_type = Atom1Feed
    subtitle = LatestEntriesFeed.description


class LatestEntriesByAuthorFeed(BirdlandFeed):
    """
    A feed of the latest published entries for a given author.
    """
    def get_object(self, bits):
        if len(bits) != 1:
            raise ObjectDoesNotExist
        return User.objects.get(username=bits[0])

    def title(self, obj):
        return u'%s - %s' % (BirdlandFeed.title, obj.get_full_name() or obj.username)

    def description(self, obj):
        return _(u'Blog entries by %s') % (obj.get_full_name() or obj.username)

    def items(self, obj):
        return published_entries.by_author(obj)[:settings.NUM_ENTRIES_IN_FEEDS]

class LatestEntriesByAuthorAtomFeed(LatestEntriesByAuthorFeed):
    feed_type = Atom1Feed
    subtitle = LatestEntriesByAuthorFeed.description

# Feed dicts

rss_feeds = {
    'latest': LatestEntriesFeed,
    'author': LatestEntriesByAuthorFeed,
}

atom_feeds = {
    'latest': LatestEntriesAtomFeed,
    'author': LatestEntriesByAuthorAtomFeed,
}

# Optional tagging feeds

if settings.TAGGING_ENABLED:
    class LatestEntriesByTagFeed(BirdlandFeed):
        """
        A feed of the latest published entries associated with the given tag.
        """
        def get_object(self, bits):
            if len(bits) != 1:
                raise ObjectDoesNotExist
            return Tag.objects.get(name=bits[0])

        def title(self, obj):
            return u'%s - %s' % (BirdlandFeed.title, obj.name)

        def description(self, obj):
            return _(u'Latest blog entries tagged with %s') % obj.name

        def items(self, obj):
            return TaggedItem.objects.get_by_model(published_entries.filter(), obj)[:settings.NUM_ENTRIES_IN_FEEDS]

    class LatestEntriesByTagAtomFeed(LatestEntriesByTagFeed):
        feed_type = Atom1Feed
        subtitle = LatestEntriesByTagFeed.description
    
    # Update feed dicts
    rss_feeds['tag'] = LatestEntriesByTagFeed
    atom_feeds['tag'] = LatestEntriesByTagAtomFeed

