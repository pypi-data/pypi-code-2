from fanstatic import Resource
from js.extjs.library import library
from js.extjs import extjs

defaultThemes = ['gray', 'access']   # what about vista?
themes = {}


def add_theme(themeName):
    css = Resource(library, 'resources/css/xtheme-%s.css' % themeName,
                   depends=[extjs.css])

    global themes
    themes[themeName] = globals()[themeName] = css
    return css

for themeName in defaultThemes:
    add_theme(themeName)
