# -*- coding: utf-8 -*-

from zope.interface import alsoProvides, noLongerProvides
from collective.flowplayercaptions.interfaces import ICaptionsSource

def toggleCaptions(object, event):
    """Mark the video as ICaptionsSource, or remove it; it depends on "captions" data"""
    data = object.getField('captions').get(object)
    if data:
        if not ICaptionsSource.providedBy(object):
            alsoProvides(object, ICaptionsSource)
            object.reindexObject(idxs=['object_provides'])
    else:
        if ICaptionsSource.providedBy(object):
            noLongerProvides(object, ICaptionsSource)
            object.reindexObject(idxs=['object_provides'])
