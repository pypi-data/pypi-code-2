##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id: __init__.py 97 2007-03-29 22:58:27Z rineichen $
"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.component
import zope.schema
from zope.traversing.browser import absoluteURL
from zope.exceptions.interfaces import DuplicationError

from z3c.template.template import getPageTemplate
from z3c.template.template import getLayoutTemplate
from z3c.template.interfaces import ILayoutTemplate
from z3c.pagelet import browser
from z3c.form.interfaces import IWidgets
from z3c.form import field
from z3c.form import button
from z3c.formui import form
from z3c.formui import layout
from z3c.sampledata.interfaces import ISampleManager

from zam.api.i18n import MessageFactory as _
from zamplugin.sampledata import interfaces



class SampleData(browser.BrowserPagelet):
    """Sampledata managers."""

    zope.interface.implements(interfaces.ISampleDataPage)

    def managers(self):
        return [name for name, util in 
                zope.component.getUtilitiesFor(ISampleManager)]

    def update(self):
        if 'manager' in self.request:
            managerName = self.request['manager']
            self.request.response.redirect(
                absoluteURL(self.context, self.request)+
                '/@@generatesample.html?manager="%s"'%(managerName))


class IGeneratorSchema(zope.interface.Interface):
    """Schema for the minimal generator parameters"""

    seed = zope.schema.TextLine(
            title = _('Seed'),
            description =  _('A seed for the random generator'),
            default = u'sample',
            required=False,
            )


class GenerateSample(form.Form):
    """Edit all generator parameters for a given manager"""

    zope.interface.implements(interfaces.ISampleDataPage)

    subforms = []
    workDone = False

    @property
    def showGenerateButton(self):
        if self.request.get('manager', None) is None:
            return False
        return True

    def updateWidgets(self):
        self.widgets = zope.component.getMultiAdapter(
            (self, self.request, self.getContent()), IWidgets)
        self.widgets.ignoreContext = True
        self.widgets.update()

    def update(self):
        managerName = self.request.get('manager', None)
        if managerName is not None:
            self.subforms = []
            manager = zope.component.getUtility(ISampleManager, name=managerName)
            plugins = manager.orderedPlugins()
            self.fields = field.Fields()
            subform = Generator(context=self.context,
                                request=self.request,
                                schema=IGeneratorSchema,
                                prefix='generator')
            subform.fields = field.Fields(IGeneratorSchema)
            self.subforms.append(subform)
            for plugin in plugins:
                if plugin.generator.schema is None:
                    continue
                subform = Generator(context=self.context,
                                    request=self.request,
                                    plugin=plugin.generator,
                                    prefix=str(plugin.name))
                subform.fields = field.Fields(plugin.generator.schema)
                self.subforms.append(subform)
        super(GenerateSample, self).update()

    @button.buttonAndHandler(u'Generate',
        condition=lambda form: form.showGenerateButton)
    def handleGenerate(self, action):
        managerName = self.request['manager']
        manager = zope.component.getUtility(ISampleManager, name=managerName)
        generatorData = {}
        for subform in self.subforms:
            subform.update()
            formData = {}
            data, errors = subform.widgets.extract()
            generatorData[subform.prefix] = data
        gen = generatorData.get('generator', {})
        seed = gen.get('seed', None)
        try:
            self.workedOn = manager.generate(context=self.context, 
                param=generatorData, seed=seed)
            self.workDone = True
        except DuplicationError:
            self.status = _('Duplidated item')

    def manager(self):
        return self.request.get('manager', None)


class Generator(form.Form):
    """An editor for a single generator"""

    template = getPageTemplate('subform')

    def updateWidgets(self):
        self.widgets = zope.component.getMultiAdapter(
            (self, self.request, self.getContent()), IWidgets)
        self.widgets.ignoreContext = True
        self.widgets.update()

    def __init__(self, context, request, plugin=None, schema=None, prefix=''):
        self.plugin = plugin
        self.schema = schema
        self.prefix = str(prefix) # must be a string in z3c.form
        super(Generator, self).__init__(context, request)

    def render(self):
        return self.template()

    def __call__(self):
        self.update()
        return self.render()