#-*- coding: utf-8 -*-
"""Provides functions for dealing with user notifications.

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2010
"""
import cherrypy

def notify_user(message, category = None, transient = True):
    """Creates a new notification for the current user.
    
    Notifications are stored until a proper page is served to the user. It
    is up to the views to decide how these messages should be displayed.

    @param message: The message that will be shown to the user.
    @type message: unicode

    @param category: An optional free form string identifier that qualifies
        the message. Standard values include 'success' and 'error'.
    @type category: unicode

    @param transient: Indicates if the message should be hidden after a
        short lapse (True), or if it should remain visible until explicitly
        closed by the user (False).
    @type transient: bool
    """
    notifications = cherrypy.session.get("notifications")

    if notifications is None:
        cherrypy.session["notifications"] = notifications = []

    notifications.append((message, category, transient))

def pop_user_notifications():
    """Retrieves pending notification messages that were stored through the
    L{notify_user} method.

    Retrieved messages are considered to be consumed, and therefore they
    are removed from the list of pending notifications.

    @return: The sequence of pending notification messages. Each message
        consists of a tuple with the message text, its category and wether
        or not it should be treated as a transient message.
    @rtype: sequence of (tuple of (unicode, unicode or None, bool))
    """
    notifications = cherrypy.session.get("notifications")
    cherrypy.session["notifications"] = []
    return notifications or []

