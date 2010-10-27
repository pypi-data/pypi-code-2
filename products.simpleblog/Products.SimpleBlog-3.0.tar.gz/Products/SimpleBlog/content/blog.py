from Products.Archetypes.public import *
from Products.SimpleBlog.config import DISPLAY_MODE
from Products.SimpleBlog.config import PROJECTNAME
from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.content.base import ATCTFolder
from plone.app.portlets.utils import assignment_mapping_from_key
from Products.SimpleBlog.browser import simpleblogportlet
from Products.SimpleBlog.interfaces import IBlog
from zope.interface import implements

schema = ATCTFolder.schema.copy() +  Schema((
    StringField('description',
                isMetadata=1,
                accessor='Description',
                searchable=1,
                widget=TextAreaWidget(label='Description',
                                      label_msgid="label_blog_description",
                                      description_msgid="help_blog_description",
                                      i18n_domain="SimpleBlog",
                                      description='Give a description for this SimpleBlog.')),
    # this field is deprecated, here for compatibility
    StringField('displayMode',
                vocabulary=DISPLAY_MODE,
                widget=SelectionWidget(label='Display Mode',
                                       label_msgid="label_display_mode",
                                       description_msgid="help_display_mode",
                                       i18n_domain="SimpleBlog",
                                       description='Choose the display mode.',
                                       visible={'view' : 'invisible', 'edit':'invisible'}),
                default='descriptionOnly'),
    IntegerField('displayItems',
                widget=IntegerWidget(label='BlogEntries to display',
                                      label_msgid="label_display_items",
                                      description_msgid="help_display_items",
                                      i18n_domain="SimpleBlog",
                                      description='Set the maximum number of BlogEntries to display.'),
                 default=20),
    BooleanField('warnForUnpublishedEntries',
             default=1,
             widget=BooleanWidget(label='Show unpublished entries warning',
                        i18n_domain="SimpleBlog",
                        label_msgid="label_warnForUnpublishedEntries",
                        description_msgid="help_warnForUnpublishedEntries",
                        description='When checked, a warning will be displayed on the blog\'s frontpage if there are entries that are not yet published.')),
    BooleanField('allowCrossPosting',
             default=1,
             widget=BooleanWidget(label='Allow cross-posting',
                        i18n_domain="SimpleBlog",
                        label_msgid="label_allowCrossPosting",
                        description_msgid="help_allowCrossPosting",
                        description='When checked, this blog will include cross-post entries from other blogs.')),
    LinesField('categories',
               widget=LinesWidget(label='Possible Categories',
                                  label_msgid="label_categories",
                                  description_msgid="help_categories",
                                  i18n_domain="SimpleBlog",
                                  description='Supply the list of possible categories that can be used in SimpleBlog Entries.'))
        ))

# hide relatedItems
schema['relatedItems'].widget.visible={'view' : 'invisible', 'edit':'invisible'}

class Blog(ATCTFolder):
    """ Blog """

    implements(IBlog)

    schema = schema

    def canSetDefaultPage(self):
        return False

    def synContentValues(self):
        # get brains for items that are published within the context of this blog.
        entries = self.simpleblog_tool.searchForEntries(self, maxResults=0)

        # convert to objects
        objs = [e.getObject() for e in entries]
        return objs

    def listCategories(self):
        cats=self.getCategories()

        # add the global categories
        for c in self.simpleblog_tool.getGlobalCategories():
            if not c in cats:
                cats.append(c)
        cats = list(cats)
        cats.sort()
        return tuple(cats)

    def getForeignEntries(self):
        """ Returns all entries from other blogs that are published into this blog using the remoteBlogs value """
        foreign = [f for f in self.getBRefs('AppearsIn') if self.portal_membership.checkPermission('View', f)]
        pw=getToolByName(self, 'portal_workflow')
        state = self.simpleblog_tool.getPublishedState()
        return [f for f in foreign if pw.getInfoFor(f, 'review_state') == state]


    def getEntries(self, category=None, maxResults=None, fromHere=0, filterState=1, sort=1, join=0, addCrossPostInfo=0, **kwargs):
        """ Return all the contained published entries, real objects, not the brains """
        # see simpleblog_tool.searchForEntries for API description

        query=kwargs

        publishedState = self.simpleblog_tool.getPublishedState()

        if category!=None:
            query['EntryCategory']=category

        query['getAlwaysOnTop']=1

        if filterState:
            query['review_state']=publishedState

        # first the items that need to be listed on top
        localOnTop = self.portal_catalog.searchResults(query, meta_type='BlogEntry', path={'query':self.simpleblog_tool.getObjectPath(self),'level':0}, sort_order='reverse', sort_on='effective')
        localOnTop = [r.getObject() for r in localOnTop ]

        # then the other items
        query['getAlwaysOnTop']=0
        localNoTop = self.portal_catalog.searchResults(query, meta_type='BlogEntry', path={'query':self.simpleblog_tool.getObjectPath(self),'level':0}, sort_order='reverse', sort_on='effective')
        localNoTop= [r.getObject() for r in localNoTop]

        # foreign items
        if self.getAllowCrossPosting():
            foreignEntries = self.getForeignEntries()
        else:
            foreignEntries=[]

        # filter out the always on top entries
        foreignOnTop = [e for e in foreignEntries if e.getAlwaysOnTop()]
        foreignNoTop = [e for e in foreignEntries if not e.getAlwaysOnTop()]

        # so, now we have:
        # total = localOnTop + foreignOnTop + localNoTop + foreignNoTop
        # and that needs to be sorted


        if addCrossPostInfo:
            # make each object a tuple (obj, <iscrosspost>)
            foreignOnTop = [(e,1) for e in foreignOnTop]
            foreignNoTop = [(e,1) for e in foreignNoTop]
            localOnTop = [(e,0) for e in localOnTop]
            localNoTop = [(e,0) for e in localNoTop]

        onTop = foreignOnTop + localOnTop
        onBottom = foreignNoTop + localNoTop

        if sort and foreignEntries:
            if addCrossPostInfo:
                onTop.sort((lambda x,y:cmp(y[0].effective(), x[0].effective())))
                onBottom.sort((lambda x,y:cmp(y[0].effective(), x[0].effective())))
            else:
                onTop.sort((lambda x,y:cmp(y.effective(), x.effective())))
                onBottom.sort((lambda x,y:cmp(y.effective(), x.effective())))

        if join:
            results = onTop+onBottom
            if maxResults==0:
                return results
            elif maxResults==None:
                return results[:self.simpleblog_tool.getMaxItemsInPortlet()]
            else:
                return results[:maxResults]
        else:
            return (onTop, onBottom)

    def at_post_create_script(self):
        """ create the portlet  """
        # do we have to create the portlet?
        tool = getToolByName(self, 'simpleblog_tool')
        if tool.getCreatePortletOnBlogCreation():
            portlet_mapping = assignment_mapping_from_key(
               context=self,
               manager_name=u"plone.rightcolumn",
               category="context",
               key="/".join(self.getPhysicalPath()))

            showComments = tool.getShowComments()
            showRecent = tool.getShowRecent()
            showCalendar = tool.getShowCalendar()
            showCategories = tool.getShowCategories()

            portlet_mapping[self.UID()] = simpleblogportlet.Assignment(showCategories = showCategories,
                                                                                                   showCalendar = showCalendar,
                                                                                                   showRecent = showRecent,
                                                                                                   showComments = showComments)

registerType(Blog, PROJECTNAME)
