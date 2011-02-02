import string
from optparse import OptionParser
import os, sys

import egg_translations
from babel import negotiate_locale

from rum import app

__all__ = ["_", "N_", "RumTranslator", "ugettext", "ungettext"]

# Monkey-patch dumb validation
egg_translations.isValidLocaleForm = lambda locale: True

class LazyString(object):
    """Has a number of lazily evaluated functions replicating a 
    string. Just override the eval() method to produce the actual value.

    This method copied from TurboGears.
    
    """
    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.post_processors = []

    def capitalize(self):
        self.post_processors.append(string.capitalize)
        return self

    def eval(self):
        ret = self.func(*self.args, **self.kwargs)
        for p in self.post_processors:
            ret = p(ret)
        return ret

    def __unicode__(self):
        return unicode(self.eval())

    def __str__(self):
        return str(self.eval())

    def __mod__(self, other):
        return self.eval() % other

    #
    # __repr__ and __eq__ are just needed to make fields unit-tests and
    # doctests pass since they now have i18nized labels
    #

    def __repr__(self):
        s = self.args[0]
        for p in self.post_processors:
            s = p(s)
        return repr(s)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.args == other.args and self.func is other.func
        return False

    def __cmp__(self, other):
        if isinstance(other, self.__class__):
            return cmp(self.args, other.args)
        return 1

def lazify(func):
    """Decorator to return a lazy-evaluated version of the original"""
    def newfunc(*args, **kwargs):
        return LazyString(func, *args, **kwargs)
    newfunc.__name__ = 'lazy_%s' % func.__name__
    newfunc.__doc__ = 'Lazy-evaluated version of the %s function\n\n%s' % \
        (func.__name__, func.__doc__)
    return newfunc

class RumTranslator(egg_translations.EggTranslations):
    """
    A translator that is able to load translation catalogs from pluggable
    eggs.

    TODO: Document me and how to create aforementioned plugins
    """
    _NAME = "RumTranslator"

    def __init__(self, locales, search_order=None, fallback=True):
        super(RumTranslator, self).__init__()
        if "all" in locales:
            fallback=True
        locales=[l for l in locales if l!="all"]

        self.initialize(locales, fallback)
        self.search_order = search_order or self.available_projects

    def initialize(self, localeSet, fallback=True):
        super(RumTranslator, self).initialize(
            localeSet, iniFileName='rum_i18n.ini', fallback=fallback
            )
        
    @property
    def available_projects(self):
        return self._localeCache.keys()

    @property
    def available_locales(self):
        if not self._fallback:
            return self._localeSet
        else:
            res=list(self._localeSet)
            res.append("all")
            return res
            
    @property
    def default_locale(self):
        return self.available_locales[0]
      

    @property
    def active_locale(self):
        request = app.request._current_obj()
        if request:
            locale = request.environ.get('rum.active_locale')
            if locale is None:
                if request.routes.get('lang') is None:
                    matches = request.accept_language.best_matches(
                        self.default_locale
                        )
                else:
                    matches = [request.routes['lang']]

                matches = map(lambda s: s.replace('-', '_'), matches)
                locale = negotiate_locale(matches, self.available_locales, '_')
                request.environ['rum.active_locale'] = locale
            return locale

    def _iter_translators(self, locales, project):
        if isinstance(locales, basestring):
            assert locales in self.available_locales
            locales = [locales]
        if self._fallback:
            locales.extend(l for l in self.available_locales
                           if l not in locales)

        if project == 'all':
            projects = self.search_order
        else:
            assert project in self.available_projects
            projects = [project]

        for locale in locales:
            for project in projects:
                key = (project, 'catalog', locale)
                if key in self._gtCache:
                    yield self._gtCache[key]
        

    #XXX: This is grossly inefficient. Try merging all project catalogs from
    #     each locale into one
    def ugettext(self, txt, project='all'):
        locale = self.active_locale or self.default_locale
        for translator in self._iter_translators(locale, project):
            result = translator.ugettext(txt, None)
            if result is not None:
                return result
        return txt
        
    def ungettext(self, singular, plural, n, project='all'):
        locale = self.active_locale or self.default_locale
        for translator in self._iter_translators(locale, project):
            result = translator.ungettext(singular, plural, n, None)
            if result is not None:
                return result
        return singular

@lazify
def ugettext(value):
    return app.translator.ugettext(value)

@lazify
def ungettext(singular, plural, n):
    return app.translator.ungettext(singular, plural, n)

_ = ugettext


def gettext_noop(value):
    """Mark a string for translation without translating it. Returns
    value.

    Used for global strings, e.g.::

        foo = N_('Hello')

        class Bar:
            def __init__(self):
                self.local_foo = _(foo)

        h.set_lang('fr')
        assert Bar().local_foo == 'Bonjour'
        h.set_lang('es')
        assert Bar().local_foo == 'Hola'
        assert foo == 'Hello'

    """
    return value

N_ = gettext_noop



tpl = """\
[%(domain)s::%(key)s]
catalog = %(locale_dir)s/%(locale)s/LC_MESSAGES/%(domain)s.mo
"""

parser = OptionParser(usage="%prog [OPTIONS] <egg-info-dir>")
parser.add_option("", "--locale-dir",
                  help="Relative path from egg-info dir where locales live, "
                       "default=i18n",
                  default="i18n",
                  dest="locale_dir"
                  )
parser.add_option("-d", "--domain",
                  help="Basename of the .mo file, eg: messages -> messages.mo. "
                       "default=messages",
                  default="messages",
                  dest="domain"
                  )
parser.add_option("-m", "--mode",
                  help="Mode we should open the .ini file as. default 'a+'",
                  default="a+",
                  dest="mode"
                  )
parser.add_option("", "--default",
                  help="Default locale. default 'en'",
                  default="en",
                  dest="default"
                  )

def main(argv=None):
    opts, args = parser.parse_args(argv)
    try:
        egginfo = args[0]
    except IndexError:
        print >> sys.stderr, "Need to provide an egg-info-dir"
        parser.print_help(sys.stderr)
        return -1

    inifile = open(os.path.join(egginfo, 'rum_i18n.ini'), opts.mode)
    locale_dir = opts.locale_dir
    domain = opts.domain

    # write 'all' section
    key = 'all'
    locale = opts.default
    print >> inifile, tpl % locals()

    for locale in os.listdir(os.path.join(egginfo, locale_dir)):
        key = locale
        if os.path.isdir(os.path.join(egginfo, locale_dir, locale)):
            print >> inifile, tpl % locals()

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
