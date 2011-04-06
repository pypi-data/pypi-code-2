from zope.interface import implements
from zope import schema
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from fourdigits.portlet.twitter import \
FourdigitsPortletTwitterMessageFactory as _
from fourdigits.portlet.twitter import twitter
import re
from urllib2 import URLError
from time import time

# Match and capture urls
urlsRegexp = re.compile(r"""
    (
    # Protocol
    http://
    # Alphanumeric, dash, slash or dot
    [A-Za-z0-9\-/?=&.]*
    # Don't end with a dot
    [A-Za-z0-9\-/]+
    )
    """, re.VERBOSE)

# Match and capture #tags
hashRegexp = re.compile(r"""
    # Hash at start of string or after space, followed by at least one
    # alphanumeric or dash
    (?:^|(?<=\s))\#([A-Za-z0-9\-]+)
    """, re.VERBOSE)

# Match and capture @names
atRegexp = re.compile(r"""
    # At symbol at start of string or after space, followed by at least one
    # alphanumeric or dash
    (?:^|(?<=\s))@([A-Za-z0-9\-]+)
    """, re.VERBOSE)

# Match and capture email address
emailRegexp = re.compile(r"""
    # Email at start of string or after space
    (?:^|(?<=\s))([A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4})\b
    """, re.VERBOSE | re.IGNORECASE)


def _twitter_cachekey(method, self):
    """A cachekey of 5 minutes"""
    return time() // (60 * 5)


def expand_tweet(str):
    """This method takes a string, parses it for URLs, hashtags and mentions
       and returns a hyperlinked string."""

    str = re.sub(urlsRegexp, '<a href="\g<1>">\g<1></a>', str)
    str = re.sub(hashRegexp,
                 '<a href="http://twitter.com/search?q=%23\g<1>">#\g<1></a>',
                 str)
    str = re.sub(atRegexp,
                 '<a href="http://twitter.com/\g<1>">@\g<1></a>',
                 str)
    str = re.sub(emailRegexp,
                 '<a href="mailto:\g<1>">\g<1></a>',
                 str)
    return str


class IFourdigitsPortletTwitter(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    name = schema.TextLine(
        title=_(u"Title"), description=_(u"The title of the portlet"))

    username = schema.TextLine(
        title=_(u"Username"),
        description=_(u"The tweets of this user will be shown"),
        required=False,)

    includerts = schema.Bool(
        title=_(u"Include retweets"),
        description=_(u"Include retweets of the user's account?"),
        required=False,
        default=True,)

    search = schema.Text(
        title=_(u"Search"),
        description=_(u"The tweets containing this text will be shown\
                      enter one per line, hashtags are allowed"),
        required=False,)

    filtertext = schema.Text(
        title=_(u"Filtertext"),
        description=_(u"If a message containes (curse) words in the filtertext\
                      it wont be shown, one per line"),
        required=False,)

    userdisplay = schema.Int(
        title=_(u'Number of items to display based on the username'),
        description=_(u'How many items to list based on the username.'),
        required=False,
        default=5,
    )
    searchdisplay = schema.Int(
        title=_(u'Number of items to display based on the searchtext'),
        description=_(u'How many items to list based on the searchtext.'),
        required=False,
        default=5,
    )
    searchlimit = schema.Int(
        title=_(u'Number of items to search for, defaults to 40'),
        description=_(u'Number of items to search for, defaults to 40'),
        required=True,
        default=40,
    )

    language = schema.Text(
        title=_("Languagefilter"),
        description=_("Language ISO code for the tweets (e.g.: en, nl, fr), \
                      if you like to filter on language\
                      one per line"),
        required=False,
    )
    userpictures = schema.Bool(
        title=_("Show user pictures?"),
        description=_("Should the portlet show the twitter user pictures?"),
        default=True,
    )


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IFourdigitsPortletTwitter)
    includerts = True

    def __init__(self, name=u"", username=u"", search=u"", filtertext="",
                 userdisplay=5, searchdisplay=5, searchlimit=40,
                 language="", userpictures=False, includerts=True):
        self.name = name
        self.username = username
        self.search = search
        self.filtertext = filtertext
        self.userdisplay = userdisplay
        self.searchdisplay = searchdisplay
        self.searchlimit = searchlimit
        self.language = language
        self.userpictures = userpictures
        self.includerts = includerts

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return "fourdigits.portlet.twitter"


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('fourdigitsportlettwitter.pt')

    twapi = twitter.Api()

    @property
    def title(self):
        return self.data.name or _(u"Tweets")

    @property
    def available(self):
        return True

    def expand(self, str):
        return expand_tweet(str)

    def twittermessages(self):
        """Twitter messages"""
        return self.getTweets()

    def getTweetsOfUser(self, username, userpictures, includerts):
        """Return the tweets of a certain user"""
        try:

            tweets = self.twapi.GetUserTimeline(username,
                                                includerts=includerts)
        except URLError:
            tweets = []
        return tweets

    def getTweetsBySearch(self, searchterms, searchlimit, language):
        """Return tweets based on a search query"""
        searchterms = searchterms.encode('utf-8')
        searchterms = searchterms.split('\n')
        for searchterm in searchterms:
            # get tweets per searchterm
            try:
                tweets = self.twapi.GetSearch(term=searchterm,
                                              per_page=searchlimit,
                                              lang=language)
            except:
                tweets = []
        return tweets

    def getTweets(self):
        """get the tweets and filter them"""
        username = self.data.username
        searchterms = self.data.search
        userdisplay = self.data.userdisplay
        searchdisplay = self.data.searchdisplay
        searchlimit = self.data.searchlimit
        filtertext = self.data.filtertext
        languages = self.data.language
        userpictures = self.data.userpictures
        includerts = self.data.includerts

        results = []
        tweets = []

        # get tweets of username
        if username:
            tweets = self.getTweetsOfUser(username,
                                          userpictures,
                                          includerts)
        tweets = tweets[:userdisplay]

        searchresults = []
        # get tweets based on search
        if searchterms:
            if languages:
                languages = languages.split('\n')
                for lang in languages:
                    lang = str(lang.encode('utf-8'))
                    searchresults += self.getTweetsBySearch(searchterms,
                                                            searchlimit,
                                                            language=lang)
            else:
                searchresults += self.getTweetsBySearch(searchterms,
                                                        searchlimit,
                                                        language="")
            # Only add tweets which are not already in the user results
            filtered_results = [tweet for tweet
                                      in searchresults
                                      if not tweet in tweets]
            tweets += filtered_results[:searchdisplay]

        if filtertext:
            filtertext = filtertext.lower()
            filterlist = filtertext.split('\n')

        # add picture and filter out tweets based on the filterlist
        for tweet in tweets:
            tweet.username = tweet.user.GetScreenName()
            picture = tweet.user.GetProfileImageUrl()
            tweet.author_url = 'http://twitter.com/%s' % tweet.username
            if userpictures:
                tweet.picture = picture

            if filtertext:
                text = tweet.text.lower()
                if not [1 for x in filterlist if x in text]:
                    results.append(tweet)
            else:
                results.append(tweet)
        tweets = results

        # sort the tweets
        tweets.sort(key=lambda tweet: tweet.GetCreatedAtInSeconds())
        tweets.reverse()

        return tweets


class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IFourdigitsPortletTwitter)

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IFourdigitsPortletTwitter)
