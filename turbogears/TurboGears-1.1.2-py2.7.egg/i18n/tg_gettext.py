import os
import sys
from gettext import translation

from turbogears import config
from turbogears.util import get_package_name, request_available
from turbogears.i18n.utils import get_locale
from turbojson.jsonify import jsonify

import logging
log = logging.getLogger("turbogears.i18n")

_catalogs = {}

def get_locale_dir():
    localedir = config.get("i18n.locale_dir")
    if not localedir:
        package = get_package_name()
        if package:
            localedir = os.path.join(os.path.dirname(
                sys.modules[package].__path__[0]), "locales")
    return localedir

def is_locale_supported(locale, domain=None):
    """Check if [domain].mo file exists for this language."""
    if not domain:
        domain = config.get("i18n.domain", "messages")

    localedir = get_locale_dir()
    return localedir and os.path.exists(os.path.join(
        localedir, locale, "LC_MESSAGES", "%s.mo" % domain))

def get_catalog(locale, domain = None):
    """Return translations for given locale."""
    if not domain:
        domain = config.get("i18n.domain", "messages")

    catalog = _catalogs.get(domain)

    if not catalog:
        catalog = _catalogs[domain] = {}

    messages = catalog.get(locale)
    if not messages:
        localedir = get_locale_dir()
        messages = catalog[locale] = translation(domain=domain,
            localedir=localedir, languages=[locale])

    return messages

def plain_gettext(key, locale=None, domain=None):
    """Get the gettext value for key.

    Added to builtins as '_'. Returns Unicode string.

    @param key: text to be translated
    @param locale: locale code to be used.
        If locale is None, gets the value provided by get_locale.

    """
    gettext_func_name = config.get("i18n.gettext", "tg_gettext")
    gettext_func = None

    if gettext_func_name == "tg_gettext":
        gettext_func = tg_gettext

    elif gettext_func_name == "so_gettext":
        try:
            from turbogears.i18n.sogettext import so_gettext
            gettext_func = so_gettext

        except ImportError, e:
            log.error("Could not load sogettext: %s" % e)
            log.error("Translation disabled")
            

    elif gettext_func_name == "sa_gettext":
        try:
            from turbogears.i18n.sagettext import sa_gettext
            gettext_func = sa_gettext

        except ImportError, e:
            log.error("Could not load sagettext: %s" % e)
            log.error("Translation disabled")
    
    else:
        log.error("Invalid i18n.gettext option: %s" % gettext_func_name)
        log.error("Translation disabled")

    if gettext_func is None:
        # gettext function could not be loaded? Just avoid
        # to translate and return original data
        return key

    else:
        # gettext function loaded properly, use it :)
        return gettext_func(key, locale, domain)

def tg_gettext(key, locale=None, domain=None):
    """Get the gettext value for key.

    Added to builtins as '_'. Returns Unicode string.

    @param key: text to be translated
    @param locale: locale code to be used.
        If locale is None, gets the value provided by get_locale.

    """
    if locale is None:
        locale = get_locale()

    if not is_locale_supported(locale):
        locale = locale[:2]

    if key == '':
        return '' # special case

    try:
        return get_catalog(locale, domain).ugettext(key)

    except KeyError:
        return key

    except IOError:
        return key

def plain_ngettext(key1, key2, num, locale=None):
    """Translate two possible texts based on whether num is greater than 1.

    @param key1: text if num==1
    @param key2: text if num!=1
    @param num: a number
    @type num: integer
    @locale: locale code to be used.
        If locale is None, gets the value provided by get_locale.

    """
    if num==1:
        return plain_gettext(key1, locale)

    else:
        return plain_gettext(key2, locale)

class lazystring(object):
    """Has a number of lazily evaluated functions replicating a string.

    Just override the eval() method to produce the actual value.

    """

    def __init__(self, func, *args, **kw):
        self.func = func
        self.args = args
        self.kw = kw

    def eval(self):
        return self.func(*self.args, **self.kw)

    def __unicode__(self):
        return unicode(self.eval())

    def __str__(self):
        return str(self.eval())

    def __mod__(self, other):
        return self.eval() % other

    def __cmp__(self, other):
        return cmp(self.eval(), other)

    def __eq__(self, other):
        return self.eval() == other

    def __deepcopy__(self, memo):
        return self

def lazify(func):
    def newfunc(*args, **kw):
        lazystr = lazystring(func, *args, **kw)
        return lazystr

    return newfunc

@jsonify.when("isinstance(obj, lazystring)")
def jsonify_lazystring(obj):
    return unicode(obj)

lazy_gettext = lazify(plain_gettext)
lazy_ngettext = lazify(plain_ngettext)

def gettext(key, locale=None, domain=None):
    """Get the gettext value for key.

    Added to builtins as '_'. Returns Unicode string.

    @param key: text to be translated
    @param locale: locale code to be used.
        If locale is None, gets the value provided by get_locale.

    """
    if request_available():
        return plain_gettext(key, locale, domain)

    else:
        return lazy_gettext(key, locale, domain)

def ngettext(key1, key2, num, locale=None):
    """Translate two possible texts based on whether num is greater than 1.

    @param key1: text if num==1
    @param key2: text if num!=1
    @param num: a number
    @type num: integer
    @param locale: locale code to be used.
        If locale is None, gets the value provided by get_locale.

    """
    if request_available():
        return plain_ngettext(key1, key2, num, locale)
    else:
        return lazy_ngettext(key1, key2, num, locale)

def install():
    """Add the gettext function to __builtins__ as '_'."""
    __builtins__["_"] = gettext
