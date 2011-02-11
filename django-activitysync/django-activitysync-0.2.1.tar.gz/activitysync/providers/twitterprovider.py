from django.conf import settings
from activitysync.providers import ActivityProvider, ActivityInfo

import time
import datetime
import twitter as TwitterLibrary

class TwitterUserProvider(ActivityProvider):
    """
    Provider for accessing Twitter status updates for one user.
    """
    
    def get_activity(self):
        item_list = []

        print 'Attempting to obtain Twitter items'
        api = TwitterLibrary.Api()
        username = settings.ACTIVITYSYNC_SETTINGS['TWITTER_USERNAME']
        print ' Username: %s' % username
        statuses = api.GetUserTimeline(username, count=50)

        for status in statuses:
            title = status.text
            guid = "twitter:%s" % status.id
            link = "http://twitter.com/%s/statuses/%s" % (status.user.screen_name, status.id)
            author = status.user.name or ''
                
            date_published = datetime.datetime.fromtimestamp(status.created_at_in_seconds)
                 
            # Don't show @replies
            if not status.in_reply_to_user_id:
                activity_info = ActivityInfo(title=title, link=link, pub_date=date_published, guid=guid, username=username, author=author)
                item_list.append(activity_info)

        return item_list


    def name(self):
        return 'Twitter'

    def prefix(self):
        return ''

    def link(self):
        return ('http://twitter.com/%s' %
            settings.ACTIVITYSYNC_SETTINGS['TWITTER_USERNAME'])

    def sourceid(self):
        return 'twitter'


class TwitterSearchProvider(ActivityProvider):
    """
    Provider for accessing Twitter status updates from a search query.
    """

    def get_activity(self):
        item_list = []

        print 'Attempting to obtain Twitter items'
        api = TwitterLibrary.Api()
        query = settings.ACTIVITYSYNC_SETTINGS['TWITTER_SEARCHTERM']
        print ' Search term: %s' % query
        statuses = api.GetSearch(term=query, per_page=50)

        for status in statuses:
            title = status.text
            guid = "twitter:%s" % status.id
            link = "http://twitter.com/%s/statuses/%s" % (status.user.screen_name, status.id)
            author = status.user.name or ''
            username = status.user.screen_name

            date_published = datetime.datetime.fromtimestamp(status.created_at_in_seconds)

            activity_info = ActivityInfo(title=title, link=link, pub_date=date_published, guid=guid, username=username, author=author)
            item_list.append(activity_info)

        return item_list


    def name(self):
        return 'Twitter'

    def prefix(self):
        return ''

    def link(self):
        return ('http://twitter.com/search?q=%s' %
            settings.ACTIVITYSYNC_SETTINGS['TWITTER_SEARCHTERM'])

    def sourceid(self):
        return 'twitter'

