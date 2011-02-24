from provide.django.apps.eui.views.base import ProvideView

class WelcomeView(ProvideView):

    templatePath = 'welcome'
    minorNavigationItem = '/'

    def __init__(self, **kwds):
        super(WelcomeView, self).__init__(**kwds)

    def setMinorNavigationItems(self):
        self.minorNavigation = [
            {'title': 'Welcome', 'url': '/'},
        ]
        if self.session:
            self.minorNavigation.append(
                {'title': 'Schedule',       'url': '/schedule/'}
            )
            self.minorNavigation.append(
                {'title': 'Report',       'url': '/report/'}
            )
        else:
            self.minorNavigation.append(
                {'title': 'Log in',      'url': '/login/'},
            )

    def canAccess(self):
        return self.canReadSystem()

    def setContext(self, **kwds):
        super(WelcomeView, self).setContext(**kwds)
        self.context.update({
        })


class PageNotFoundView(WelcomeView):

    templatePath = 'pageNotFound'

    def setMinorNavigationItems(self):
        self.minorNavigation = [
            {'title': 'Welcome', 'url': '/'},
        ]
        if self.session:
            self.minorNavigation.append(
                {'title': 'Help',       'url': '/help/'}
            )
        else:
            self.minorNavigation.append(
                {'title': 'Log in',      'url': '/login/'},
            )

class AccessControlView(ProvideView):

    templatePath = 'accessDenied'
    minorNavigationItem = '/accessDenied/'

    def __init__(self, deniedPath='', **kwds):
        super(AccessControlView, self).__init__(**kwds)
        self.deniedPath = deniedPath

    def setMinorNavigationItems(self):
        self.minorNavigation = [
            {'title': 'Sorry', 'url': '/accessDenied/'},
        ]
    
    def canAccess(self):
        return self.canReadSystem()
        
    def setContext(self, **kwds):
        super(AccessControlView, self).setContext(**kwds)
        self.context.update({
            'deniedPath'  : self.deniedPath,
        })


class UserAccountView(ProvideView):

    majorNavigationItem = '/persons/home/'

    def canAccess(self):
        return True

    def takeAction(self):
        if self.session:
            redirectPath = '/persons/%s/' % self.session.person.name
        else:
            redirectPath = '/login/'
        self.setRedirect(redirectPath)

    def setMinorNavigationItems(self):
        self.minorNavigation = [
            {'title': 'Welcome', 'url': '/'},
        ]
        if self.session:
            self.minorNavigation.append(
                {'title': 'Log out',     'url': '/logout/'}
            )
        else:
            self.minorNavigation.append(
                {'title': 'Log in',      'url': '/login/'},
            )


class RegistryWelcomeView(WelcomeView):

    templatePath = 'registry'
    majorNavigationItem = '/registry/'
    minorNavigationItem = '/registry/'

    def setMinorNavigationItems(self):
        self.minorNavigation = [
            {'title': 'Welcome', 'url': '/registry/'},
        ]
        self.minorNavigation.append(
            {'title': 'Scanners', 'url': '/scanners/'}
        )
        self.minorNavigation.append(
            {'title': 'Researchers', 'url': '/researchers/'}
        )
        self.minorNavigation.append(
            {'title': 'Radiographers', 'url': '/radiographers/'}
        )
        self.minorNavigation.append(
            {'title': 'Volunteers', 'url': '/volunteers/'}
        )
        self.minorNavigation.append(
            {'title': 'Approvals', 'url': '/approvals/'}
        )
        self.minorNavigation.append(
            {'title': 'Studies', 'url': '/studies/'}
        )
        self.minorNavigation.append(
            {'title': 'Earmark templates', 'url': '/weekEarmarkTemplates/'}
        )


def welcome(request):
    view = WelcomeView(request=request)
    return view.getResponse()

def registry(request):
    view = RegistryWelcomeView(request=request)
    return view.getResponse()

def pageNotFound(request):
    view = PageNotFoundView(request=request)
    return view.getResponse()

def accessDenied(request, deniedPath):
    view = AccessControlView(request=request, deniedPath=deniedPath)
    return view.getResponse()

def user(request):
    view = UserAccountView(request=request)
    return view.getResponse()
 
