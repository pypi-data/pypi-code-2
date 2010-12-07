from persistent.mapping import PersistentMapping
from zope.annotation.interfaces import IAnnotations

from Acquisition import aq_inner


ANNOTATION_KEY = "collective.editskinswitcher"


def get_selected_default_skin(context):
    """Get the selected default skin using annotations."""
    try:
        annotations = IAnnotations(context)
    except TypeError:
        # Not a context that we can handle (seen with
        # Products.CMFUid.UniqueIdAnnotationTool.UniqueIdAnnotation
        # when saving an object).
        return None
    ns = annotations.get(ANNOTATION_KEY, None)
    if ns is not None:
        return ns.get("default-skin", None)


def set_selected_default_skin(context, skin_name=None):
    """Set the specified skin name as the default skin using annotations."""
    annotations = IAnnotations(aq_inner(context))
    ns = annotations.get(ANNOTATION_KEY, None)
    if ns is None:
        ns = annotations[ANNOTATION_KEY] = PersistentMapping()

    ns["default-skin"] = skin_name
