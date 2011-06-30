"""Data and utilities about Django applications and packages (used for validation).
"""

from itertools import ifilter

# These packages are always installed
PREINSTALLED_PACKAGES = ["django", "south"]

# This is a mapping from python packages (as used in requirements.txt)
# to lists of django app names provided by those packages.
KNOWN_PACKAGES_TO_APPS = {
    "django": [
      "django.contrib.admin",
      "django.contrib.admindocs",
      "django.contrib.auth",
      "django.contrib.comments",
      "django.contrib.contenttypes",
      "django.contrib.csrf",
      "django.contrib.databrowse",
      "django.contrib.flatpages",
      "django.contrib.formtools",
      "django.contrib.gis",
      "django.contrib.humanize",
      "django.contrib.localflavor",
      "django.contrib.markup",
      "django.contrib.messages",
      "django.contrib.redirects",
      "django.contrib.sessions",
      "django.contrib.sitemaps",
      "django.contrib.sites",
      "django.contrib.syndication",
      "django.contrib.webdesign"
    ],
    "django-cms": [
      'cms',
      'cms.plugins.text',
      'cms.plugins.picture',
      'cms.plugins.file',
      'cms.plugins.flash',
      'cms.plugins.link',
      'cms.plugins.snippet',
      'cms.plugins.googlemap',
      'cms.plugins.teaser',
      'cms.plugins.video',
      'cms.plugins.twitter',
      'cms.plugins.inherit',
      "menus"
    ],
    "django-mptt": ["mptt"],
    "django-appmedia": ['appmedia'],
    "django-sekizai": ['sekizai'],
    "django-extensions":['django_extensions'],
    "django-disqus": ['disqus'],
    "django-memcache-status": ['memcache_status'],
    "django-tagging": ['tagging'],
    "django-debug-toolbar":['debug_toolbar'],
    "django-activitysync":['activitysync'],
    "south": ['south']
}

def get_apps_for_packages(package_list):
    """Return a list of Django apps corresponding to the package list.
    Packages not in the list are ignored.
    """
    ll = [KNOWN_PACKAGES_TO_APPS[p] for p in ifilter(KNOWN_PACKAGES_TO_APPS.has_key, package_list)]
    return sum(ll, [])

def extend_app_list(app_list):
    """Django has this really annoying feature where you can
    just list the last component of an app's package name in INSTALLED_APPS
    instead of the entire name (e.g. text instead of cms.plugins.text).
    To accomodate this, we take the a list of apps and add all the short
    names to it.
    """
    l = []
    for app in app_list:
        l.append(app)
        app_comps = app.split('.')
        if len(app_comps)>1:
            l.append(app_comps[-1])
    return l

def _get_apps_to_packages(packages_to_apps):
    m = {}
    def add_pkg(app, pkg):
        if m.has_key(app):
            l = m[app]
        else:
            l = []
        if pkg not in l:
            l.append(pkg)
            m[app] = l
    for package in packages_to_apps:
        for app in packages_to_apps[package]:
            add_pkg(app, package)
            app_comps = app.split('.')
            if len(app_comps)>1:
                add_pkg(app_comps[-1], package)
    return m

PACKAGES_FOR_KNOWN_APPS = _get_apps_to_packages(KNOWN_PACKAGES_TO_APPS)
