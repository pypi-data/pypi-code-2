import os
import sys
import urllib2
import urlparse
from paste.script import templates

DOLMEN_RELEASE_URL = 'http://www.dolmen-project.org/kgs/'


class DolmenProject(templates.Template):
    _template_dir = 'template'
    summary = "A dolmen project"
    required_templates = ['grok']

    def check_vars(self, vars, cmd):
        vars['install_requires'] = """
# Basic Dolmen Site
                        'dolmen.app.site',
                        'dolmen.app.layout',
                        'dolmen.app.content',
                        'dolmen.app.container',
# PAU
                        'zope.authentication',
                        'zope.pluggableauth',
                        'dolmen.app.authentication',
                        'menhir.contenttype.user',
# Functionalities
                        'dolmen.app.breadcrumbs',
                        'dolmen.app.viewselector',
                        'dolmen.app.search',
# Content types
                        'menhir.contenttype.document',
                        'menhir.contenttype.file',
                        'menhir.contenttype.folder',
                        'menhir.contenttype.image',
                        'menhir.contenttype.photoalbum',
# Skin
                        'menhir.skin.lightblue',"""
        vars['additional_grants'] = """
      <grant permission="dolmen.content.View"
             principal="zope.Everybody" />"""

        version_url = vars.get('version_url')
        if version_url is None:
            print "Determining current dolmen version..."
            # If no version URL was specified, we look up the current
            # version first and construct a URL.
            current_info_url = urlparse.urljoin(DOLMEN_RELEASE_URL, 'current')
            version = self.download(current_info_url).strip()
            version_url = '%sdolmen-kgs-%s.cfg' % (
                    DOLMEN_RELEASE_URL, version)
        vars['version_url'] = """
    %s
# authenticated sources
#    http://www.dolmen-project.org/kgs/dolmen-dev.cfg
    sources.cfg""" % version_url

        vars['include_site_packages'] = """true
allowed-eggs-from-site-packages = PIL"""

        vars['run_buildout'] = 'false'
        return vars

    def post(self, command, output_dir, vars):
        os.remove(os.path.join(output_dir, 'src', vars['package'], 'app_templates', 'index.pt'))

    def download(self, url):
        """Downloads a file and returns the contents.

        If an error occurs, we abort, giving some information about
        the reason.
        """
        contents = None
        try:
            contents = urllib2.urlopen(url).read()
        except urllib2.HTTPError:
            # Some 404 or similar happened...
            print "Error: cannot download required %s" % url
            print "Maybe you specified a non-existing version?"
            sys.exit(1)
        except IOError:
            # Some serious problem: no connect to server...
            print "Error: cannot download required %s" % url
            print "Server may be down.  Please try again later."
            sys.exit(1)
        return contents
