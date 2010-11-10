from Acquisition import aq_inner

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _p

from Products.statusmessages.interfaces import IStatusMessage

from raptus.article.core import RaptusArticleMessageFactory as _
from raptus.article.table.interfaces import IDefinitions
from raptus.article.table.utils import parseColumn

class Configlet(BrowserView):
    """ Manage table definitions
    """
    template = ViewPageTemplateFile('configlet.pt')

    def __call__(self):
        self.request.set('disable_border', True)

        self._definitions = IDefinitions(self.context)

        if self.request.form.has_key('raptus_article_table_save'):
            self.setProperties()

        self.definitions = []
        raw_definitions = self._definitions.getAvailableDefinitions().values()
        for definition in raw_definitions:
            definition['columns'] = '\n'.join([':'.join(filter(lambda v: bool(v), [c['name'], c['title'], c['type'], ':'.join(c.get('flags', [])),])) for c in definition['columns']])
            self.definitions.append(definition)
        return self.template()

    def setProperties(self):
        context = aq_inner(self.context)
        new = self.request.form.get('new_definition', None)
        error = 0
        if new and new['name']:
            try:
                self._definitions.addDefinition(new['name'], new['style'], [parseColumn(c) for c in new['columns'].split('\n')])
            except:
                error = _(u'Unable to parse the columns field of the definition to be added')
        modify = self.request.form.get('definitions', [])
        for definition in modify:
            if not definition['name'] == definition['origname'] or definition.has_key('delete'):
                self._definitions.removeDefinition(definition['origname'])
            if definition.has_key('delete'):
                continue
            try:
                self._definitions.addDefinition(definition['name'], definition['style'], [parseColumn(c) for c in definition['columns'].split('\n')])
            except:
                error = _(u'Unable to parse the columns field of one of the definitions to be modified')
        statusmessage = IStatusMessage(self.request)
        if error:
            statusmessage.addStatusMessage(error, 'error')
        else:
            statusmessage.addStatusMessage(_p(u'Changes saved.'), 'info')
