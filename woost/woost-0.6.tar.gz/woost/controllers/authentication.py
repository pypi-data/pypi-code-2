#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
import cherrypy
from cocktail.modeling import getter
from cocktail.persistence import datastore
from woost.models import User, set_current_user
from woost.controllers.module import Module


class AuthenticationModule(Module):

    SESSION_KEY = "user_id"

    identifier_field = User.email

    def process_request(self):

        params = cherrypy.request.params
    
        session_user_id = cherrypy.session.get(self.SESSION_KEY)
        set_current_user(
            session_user_id and User.get_instance(session_user_id)
            or self.anonymous_user
        )

        if "authenticate" in params:
            self.login(
                params.get("user"),
                params.get("password")
            )
        elif "logout" in params:
            self.logout()

    @getter
    def anonymous_user(self):
        return User.get_instance(qname = "woost.anonymous_user")

    def set_user_session(self, user):
        cherrypy.session[self.SESSION_KEY] = user.id
        set_current_user(user)

    def login(self, identifier, password):
        """Attempts to establish a new user session, using the given user
        credentials.

        @param identifier: An identifier matching a single user in the
            database. Matches are made against the field indicated by the
            L{identifier_field>} attribute.
        @type identifier: str

        @param password: The unencrypted password for the user.
        @type: str

        @return: The authenticated user.
        @rtype: L{User<woost.models.user.User>}

        @raise L{AuthenticationFailedError}: Raised if the provided user
            credentials are invalid.
        """
        identifier = identifier.strip()

        if identifier and password:
            params = {self.identifier_field.name: identifier}
            user = User.get_instance(**params)

            if user and user.enabled and user.test_password(password):            
                self.set_user_session(user)
                return user

        raise AuthenticationFailedError(identifier)

    def logout(self):
        """Ends the current user session."""
        cherrypy.session.clear()
        set_current_user(self.anonymous_user)


class AuthenticationFailedError(Exception):
    """An exception raised when a user authentication attempt fails."""

    def __init__(self, identifier):
        Exception.__init__(self, "Wrong user credentials")
        self.identifier = identifier

