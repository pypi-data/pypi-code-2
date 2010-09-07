# -*- coding: utf-8 -*-

"""Module for JSON functions."""

import calendar
import datetime
import logging
from time import mktime

from django.core import serializers
from django.core.cache import cache
from django.db.models import Sum
from django.http import (
    HttpResponse,
    HttpResponseRedirect,
    HttpResponseNotFound,)
from django.utils import simplejson
from django.utils.translation import ugettext as _

import models
from decorators import get_required

from issues.models import Issue, IssueUser, Tracker


def _clean_int(value, default, min_value=None, max_value=None):
    """Helper to cast value to int and to clip it to min or max_value.

    :param value: Any value (preferably something that can be casted to int).
    :param default: Default value to be used when type casting fails.
    :param min_value: Minimum allowed value (default: None).
    :param max_value: Maximum allowed value (default: None).

    :returns: An integer between min_value and max_value.
    """
    if not isinstance(value, (int, long)):
        try:
            value = int(value)
        except (TypeError, ValueError), err:
            value = default
    if min_value is not None:
        value = max(min_value, value)
    if max_value is not None:
        value = min(value, max_value)
    return value


@get_required
def get_customer_projects(request):
    data = []
    index = request.GET.get('index')
    account = request.user.account
    try:
        customer = models.Customer.get_by_id(index)
    except models.Customer.DoesNotExist:
        customer = None
    if customer:
        data = models.Project.objects.get_by_customer(
            customer=customer, active_only=True, user=request.user)
    else:
        data = models.Project.get_by_id(1)
    data = serializers.serialize('json', data, fields=('name',))
    return HttpResponse(data, mimetype='application/json')


@get_required
def get_project_steps(request):
    data = []
    index = request.GET.get('index')
    try:
        project = models.Project.objects.get(id=index)
    except models.Project.DoesNotExist:
        project = None
    if project:
        data = project.get_project_steps()
    data = serializers.serialize('json', data, fields=('name',))
    return HttpResponse(data, mimetype='application/json')


@get_required
def get_project_tracker(request):
    data = []
    index = request.GET.get('index')
    try:
        project = models.Project.objects.get(id=index)
    except models.Project.DoesNotExist:
        project = None
    if project:
        data = Tracker.objects.filter(projecttracker__project=project)
    data = serializers.serialize('json', data, fields=('name',))
    return HttpResponse(data, mimetype='application/json')


@get_required
def get_project_graph(request, project_id):
    """Displays a graph of working time for a project and the current year."""
    data = []

    today = datetime.date.today()
    first_day = datetime.date(today.year, 1, 1)
    last_day = datetime.date(today.year, 12, calendar.monthrange(today.year, 12)[1])

    for m in xrange(1, 13):
        for d in xrange(1, calendar.monthrange(today.year, m)[1] + 1):
            #date = first_day + datetime.timedelta(days=d)
            date = datetime.date(today.year, m, d)
            data.append({'date': date.strftime('%Y-%m-%d'), 'duration': 0})

    project = models.Project.get_by_id(project_id)
    query = models.Booking.objects.values('day__date').annotate(Sum(
            'duration'))
    query = query.filter(day__user=request.user, project=project)
    query = query.filter(day__date__gte=first_day,
                         day__date__lte=last_day)
    query = query.order_by('day__date')
    for booking in query:
        for dct in data:
            if dct['date'] == booking.get('day__date').strftime('%Y-%m-%d'):
                dct['duration'] = float(booking.get('duration__sum') / 60)
    data = simplejson.dumps(data)
    return HttpResponse(data, mimetype='application/json')


@get_required
def get_weekly_graph(request, year=None, month=None, day=None):
    """Retrieve the data for a weekly workting time graph.

    :param year: Year as an Integer
    :param month: Month as asn Integer
    :param day: Day as an Integer

    :returns: Serialized dictionary with working time information.

    :raises HttpResponseNotFound: Whenever date information is invalid
    """
    try:
        today = datetime.date(int(year), int(month), int(day))
    except ValueError:
        return HttpResponseNotFound()
    data = []
    week_day = today.weekday()
    first_day = today - datetime.timedelta(days=week_day + 1)
    last_day = today + datetime.timedelta(days=7 - (week_day + 1))
    for n in xrange(1, 8):
        date = first_day + datetime.timedelta(days=n)
        data.append({'date': date.strftime('%Y-%m-%d'), 'duration': 0})
    query = models.Booking.objects.values('day__date').annotate(Sum('duration'))
    query = query.filter(day__user=request.user)
    query = query.filter(day__date__gte=first_day,
                         day__date__lte=last_day)
    query = query.order_by('day__date')
    for booking in query:
        for dct in data:
            if dct['date'] == booking.get('day__date').strftime('%Y-%m-%d'):
                dct['duration'] = float(booking.get('duration__sum') / 60)
    # As we do not serialize Django model data, we must use the direct dump
    # string method of json.
    data = simplejson.dumps(data)
    return HttpResponse(data, mimetype='application/json')


@get_required
def issue(request):
    """Search for an issue."""
    def search_issues(tracker_id, query, property, added, response):
        # TODO: Immer noch case-sensitive
        account = request.user.account
        try:
            tracker = Tracker.objects.filter(id=tracker_id)
        except System.DoesNotExist:
            return added, response
        limit = _clean_int(request.GET.get('limit'), 10, 10, 100)
        kwargs = {'issue__%s__contains' % property: query}
        issue_users = IssueUser.objects.filter(**kwargs)
        issue_users = issue_users.filter(user=request.user,
                                         issue__tracker=tracker)
        issue_users = issue_users.order_by('issue__no')
        for iu in issue_users:
            if iu.issue.id in added:
                continue
            if len(added) >= limit:
                break
            added.add(iu.issue.id)
            response += '#%s (%s)\n' % (iu.issue.no, iu.issue.title)
        return added, response
    added = set()
    tracker_id = request.GET.get('tracker')
    query = request.GET.get('q')
    response = cache.get('issue_search:%s/%s->%s' % (request.user.id,
                                                     tracker_id, query))
    if response is None:
        logging.debug('Missing cache entry for issue search: User: %s, Tracker:'
                      ' %s, Query: %s',
                      request.user, tracker_id, query)
        response = ''
        added, response = search_issues(tracker_id, query, 'title', added,
                                        response)
        added, response = search_issues(tracker_id, query, 'no', added,
                                        response)
        cache.set('issue_search:%s/%s->%s' % (request.user.id, tracker_id,
                                              query), response)
    return HttpResponse(response)