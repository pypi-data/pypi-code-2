## ControlPanel form for the UITool

from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from plone.app.controlpanel.form import ControlPanelForm
from plone.fieldsets.fieldsets import FormFieldsets
from zope.app.form.browser import DisplayWidget
from zope.i18n import translate

from zope.component import adapts
from zope.interface import implements

from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFCore.utils import getToolByName

from ..tool.tool import IUITool, IUIToolSettings, IUIToolTheme
from zettwerk.ui import messageFactory as _
from ..filesystem import isAvailable, DOWNLOAD_HOME

class UIControlPanelAdapter(SchemaAdapterBase):
    """ Adapter for the interface schema fields """

    adapts(IPloneSiteRoot)
    implements(IUITool)

    def __init__(self, context):
        super(UIControlPanelAdapter, self).__init__(context)
        self.portal = context
        ui_tool = getToolByName(self.portal, 'portal_ui_tool')
        self.context = ui_tool

settings = FormFieldsets(IUIToolSettings)
settings.id = 'settings'
settings.label = _(u"Settings")

theme = FormFieldsets(IUIToolTheme)
theme.id = 'theme'
theme.label = _(u"Theme")
theme.description = _(u"theme_description_text", """New themes gets
downloaded to your server's filesystem. The target directory for storing them
is given below. If the folder is not available - downloading is disabled. But
this tool can create the directory. If you want to integrate a custom theme
from themeroller do not use the themeroller's download link - that will
download the theme to your local machine. You must use the link given
below.""")


class ThemerollerDisplayWidget(DisplayWidget):
    """ Display the themeroller link """

    def __call__(self):
        tool = self.context.context
        if tool.theme and tool.themeHashes:
            hash = tool.themeHashes.get(tool.theme, '')
            themeroller = u"javascript:callThemeroller('%s')" % (hash)
        else:
            themeroller = u"javascript:callThemeroller()"

        open_link = '<a href="%s">%s</a>' % (themeroller,
                                             translate(_(u"Open jquery.ui themeroller (only firefox)"),
                                                       domain="zettwerk.ui",
                                                       context=self.request))

        name_help = translate(_(u"Name of the new theme"),
                              domain='zettwerk.ui',
                              context=self.request)
        name_input = u'<input type="text" value="" />'
        add_link_text = translate(_(u'Add theme to available themes'),
                                  domain="zettwerk.ui",
                                  context=self.request)
        add_link = u'''<a style="display: none;" id="ploneDownloadTheme"
href="javascript:ploneDownloadTheme()">%s</a>''' % (add_link_text)
        name_div = u'<div id="themename">%s %s %s</div>' % (name_help,
                                                            name_input,
                                                            add_link)
        create_help = translate(_(u"Create download directory at: "),
                                domain="zettwerk.ui",
                                context=self.request)
        create_text = "%s %s" % (create_help, DOWNLOAD_HOME)
        create_dl = u'''<br /><br /><a href="javascript:createDLDirectory()">
%s</a>''' % (create_text)

        if isAvailable():
            return u'%s %s' % (open_link, name_div)
        else:
            return u'%s %s' % (open_link, create_dl)

class UIControlPanel(ControlPanelForm):
    """ Build the ControlPanel form. """

    form_fields = FormFieldsets(settings, theme)

    form_fields['themeroller'].custom_widget = ThemerollerDisplayWidget
    form_fields['themeroller'].for_display = True

    label = _(u"Zettwerk UI Themer")
    description = _('cp_description', u'''The settings are for enable or disable theming of
elements. With the theme link, new themes are created or the current used one
can be changed.''')
