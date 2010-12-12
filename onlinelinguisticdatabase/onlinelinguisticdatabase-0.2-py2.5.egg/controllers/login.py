# Copyright (C) 2010 Joel Dunham
#
# This file is part of OnlineLinguisticDatabase.
#
# OnlineLinguisticDatabase is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# OnlineLinguisticDatabase is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with OnlineLinguisticDatabase.  If not, see
# <http://www.gnu.org/licenses/>.

import logging

import hashlib

from pylons import request, response, session, app_globals, tmpl_context as c
from pylons import url
from pylons.controllers.util import abort, redirect
from pylons.decorators.rest import restrict
from pylons.decorators import validate

from formencode.schema import Schema
from formencode.validators import UnicodeString
from formencode import htmlfill

from onlinelinguisticdatabase.lib.base import BaseController, render
import onlinelinguisticdatabase.model as model
import onlinelinguisticdatabase.model.meta as meta
import onlinelinguisticdatabase.lib.helpers as h

log = logging.getLogger(__name__)

class LoginForm(Schema):
    """LoginForm simply validates that both username
    and passwrod have been entered.""" 
    allow_extra_fields = True
    filter_extra_fields = True
    username = UnicodeString(not_empty=True)
    password = UnicodeString(not_empty=True)

class LoginController(BaseController):

    def login(self):
        """Renders the login.html page for authentication.
        login.html calls the authenticate action."""
        return render('/derived/login/login.html')

    @restrict('POST')
    @validate(schema=LoginForm(), form='login')
    def authenticate(self):
        """Checks whether username and password match
        any records in the User table.""" 
        username = self.form_result['username']
        password = hashlib.sha224(self.form_result['password']).hexdigest()
        user_q = meta.Session.query(model.User)
        user = user_q.filter(model.User.username==username).filter(model.User.password==password).first()

        if user:
            # Successful login
            # Update session and app_globals data (function located in lib/functions.py)
            h.updateSessionAndGlobals(user)
            redirect(url(controller='home', action='index'))
        else:
            session['flash'] = 'Authentication failed.'
            return render('/derived/login/login.html')

    def logout(self):
        """Log the user out by destroying the session['user_username']
        variable.  Redirect to home page."""
        if 'user_username' in session:
            del session['user_username']
            del session['user_id']
            del session['user_role']
            del session['user_firstName']
            del session['user_lastName']
            session['flash'] = 'You have been logged out.'
            session.save()
        redirect(url(controller='home', action='index'))

