from django.conf.urls.defaults import patterns

from i18nurls.urlresolvers import PrefixedRegexURLResolver, PrefixedURLConf


def language_prefixed_patterns(prefix, *args):
    """
    Prefix all URLs with the current active language code.
    """
    pattern_list = patterns(prefix, *args)
    return [PrefixedRegexURLResolver(PrefixedURLConf(pattern_list))]
