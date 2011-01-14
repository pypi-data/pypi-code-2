#!/usr/bin/env python
#-*- coding: utf8 -*-
from __future__ import unicode_literals

from pytz import utc

class Show(object):
    """
    Represents a TV-show. On object construction the time is automatically
    convertet into UTC time and normalized.
    """ 
    
    def __init__(self, thetime, title, subtitle, genre):
        #: The time when this show starts. This is a ``datetime.datetime`` in
        #: UTC.
        self.time = utc.normalize(thetime.astimezone(utc))
        #: The title of this show.
        self.title = title
        #: The subtitle of this show. This is usually the name of the episode.
        self.subtitle = subtitle
        #: The German genre this show belongs to.
        self.genre = genre

class ShowList(list):
    """
    Is a ``list`` for TV shows with some convinience methods.
    """
    
    def get_at(self, thetime):
        """
        Returns the show running at the given time. If time is smaller than
        the first show's time a KeyError is raised. ``thetime`` is automatically
        converted into UTC time and normalized.
        """
        thetime = utc.normalize(thetime.astimezone(utc))
        shows = sorted(self, lambda a, b: cmp(a.time, b.time))
        
        if thetime < shows[0].time:
            raise KeyError("%s is before the first show" % thetime)

        lastshow = shows[0]
        for show in shows:
            if show.time > thetime:
                return lastshow
            lastshow = show
        return lastshow

