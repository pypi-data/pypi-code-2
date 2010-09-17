"""
Utilities useful in django views.

Usage::

  from djview import *

This will import several utility functions, as well as the functions
and objects one most often needs in Django views.

"""

# private imports
import datetime as _datetime

from django.db.models import Manager as _Manager
from django.template import RequestContext as _rc

import djview.jsonutil as _jsonutil
from djview.qsutil import *

# public imports -- available in from viewutil import *
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.core.urlresolvers import reverse
from django.http import (Http404,
                         HttpResponse,
                         HttpResponseBadRequest,
                         HttpResponseForbidden,
                         HttpResponseGone,
                         HttpResponseNotAllowed,
                         HttpResponseNotFound,
                         HttpResponseNotModified,
                         HttpResponsePermanentRedirect,
                         HttpResponseRedirect,
                         HttpResponseServerError)
from django.shortcuts import get_object_or_404, render_to_response
from django.template.loader import render_to_string
from django.views.decorators.cache import cache_page


def render_with_request(template, data, request, mimetype=None):
    return render_to_response(template,
                              data,
                              context_instance=_rc(request),
                              mimetype=mimetype)


def resolve_date(year, month='jan', day='01'):
    try:
        return _datetime.datetime.strptime("%s/%s/%s" % (year, month, day),
                                           '%Y/%b/%d').date()
    except (ValueError, TypeError):
        return None


def resolve_date_or_404(year, month='jan', day='01'):
    day = resolve_date(year, month, day)
    if not day:
        raise Http404
    return day


def paginate_or_404(queryset, page, num_per_page=20):
    """
    paginate a queryset (or other iterator) for the given page,
    returning the paginator and page object.  Raises a 404 for an
    invalid page.
    """
    if page is None:
        page = 1
    paginator = Paginator(queryset, num_per_page)
    try:
        page_obj = paginator.page(page)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    except InvalidPage:
        raise Http404
    return paginator, page_obj


def get_int_or_404(value):
    """
    cast a value as an integer, or raise a 404.
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        raise Http404


def get_object_or_None(model_or_manager, **kwargs):
    mgr = (model_or_manager
           if isinstance(model_or_manager, _Manager)
           else model_or_manager._default_manager)
    try:
        return mgr.get(**kwargs)
    except ObjectDoesNotExist:
        return None


def url_for(route, **kwargs):
    return reverse(route, kwargs=kwargs)


def json(func):
    def wrapper(request, *args, **kwargs):
        res = func(request, *args, **kwargs)
        if isinstance(res, HttpResponse):
            return res
        else:
            data = _jsonutil.dumps(res)
            return HttpResponse(data, mimetype='application/json')
    return wrapper


def jsonp(func):
    def wrapper(request, *args, **kwargs):
        res = func(request, *args, **kwargs)
        if isinstance(res, HttpResponse):
            return res
        elif request.method == 'GET' and 'callback' in request.GET:
            body = u'%s(%s)' % (request.GET['callback'],
                                _jsonutil.dumps(res))
            return HttpResponse(body, mimetype='text/javascript')
        else:
            data = _jsonutil.dumps(res)
            return HttpResponse(data, mimetype='application/json')
    return wrapper
