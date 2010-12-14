#from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from AccessControl.SecurityManagement import getSecurityManager
from plone.session.plugins.session import SessionPlugin

class SessionRefreshViewlet(ViewletBase):
    #index = ViewPageTemplateFile('session_refresh.pt')

    def render(self):
        user = getSecurityManager().getUser()
        try:
            session = user._getPAS().session
        except AttributeError:
            # Not our user
            return ""
        if not isinstance(session, SessionPlugin):
            return ""
        if session.refresh_interval < 0:
            return ""
        imgsrc = "%s/refresh?type=gif" % session.absolute_url()
        url = "%s/refresh?type=js" % session.absolute_url()
        interval = 10
        #import pdb; pdb.set_trace()
        return """<span class="session-refresh">
        <script type="text/javascript">var still_logged_in = true;</script>
        <script type="text/javascript" src="%s" id="session-refresh-1-seconds-%d"></script>
        <noscript><img src="%s" style="position:fixed;top:0;left:0;" /></noscript></span>
        """ % (url, interval, imgsrc)
