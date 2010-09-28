from plone.browserlayer.utils import registered_layers
from zope.app.publisher.browser.menu import BrowserMenu
from zope.app.publisher.browser.menu import BrowserSubMenuItem
from zope.interface import implements

from Products.CMFCore.utils import getToolByName

from Products.LinguaPlone import LinguaPloneMessageFactory as _
from Products.LinguaPlone.browser.interfaces import ITranslateMenu
from Products.LinguaPlone.browser.interfaces import ITranslateSubMenuItem
from Products.LinguaPlone.interfaces import ILinguaPloneProductLayer


class TranslateMenu(BrowserMenu):
    implements(ITranslateMenu)

    def getUntranslatedLanguages(self, context):
        lt=getToolByName(context, "portal_languages")
        languages=lt.listSupportedLanguages()
        translated=context.getTranslationLanguages()
        languages=[lang for lang in languages if lang[0] not in translated]
        languages.sort(key=lambda x: x[1])
        return languages


    def getMenuItems(self, context, request):
        """Return menu item entries in a TAL-friendly form."""

        menu = []
        url = context.absolute_url()
        lt = getToolByName(context, "portal_languages")
        showflags = lt.showFlags()
        langs = self.getUntranslatedLanguages(context)

        for (lang_id, lang_name) in langs:
            icon=showflags and lt.getFlagForLanguageCode(lang_id) or None
            item={
                "title": lang_name,
                "description": _(u"title_translate_into",
                                 default=u"Translate into ${lang_name}",
                                 mapping={"lang_name": lang_name}),
                "action": url+"/@@translate?newlanguage=%s" % lang_id,
                "selected": False,
                "icon": icon,
                "extra": {"id": "translate_into_%s" % lang_id,
                          "separator": None,
                          "class": ""},
                "submenu": None,
                }

            menu.append(item)

        menu.append({
            "title": _(u"label_manage_translations",
                       default=u"Manage translations..."),
            "description": u"",
            "action": url+"/manage_translations_form",
            "selected": False,
            "icon": None,
            "extra": {"id": "_manage_translations",
                      "separator": langs and "actionSeparator" or None,
                      "class": ""},
            "submenu": None,
            })

        return menu


class TranslateSubMenuItem(BrowserSubMenuItem):
    implements(ITranslateSubMenuItem)

    title = _(u"label_translate_menu", default=u"Translate into...")
    description = _(u"title_translate_menu",
            default="Manage translations for your content.")
    submenuId = "plone_contentmenu_translate"

    order = 5
    extra = {"id": "plone-contentmenu-translate"}

    @property
    def action(self):
        return self.context.absolute_url() + "/manage_translations_form"

    def available(self):
        if self.disabled():
            return False # pragma: no cover
        return ILinguaPloneProductLayer in registered_layers()

    def disabled(self):
        return False

    def selected(self):
        return False
