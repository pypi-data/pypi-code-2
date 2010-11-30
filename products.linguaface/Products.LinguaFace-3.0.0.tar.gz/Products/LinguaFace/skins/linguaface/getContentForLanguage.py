## Script (Python) "getContentForLanguage"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=languageCode
##title=
##
results = context

## The original script comes from
## LinguaPlone's file skins/LinguaPlone/languageSelectorData.py

translations = {} # lang:[object, wfstate]
if context.isTranslatable():
    translations = context.getTranslations()

langtool = context.portal_languages
site_languages = langtool.listSupportedLanguages()
current_language = langtool.getPreferredLanguage()

for code, name in site_languages:
    available = translations.has_key(code)
    if available and code == languageCode:
        return translations.get(languageCode)[0]

return context

