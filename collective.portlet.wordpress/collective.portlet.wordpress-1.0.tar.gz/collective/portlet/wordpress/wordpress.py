import logging
import sys
import urllib2
import socket
from elementtree import ElementTree as et

from zope.interface import Interface
from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from plone.memoize.instance import memoize

from zope import schema
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.portlet.wordpress import wordPressPortletMessageFactory as _


FEED_PATH = '?feed=rss2'

logger = logging.getLogger('collective.portlet.wordpress.WordPressBlogPortlet')
def logException(msg, context=None):
    logger.exception(msg)
    if context is not None:
        error_log = getattr(context, 'error_log', None)
        if error_log is not None:
            error_log.raising(sys.exc_info())

class IWordPressBlogPortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    name = schema.TextLine(
        title=_(u"Portlet header"),
        description=_(u"This is used as a portlet header text."),
        required=False)
    
    url = schema.URI(
        title=_(u"Blog URL"),
        description=_("URL to your wordpress blog."),
        required=True)
    
    wait = schema.Int(
        title=_(u"Request Timeout"),
        description=_(u"Enter here number of seconds you allow portlet "
                      u"to wait for answer from wordpress site."),
        min=1,
        required=True,
        default=15)
    
    limit = schema.Int(
        title=_(u"Number of entries"),
        description=_(u"Number of entries to list in a portlet. Note: set 0 to "
                      u"show all items."),
        required=True,
        default=5)
    
    show_more = schema.Bool(
        title=_(u"Show more link"),
        description=_(u"If checked, link to blog will be inserted at the bottom"
                      " of the portlet."),
        default=True)


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IWordPressBlogPortlet)

    name = u""
    url = ''
    wait = 15
    limit = 5
    show_more = True

    def __init__(self, name=u"", url='', wait = 15,
                 limit=5, show_more=True):
        self.name = name
        self.url = url
        self.wait = wait
        self.limit = limit
        self.show_more = show_more

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return _(self.name or u"WordPress Blog Portlet")


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """
    render = ViewPageTemplateFile('wordpress.pt')

    @property
    def available(self):
        return len(self.getBlogEntries()) > 0
    
    @memoize
    def getBlogEntries(self):
        """Returns recent WP blog entries"""
        result = []
        counter = 0
        limit = self.data.limit
        for item in self._fetchEntries(self.data.url+FEED_PATH):
            if limit and counter >= limit:
                break
            result.append(item)
            counter += 1
        return tuple(result)

    def _fetchEntries(self, url):
        default_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(self.data.wait)
        result = []
        
        # one more try to finally set socket timeout back to previous value
        try:
            try:
                feed = urllib2.urlopen(url).read()
            except Exception, e:
                logException(_(u"Problem during fetching '%s' resource" % url),
                             self.context)
                pass
            else:
                try:
                    root = et.fromstring(feed).find('channel')
                except Exception, e:
                    pass
                else:
                    if root is not None:
                        for item in root.findall("item"):
                            # item title
                            title_node = item.find('title')
                            title = title_node is not None and \
                                title_node.text or ''
                        
                            # item description
                            desc_node = item.find('description')
                            desc = desc_node is not None and desc_node.text \
                                or ''
                        
                            # item link
                            link_node = item.find('link')
                            link = link_node is not None and link_node.text \
                                or ''
                        
                            # item date
                            date_node = item.find('pubDate')
                            date = date_node is not None and date_node.text \
                                or ''
                        
                            # title and link url are required
                            if not (title and link):
                                continue
                        
                            result.append({
                                'title': title,
                                'desc': desc,
                                'url': link,
                                'date': date})
        except Exception:
            pass
        
        socket.setdefaulttimeout(default_timeout)
        return result

class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IWordPressBlogPortlet)
    label = _(u"Add WordPress Blog Portlet")
    description = _(u"This portlet displays recent WordPress blog entries.")

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IWordPressBlogPortlet)
    label = _(u"Edit WordPress Blog Portlet")
    description = _(u"This portlet displays recent WordPress blog entries.")
