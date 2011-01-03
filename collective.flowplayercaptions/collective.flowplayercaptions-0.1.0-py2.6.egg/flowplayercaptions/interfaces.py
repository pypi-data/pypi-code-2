# -*- coding: utf-8 -*-

from zope.interface import Interface

class IFlowplayerCaptionsLayer(Interface):
    """Marker interface for the collective.flowplayercaptions layer"""

class ICaptionsSource(Interface):
    """Marker interface for sorce that provides captions"""
    
