#!/usr/bin/env python
#-*- coding: utf8 -*-
from __future__ import unicode_literals

class Channel(object):
    """
    Represents a single TV-channel.
    """
    
    def __init__(self, key, name):
        #: The internal name of the channel.
        self.key = key
        #: The human readable name of the channel.
        self.name = name
    
    def __eq__(self, other):
        return self.key == other.key and self.name == other.name
    
    def __ne__(self, other):
        return not self == other

class ChannelList(list):
    """
    This extends ``list`` with some utilitiy methods to find channels.
    """
    
    def get_by_name(self, name):
        """
        Returns the first channel in the list that has the given name. Raises
        an ``KeyError`` if the given name is not found.
        """
        for channel in self:
            if channel.name == name:
                return channel
        raise KeyError
    
    def get_by_key(self, key):
        """
        Returns the first channel in the list that has the given key. Raises
        an ``KeyError`` if the given name is not found.
        """
        for channel in self:
            if channel.key == key:
                return channel
        raise KeyError
    

