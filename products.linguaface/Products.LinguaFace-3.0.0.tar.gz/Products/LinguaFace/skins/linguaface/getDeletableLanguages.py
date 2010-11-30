##parameters=
##title=Return deletable languages

lang_names = context.portal_languages.getAvailableLanguages()
lang_names[''] = 'Neutral'
translations = context.getTranslations()

# Return tuples of lang id, lang name and content title
languages = [(lang, lang_names[lang], translations[lang][0].Title())
             for lang in translations.keys()]

def lcmp(x, y):
    return cmp(x[1], y[1])

languages.sort(lcmp)


return languages
