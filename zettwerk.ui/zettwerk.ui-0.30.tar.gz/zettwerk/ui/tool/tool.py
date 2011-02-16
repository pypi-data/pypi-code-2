from Products.CMFCore.utils import UniqueObject, getToolByName
from OFS.SimpleItem import SimpleItem
from persistent.mapping import PersistentMapping

from zope.interface import Interface
from zope.interface import implements
from zope import schema
from zope.i18n import translate

from zettwerk.ui import messageFactory as _
from css import FORMS, STATUS_MESSAGE, TABS, FOOTER, PERSONAL_TOOL

import urllib2
from urllib import urlencode

from ..filesystem import extractZipFile, storeBinaryFile, \
    createDownloadFolder, getDirectoriesOfDownloadHome, \
    getThemeHashOfCustomCSS
from ..resources import registerResourceDirectory
from ..filesystem import DOWNLOAD_HOME

UI_DOWNLOAD_URL = 'http://jqueryui.com/download'

## a list of jquery.ui elements, needed for the url to download a new theme.
UI = """ui.core.js
ui.widget.js
ui.mouse.js
ui.position.js
ui.draggable.js
ui.droppable.js
ui.resizable.js
ui.selectable.js
ui.sortable.js
ui.accordion.js
ui.autocomplete.js
ui.button.js
ui.dialog.js
ui.slider.js
ui.tabs.js
ui.datepicker.js
ui.progressbar.js
effects.core.js
effects.blind.js
effects.bounce.js
effects.clip.js
effects.drop.js
effects.explode.js
effects.fold.js
effects.highlight.js
effects.pulsate.js
effects.scale.js
effects.shake.js
effects.slide.js
effects.transfer.js"""


class IUIToolTheme(Interface):
    """ UITool interface defining needed schema fields. """

    theme = schema.Choice(title=_(u"Theme"),
                          required=False,
                          vocabulary="zettwerk.ui.ListThemesVocabulary")


class IUIToolThemeroller(Interface):
    """ UITool interface for themeroller fields """

    themeroller = schema.TextLine(
        title=_("Themeroller")
        )

    download = schema.TextLine(
        title=_("Download"),
        required=False,
        description=_("Name of the theme to download.")
        )


class IUIToolSettings(Interface):
    """ UITool interface for setting fields """

    enableFonts = schema.Bool(
        title=_(u"Enable fonts styling"),
        description=_(u"Use jquery ui's font class for global font styling")
        )
    enableGlobalTabs = schema.Bool(
        title=_(u"Enable global-tabs styling"),
        description=_(u"Use jquery ui's tabs classes for global-tab " \
                          "styling (this do not use ui's tabs())")
        )
    enableDialogs = schema.Bool(
        title=_(u"Enable dialogs"),
        description=_(u"This applies dialog() to a.link-overlay links")
        )
    enableStatusMessage = schema.Bool(
        title=_(u"Enable status messages"),
        description=_(u"Use jquery ui's status message styling")
        )
    enablePersonalTool = schema.Bool(
        title=_(u"Enable personal-tool"),
        description=_(u"Use jquery ui's widget class for personal-tool " \
                          "styling")
        )
    enablePortlets = schema.Bool(
        title=_(u"Enable portelts styling"),
        description=_(u"Use jquery ui's tabs classes for portlet styling")
        )
    enableTabs = schema.Bool(
        title=_(u"Enable tabs styling"),
        description=_(u"Use jquery ui's tabs classes for tab styling " \
                          "(this do not use ui's tabs())")
        )
    enableEditBar = schema.Bool(
        title=_(u"Enable edit bar styling"),
        description=_(u"Use jquery ui's classes for edit bar styling")
        )
    enableForms = schema.Bool(
        title=_(u"Enable forms"),
        description=_(u"Use ui css classes for form elements")
        )
    enableFooter = schema.Bool(
        title=_(u"Enable footer styling"),
        description=_(u"Use jquery ui's classes for footer styling")
        )


class IUITool(IUIToolSettings, IUIToolTheme, IUIToolThemeroller):
    """ Mixin Interface """
    pass


