from zope.interface import implements, Interface
from zope.component import getUtility

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

from plone.registry.interfaces import IRegistry

from collective.taghelper import taghelperMessageFactory as _
from collective.taghelper.utilities import get_yql_subjects
from collective.taghelper.utilities import get_calais_subjects
from collective.taghelper.utilities import get_silcc_subjects
from collective.taghelper.utilities import get_ttn_subjects
from collective.taghelper.utilities import get_ttn_subjects_remote
from collective.taghelper.interfaces import ITagHelperSettingsSchema


class IExtractedTermsView(Interface):
    """
    ExtractedTerms view interface
    """




class ExtractedTermsView(BrowserView):
    """
    ExtractedTerms browser view
    """
    implements(IExtractedTermsView)

    template = ViewPageTemplateFile('extractedtermsview.pt')
    use_remote_url = False

    def __init__(self, context, request):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ITagHelperSettingsSchema)
        self.use_remote_url = settings.use_remote_url
        self.context = context
        self.request = request
        if self.context.portal_type == 'File':
            self.url = self.request.URL1 +'/filehtmlpreview_view'
        elif hasattr(self.context, 'getRemoteUrl'):
            if self.use_remote_url and self.context.getRemoteUrl():
                self.url = self.context.getRemoteUrl()
            else:
                self.url = self.request.URL1 +'?ajax_load=1'
        if not self.url:
            self.url = self.request.URL1 +'?ajax_load=1'
        self.text = self._get_text()

    def _get_text(self):
        if hasattr(self.context, 'SearchableText'):
            return self.context.SearchableText()
        else:
            return ''


    def yahoo_terms(self):
        return get_yql_subjects(self.url)

    def calais_terms(self):
        return get_calais_subjects(self.text, self.context.UID())

    def ttn_terms(self):
        if self.use_remote_url:
            return get_ttn_subjects_remote(self.url)
        else:
            return get_ttn_subjects(self.text)


    def silcc_terms(self):
        text = self.context.Title() + '. ' + self.context.Description()
        return get_silcc_subjects(text)

    def __call__(self):
        form = self.request.form
        if form.has_key('form.button.save'):
            keywords = list(self.context.Subject())
            keywords = keywords + form.get('subject', [])
            keywords=list(set(keywords))
            self.context.setSubject(keywords)
            self.request.response.redirect(self.context.absolute_url() + '/edit')
            return ''
        elif form.has_key('form.button.cancel'):
            self.request.response.redirect(self.context.absolute_url() + '/view')
            return ''
        return self.template()
