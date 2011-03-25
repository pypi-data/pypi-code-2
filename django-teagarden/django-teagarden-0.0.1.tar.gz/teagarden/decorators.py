# -*- coding: utf-8 -*-

import logging
import urllib

from django.http import (
    HttpResponse,
    HttpResponseNotFound,
    HttpResponseRedirect,
    HttpResponseForbidden)

from teagarden import models

### Generic decorators ###

def get_required(func):
    """Decorator that returns an error unless request.method == 'POST'."""

    def get_wrapper(request, *args, **kwds):
        if request.method != "GET":
            return HttpResponse("This requires a GET request.", status=405)
        return func(request, *args, **kwds)
    return get_wrapper
    
    
def field_required(func):
    def field_wrapper(request, field_id, *args, **kwds):
        field = models.Field.objects.filter(id=int(field_id))
        if not field:
            return HttpResponseNotFound("No field exists with that id (%s)" %
                                        field_id)
        request.field = field[0]
        return func(request, *args, **kwds)
    return field_wrapper


def login_required(func):
    """Decorator that redirects to the login page if you're not logged in."""

    def login_wrapper(request, *args, **kwds):
        if request.user is None or request.user.is_anonymous():
            return HttpResponseRedirect("/signin")
        return func(request, *args, **kwds)
    return login_wrapper


def post_required(func):
    """Decorator that returns an error unless request.method == 'POST'."""

    def post_wrapper(request, *args, **kwds):
        if request.method != 'POST':
            return HttpResponse('This requires a POST request.', status=405)
        return func(request, *args, **kwds)
    return post_wrapper


def project_required(func):
    def project_wrapper(request, project_id, *args, **kwds):
        project = models.Project.objects.filter(id=int(project_id))
        if not project:
            return HttpResponseNotFound("No project exists with that id (%s)" %
                                        project_id)
        request.project = project[0]
        return func(request, *args, **kwds)
    return project_wrapper


def table_required(func):
    def table_wrapper(request, table_id, *args, **kwds):
        table = models.Table.objects.filter(id=int(table_id))
        if not table:
            return HttpResponseNotFound("No table exists with that id (%s)" %
                                        table_id)
        request.table = table[0]
        return func(request, *args, **kwds)
    return table_wrapper


def user_key_required(func):
    """Decorator that processes the user handler argument."""

    def user_key_wrapper(request, user_key, *args, **kwds):
        user_key = urllib.unquote(user_key)
        if "@" in user_key:
            request.user_to_show = models.Account.objects.filter(email=user_key)[0]
        else:
            users = models.Account.objects.filter(id=user_key)
            if not users:
                logging.info("Account not found for nickname %s" % user_key)
                return HttpResponseNotFound('No user found with that key (%s)' %
                                            user_key)
            request.user_to_show = users[0]
        return func(request, *args, **kwds)
    return user_key_wrapper