class UITool(UniqueObject, SimpleItem):
    """ The UITool handles creation and loading of ui themes. """

    implements(IUITool)
    id = 'portal_ui_tool'

    ## implement the fields, given through the interfaces
    theme = ''
    download = ''
    themeroller = ''
    enableStatusMessage = True
    enableDialogs = True
    enableForms = True
    enablePersonalTool = True
    enableTabs = True
    enableGlobalTabs = True
    enablePortlets = True
    enableFooter = True
    enableEditBar = True
    enableFonts = True

    themeHashes = None

    def cp_js_translations(self):
        """ return some translated js strings """
        return u'var sorry_only_firefox = "%s";\n' \
            u'var nothing_themed = "%s";\n' \
            u'var name_missing = "%s";\n\n' % (
            translate(_(u"Sorry, due to security restrictions, this tool " \
                            u"only works in Firefox"),
                      domain='zettwerk.ui',
                      context=self.REQUEST),
            translate(_(u"Download name given but nothing themed - please " \
                            "use themeroller"),
                      domain='zettwerk.ui',
                      context=self.REQUEST),
            translate(_(u"You opened themeroller, but no download name is " \
                            u"given. Click ok to continue and ignore your " \
                            u"changes or click cancel to enter a name."),
                      domain='zettwerk.ui',
                      context=self.REQUEST))

    def js(self, *args):
        """ Generate the js, suitable for the given settings. """
        content_type_header = 'application/x-javascript;charset=UTF-8'
        self.REQUEST.RESPONSE.setHeader('content-type',
                                        content_type_header)

        result = [self.cp_js_translations(),
                  'jq(document).ready(function() {']

        if self.enableFonts:
            result.append('enableFonts();')
        if self.enableDialogs:
            result.append('enableDialogs();')
        if self.enableStatusMessage:
            result.append('enableStatusMessage();')
        if self.enableForms:
            result.append('enableForms();')
            result.append('forms_are_enabled = true;')
        if self.enablePersonalTool:
            result.append('enablePersonalTool();')
        if self.enableTabs:
            result.append('enableTabs();')
        if self.enableGlobalTabs:
            result.append('enableGlobalTabs();')
        if self.enablePortlets:
            result.append('enablePortlets();')
        if self.enableFooter:
            result.append('enableFooter();')
        if self.enableEditBar:
            result.append('enableEditBar();')

        result.append('removeRules();')
        result.append('});')
        return '\n'.join(result)

    ## css generation
    def css(self, *args):
        """ Generate the css rules, suitable for the given settings. """
        content_type_header = 'text/css;charset=UTF-8'
        self.REQUEST.RESPONSE.setHeader('content-type',
                                        content_type_header)
        result = ""

        if self.theme:
            resource_base = '++resource++zettwerk.ui.themes'
            result += '@import "%s/%s/jquery-ui-.custom.css";' % (
                resource_base,
                self.theme
                )

        if self.enableForms:
            result += FORMS
        if self.enableStatusMessage:
            result += STATUS_MESSAGE
        if self.enableTabs or self.enableGlobalTabs:
            result += TABS
        if self.enableFooter:
            result += FOOTER
        if self.enablePersonalTool:
            result += PERSONAL_TOOL
        return result

    def _redirectToCPView(self, msg=None):
        """ Just a redirect. """
        if msg is not None:
            utils = getToolByName(self, 'plone_utils')
            utils.addPortalMessage(msg)

        portal_url = getToolByName(self, 'portal_url')
        url = '%s/%s/@@ui-controlpanel' % (portal_url(),
                                           self.getId())
        self.REQUEST.RESPONSE.redirect(url)

    def _rebuildThemeHashes(self):
        """ For edit existing themes, the hash is needed. They are stored
        in self.themeHashes. The problem with this: by quick-reinstalling
        zettwerk.ui this attribute get None. Also, if new themes were
        copied 'by hand' (as described in the README for deploying) the
        themeHashes doesn't know the copied theme's hash. This method
        reads all available themes and the theme-custom.css file to rebuild
        the themeHashes attribute. Its called every time the control panel
        view is called. """
        if self.themeHashes is None:
            self.themeHashes = PersistentMapping()

        theme_dirs = getDirectoriesOfDownloadHome()
        for theme_dir in theme_dirs:
            theme_hash = getThemeHashOfCustomCSS(theme_dir)
            if theme_hash:
                self.themeHashes.update({theme_dir: theme_hash})

    def createDLDirectory(self):
        """ Create the storage and register the resource"""
        createDownloadFolder()
        registerResourceDirectory(name='zettwerk.ui.themes',
                                  directory=DOWNLOAD_HOME)
        self._redirectToCPView(_(u"Directory created"))

    def handleDownload(self, name, hash):
        """ Downsload a new theme, created by themeroller.

        @param name: string with the name of the new theme.
        @param hash: themeroller hast, with theme settings.
        """

        url = self._prepareUIDownloadUrl(hash)
        handler = urllib2.urlopen(url)
        content = handler.read()

        storeBinaryFile(name, content)
        self._enableNewTheme(name, hash)

    def _enableNewTheme(self, name, hash):
        """ Extract the downloaded theme and set it as current theme. """

        extractZipFile(name)
        if self.themeHashes is None:
            self.themeHashes = PersistentMapping()

        self.themeHashes.update({name: hash})
        self.theme = name

    def _prepareUIDownloadUrl(self, hash):
        """ Built the download url. """

        data = []
        data.append(('download', 'true'))
        for part in UI.split('\n'):
            part = part.strip()
            if part:
                data.append(('files[]', part))
        data.append(('theme', '?' + hash))
        data.append(('scope', ''))
        data.append(('t-name', 'custom-theme'))
        data.append(('ui-version', '1.8'))

        data = urlencode(data)
        return "%s?%s" % (UI_DOWNLOAD_URL, data)
