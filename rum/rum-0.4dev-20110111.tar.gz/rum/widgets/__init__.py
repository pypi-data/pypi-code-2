from tw.api import JSLink, CSSLink

modname = "rum.widgets"

# Default widgets. These can be accessed from the template at the `widgets`
# dictionary.
#
# The can be overriden by passing a dictionary at the `widgets` key of
# the configuration dict.
#
# entry_point notation can be used in the config file, Example:
#
#   [widgets]
#   main_css = 'myapp.widgets:rum_main_css'
# 
DEFAULT_WIDGETS = {
    # CSS included in all pages
    'rum_css': CSSLink(modname=modname, media="screen", filename="static/rum.css"),
    'rum_print_css':CSSLink(modname=modname, media="print", filename="static/print.css"),
    # CSS included in all pages that display forms
    'form_css': CSSLink(modname=modname, media="screen", filename="static/form.css"),
    # CSS included in the _meta page
    'meta_css': CSSLink(modname=modname, filename="static/meta.css"),
    }
