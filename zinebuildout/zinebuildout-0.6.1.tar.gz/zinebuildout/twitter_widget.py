from werkzeug.contrib.cache import SimpleCache
from zine.application import get_application
from zine.widgets import Widget, all_widgets
import datetime
import os
import re
import twitter
import zinebuildout

cache = SimpleCache()
twitter_api = twitter.Api()

class Twitter(Widget):
    """widget to display your latests tweets
    """
    name = 'tweets'
    template = 'tweets.html'
    tweets = None

    def __init__(self, user, number, show_title=True):
        self.user = user
        here = os.path.dirname(zinebuildout.__file__)
        get_application()._template_searchpath.append(here)
        self.number = number
        self.show_title = show_title
        self.tweets = cache.get(self.name)
        if self.tweets is None:
            try:
                self.tweets = twitter_api.GetUserTimeline(user)[:number]
            except Exception, error:
                self.tweets = []
                print 'Could not retrieve the user timeline: %s' % error
            for t in self.tweets:
                t.text = text2html(t.text)
            cache.set(self.name, self.tweets, timeout=60*10)


all_widgets.append(Twitter)


link_regexp = re.compile(r"((http|ftp)://[^ ]+)")
search_regexp = re.compile(r"#(\w+)")
user_regexp = re.compile(r"@(\w+)")

def text2html(text):
    text = link_regexp.sub(r'<a target="_blank" href="\1">\1</a>', text)
    text = search_regexp.sub(r'<a target="_blank" href="http://twitter.com/search?q=%23\1">#\1</a>', text)
    text = user_regexp.sub(r'<a target="_blank" href="http://twitter.com/\1">@\1</a>', text)
    return text

