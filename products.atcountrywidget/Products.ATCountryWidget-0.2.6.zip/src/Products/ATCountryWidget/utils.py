from Products.ATCountryWidget.config import LANGUAGE_LIST

def getLanguageList(preferences=[]):
    langs = LANGUAGE_LIST[:]
    prefs = []
    normal = []
    for code, lang in langs:
        if code in preferences:
            prefs.append((code, lang))
        else:
            normal.append((code, lang))
    return prefs + normal
