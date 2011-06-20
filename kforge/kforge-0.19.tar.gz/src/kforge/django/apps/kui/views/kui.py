from kforge.django.apps.kui.views.base import KforgeView
from kforge.dictionarywords import SYSTEM_SERVICE_NAME
from kforge.dictionarywords import FEED_LENGTH
from kforge.dictionarywords import FEED_SUMMARY_LENGTH
import kforge.command
import kforge.url
from dm.webkit import HttpResponse

class WelcomeView(KforgeView):

    templatePath = 'index'
    minorNavigationItem = '/'

    def __init__(self, **kwds):
        super(WelcomeView, self).__init__(**kwds)

    def setMinorNavigationItems(self):
        self.minorNavigation = [
            {'title': 'Welcome', 'url': '/'},
        ]
        if self.session:
            self.minorNavigation.append(
                {'title': 'Log out',   'url': '/logout/'}
            )
            self.minorNavigation.append(
                {'title': 'Join project',       'url': '/project/'}
            )
        else:
            self.minorNavigation.append(
                {'title': 'Log in',      'url': '/login/'},
            )
            self.minorNavigation.append(
                {'title': 'Join',      'url': '/person/create/'},
            )

    def canAccess(self):
        return self.canReadSystem()

    def setContext(self, **kwds):
        super(WelcomeView, self).setContext(**kwds)
        projects = self.registry.projects
        projectCount = len(projects)
        persons = self.registry.persons
        personCount = len(persons)
        self.context.update({
            'projectCount' : projectCount,
            'personCount'  : personCount,
            'feedUrl' : kforge.url.UrlScheme().url_for('feed') + '/',
            'feedEntries' : self.getFeedSummary()
        })

    # Todo: Limit by time? Add parameters.
    def getFeedSummary(self):
        feedSummaryLength = int(self.dictionary[FEED_SUMMARY_LENGTH])
        return self.registry.feedentries.listMax(feedSummaryLength)


class FeedView(KforgeView):

    templatePath = 'feed'

    def getResponse(self):
        self.content = self.getFeedContent()
        self.response = HttpResponse(self.content)
        #self.response.headers['Content-Type'] = 'text/html'
        return self.response

    def getFeedContent(self):
        from django.utils.feedgenerator import Atom1Feed
        from kforge.url import UrlScheme
        atomFeed = Atom1Feed(
            title='%s Recent Changes' % self.dictionary[SYSTEM_SERVICE_NAME],
            link=UrlScheme().url_for('home'),
            description='Entries are generated from project feeds.',
        )
        feedLength = int(self.dictionary[FEED_LENGTH])
        for entry in self.registry.feedentries.listMax(feedLength):
            atomFeed.add_item(
                title=entry.title,
                link=entry.link,
                description=entry.summary,
                unique_id=entry.uid,
            )
        return atomFeed.writeString('utf-8')


class PageNotFoundView(WelcomeView):

    templatePath = 'pageNotFound'

    def getResponse(self):
        return self.getNotFoundResponse()


class AccessControlView(KforgeView):

    templatePath = 'accessDenied'
    minorNavigationItem = ''

    def __init__(self, deniedPath='', **kwds):
        super(AccessControlView, self).__init__(**kwds)
        if self.request.GET:
            params = self.request.GET.copy()
            self.deniedPath = params.get('returnPath', '') # Todo: This supports this mod_handlers, but name needs to be fixed.
        else:
            self.deniedPath = deniedPath

    def setMinorNavigationItems(self):
        self.minorNavigation = [
            {'title': 'Welcome', 'url': '/'},
        ]
        if self.session:
            self.minorNavigation.append(
                {'title': 'Log out',   'url': '/logout/'}
            )
            self.minorNavigation.append(
                {'title': 'Join project',       'url': '/project/'}
            )
        else:
            self.minorNavigation.append(
                {'title': 'Log in',      'url': '/login/'},
            )
            self.minorNavigation.append(
                {'title': 'Register',      'url': '/person/create/'},
            )
    
    def canAccess(self):
        return True
        #return self.canReadSystem()
        
    def setContext(self, **kwds):
        super(AccessControlView, self).setContext(**kwds)
        self.context.update({
            'deniedPath'  : self.deniedPath,
        })


def welcome(request):
    view = WelcomeView(request=request)
    return view.getResponse()

def feed(request):
    view = FeedView(request=request)
    return view.getResponse()

def pageNotFound(request):
    view = PageNotFoundView(request=request)
    return view.getResponse()

def accessDenied(request, deniedPath):
    view = AccessControlView(request=request, deniedPath=deniedPath)
    return view.getResponse()


