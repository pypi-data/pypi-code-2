################################################################
# zopyx.smartprintng.lite
# (C) 2009,  ZOPYX Limited & Co. KG, D-72070 Tuebingen, Germany
################################################################


def getLanguageForObject(obj):

    language = obj.portal_languages.getDefaultLanguage()
    obj_language = None
    try:
        obj_language = obj.Language()
    except AttributeError:
        obj_language = obj.getLanguage()
    if obj_language:
        language = obj_language
    return language


