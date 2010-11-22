"""The conversation and replies adapters

The conversation is responsible for storing all comments. It provides a
dict-like API for accessing comments, where keys are integers and values
are IComment objects. It also provides features for finding comments quickly.

The two IReplies adapters - one for the IConversation and one for IComment -
manipulate the same data structures, but provide an API for finding and
manipulating the comments directly in reply to a particular comment or at the
top level of the conversation.
"""



from plone.registry.interfaces import IRegistry

from zope import interface, component
from zope.annotation.interfaces import IAnnotations, IAnnotatable
from zope.interface import implements, implementer
from zope.component import adapts, adapter, queryUtility


from Acquisition import aq_base, aq_inner, aq_parent


from Products.CMFCore.utils import getToolByName
from Products.CMFCore.interfaces import IFolderish

from Products.CMFPlone.interfaces import IPloneSiteRoot, INonStructuralFolder

from plone.app.discussion.interfaces import IDiscussionSettings

from plone.app.discussion.conversation import Conversation as ConversationBase
from plone.app.discussion.conversation import ANNOTATION_KEY
from raptus.article.core.interfaces import IArticle
from plone.app.discussion.interfaces import IConversation

class Conversation(ConversationBase):
    
    def enabled(self):
        # Returns True if discussion is enabled on the conversation

        # Fetch discussion registry
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings, check=False)

        # Check if discussion is allowed globally
        if not settings.globally_enabled:
            return False

        parent = aq_inner(self.__parent__)

        def traverse_parents(obj):
            # Run through the aq_chain of obj and check if discussion is
            # enabled in a parent folder.
            for obj in self.aq_chain:
                if not IPloneSiteRoot.providedBy(obj):
                    if (IFolderish.providedBy(obj) and
                        not INonStructuralFolder.providedBy(obj)):
                        flag = getattr(obj, 'allow_discussion', None)
                        if flag is not None:
                            return flag
            return None

        obj = aq_parent(self)

        # If discussion is disabled for the object, bail out
        obj_flag = getattr(aq_base(obj), 'allow_discussion', None)
        if obj_flag is False:
            return False

        # Check if traversal returned a folder with discussion_allowed set
        # to True or False.
        folder_allow_discussion = traverse_parents(obj)

        if folder_allow_discussion is True:
            if not getattr(self, 'allow_discussion', None):
                return True
        elif folder_allow_discussion is False:
            if obj_flag:
                return True

        # Check if discussion is allowed on the content type
        portal_types = getToolByName(self, 'portal_types')
        document_fti = getattr(portal_types, obj.portal_type)
        if not document_fti.getProperty('allow_discussion'):
            # If discussion is not allowed on the content type,
            # check if 'allow discussion' is overridden on the content object.
            if not obj_flag:
                return False

        return True


@implementer(IConversation)
@adapter(IArticle)
def conversationAdapterFactory(content):
    """Adapter factory to fetch the default conversation from annotations.
    Will create the conversation if it does not exist.
    """
    
    annotions = IAnnotations(content)
    if ANNOTATION_KEY in annotions and isinstance(annotions[ANNOTATION_KEY], Conversation):
        conversation = annotions[ANNOTATION_KEY]
    else:
        conversation = Conversation()
        conversation.__parent__ = aq_base(content)
        annotions[ANNOTATION_KEY] = conversation
        
    return conversation.__of__(content)
