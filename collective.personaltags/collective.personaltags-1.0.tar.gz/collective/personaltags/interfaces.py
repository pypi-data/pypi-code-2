
from zope.interface import Interface, Attribute
from zope import schema

class ITagManager(Interface):
    def getTagsForContext(include_hidden=False):
        """Return the tags for the context"""
    def getTagsAndCounts(include_hidden=False):
        """Return a list of tags and counts - this is the summary information.
        """
    def getAllTags(include_hidden=False):
        """Return the list of available tags"""
    def addTag(tag):
        """Add a new tag to the content"""
    def deleteTag(tag):
        """Delete a new tag from the content"""
    def editorAvailable():
        """Is the editor viewlet available in this context"""
    def portletAvailable():
        """Is the portlet available in this context"""
    def getItemsForTag(tag):
        """Return the items tagged with the named tag"""
    def getTagsAndStatus():
        """
            Return a list of dict with
            tag - name
            count - usage count
            system - true of false for system tag
            hidden - true or false for hidden
        """
    def confShow(tag):
        """Configure the named tag so that it is shown"""
    def confHide(tag):
        """Configure the named tag so that it is hidden"""
    def confDelete(tag):
        """Delete the named tag alltogether"""
    defaultViewName = Attribute(u"The name of the default View")


class IPersonalTagsSettings(Interface):
    #storage = schema.TextLine(title=u'Storage Class', default=u'demo')
    storage = schema.Choice(title=u"Storage Class", default=u'demo',
            vocabulary=u"collective.personaltags.managers")
    viewurl = schema.TextLine(title=u'Override View URL', required=False)
    system_tags = schema.TextLine(title=u'System Wide Tags - comma separated', default=u'starred', required=False)
    portal_types = schema.Set(title=u"Limit to these Types",
        description=u"If you select no options, the tags will apply to all portal_types",
        value_type=schema.Choice(title=u"portal_type",
        vocabulary=u"collective.personaltags.content_types"))

