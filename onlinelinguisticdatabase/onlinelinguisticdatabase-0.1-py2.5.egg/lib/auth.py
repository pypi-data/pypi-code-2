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

from decorator import decorator
from pylons import session, request, url
from pylons.controllers.util import redirect

import logging

log = logging.getLogger(__name__)

def authenticate(target):
    """Simple decorator that redirects to the login/login
    action if the user is not logged in.

    Example usage (must be logged in): 
    >@authenticate
    >def actionName(self):
    >   ...
    """
    def wrapper(target, *args, **kwargs):
        if 'user_username' in session and session['user_username'] != None:
            return target(*args, **kwargs)
        else:
            session['flash'] = 'Sorry, you need to be logged in to perform that action.'
            session.save()
            return redirect(url(controller='login', action='login'))
    return decorator(wrapper)(target)

def authorize(roles, users=None, userIDIsArgs1=None):
    """Decorator that redirects to home/index
    action if 
        *   the user does not have one of the roles in roles or 
        *   the user is not one of the users in users or
        *   the user does not have the same id as the id of the entity the action takes as argument

    Example 1: (user must be an administrator or a researcher): 
    >@authorize(['administrator', 'researcher'])
    >def actionName(self):
    >   ...

    Example 2: (user must be either an administrator or the researcher with ID 2): 
    >@authorize(['administrator', 'researcher'], [2])
    >def actionName(self):
    >   ...

    Example 3: (user must have the same ID as the entity she is trying to affect): 
    >@authorize(['administrator', 'researcher', 'learner'], userIDIsArgs1=True)
    >def actionName(self, id):
    >   ...
    """
    def wrapper(func, *args, **kwargs):
        # check for authorization via role
        if 'user_role' in session and session['user_role'] in roles:
            # check for authorization via user
            if users:
                if session['user_role'] is not 'administrator' and session['user_id'] not in users:
                    session['flash'] = 'Sorry, you do not have permission to perform that action.'
                    session.save()
                    print '\n\n\nProblem 1\n\n\n'
                    return redirect(url(controller='home', action='index'))
            # check whether user id is equal to the id argument given to the target function
            # this is useful for cases where a user can only edit their own personal page
            if userIDIsArgs1:
                if session['user_role'] != 'administrator' and int(session['user_id']) != int(args[1]):
                    session['flash'] = 'Sorry, you do not have permission to perform that action.'
                    session.save()
                    print '\n\n\nProblem 2:\n\n\tYour id is %s but the first arg is %s\n\n\n' % (int(session['user_id']), int(args[1]))
                    return redirect(url(controller='home', action='index'))
            return func(*args, **kwargs)
        else:
            session['flash'] = 'Sorry, you do not have permission to perform that action.'
            session.save()
            print '\n\n\nProblem 3\n\n\n'
            return redirect(url(controller='home', action='index'))
    return decorator(wrapper)
