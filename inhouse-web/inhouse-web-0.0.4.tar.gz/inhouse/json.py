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
    """Returns the projects of a customer.

    :returns: :class:`HttpResponse`
    """
    data = []
    ids = set()
    index = _clean_int(request.GET.get('index'), -1)
    account = request.user.account
    try:
        customer = models.Customer.get_by_id(index)
    except models.Customer.DoesNotExist:
        customer = None
    if customer:
        query = models.Project.objects.get_by_customer(
            customer=customer, active_only=True,
            user=request.user)
        for project in query:
            if project.get_project_steps(active_only=True).count() > 0:
                ids.add(project.id)
        data = models.Project.objects.filter(id__in=ids).order_by('name')
    data = serializers.serialize('json', data, fields=('name',))
    return HttpResponse(data, mimetype='application/json')


@get_required
def get_project_steps(request):
    """Returns a project's steps.

    :returns: :class:`HttpResponse`
    """

    # [{"pk": 1, "model": "inhouse.projectstep", "fields": {"name": "Entwicklung"}}]

    data = []
    index = _clean_int(request.GET.get('index'), -1)
    with_default = _clean_int(request.GET.get('with_default'), 0)
    try:
        project = models.Project.objects.get(id=index)
    except models.Project.DoesNotExist:
        project = None
    if project:
        #data = project.get_project_steps()
        for step in project.get_project_steps():
            if with_default:
                default = step.is_default(request.user)
            else:
                default = False
            data.append({'pk': step.id, 'model': 'inhouse.projectstep',
                         'fields': {'name': step.name,
                                    'default': default}})
    print data

    #data = serializers.serialize('json', data, fields=('name',))
    data = simplejson.dumps(data)
    return HttpResponse(data, mimetype='application/json')


@get_required
def get_default_projectstep(request):
    data = []
    index = _clean_int(request.GET.get('index'), -1)
    try:
        project = models.Project.objects.get(id=index)
    except models.Project.DoesNotExist:
        project = None
    query = models.ProjectUser.objects.filter(project=project,
                                              user=request.user)
    if query.count() == 1:
        query = query[0]
        steps = models.ProjectStep.objects.filter(id=query.default_step.id)
        if steps.count() == 1 and not steps[0].is_closed():
            data = steps
    data = serializers.serialize('json', data, fields=('name',))
    return HttpResponse(data, mimetype='application/json')


@get_required
def get_project_tracker(request):
    """Returns a project's available issue trackers.

    :returns: :class:`HttpResponse`
    """
    data = []
    index = _clean_int(request.GET.get('index'), -1)
    try:
        project = models.Project.objects.get(id=index)
    except models.Project.DoesNotExist:
        project = None
    if project:
        data = Tracker.objects.filter(projecttracker__project=project)
    data = serializers.serialize('json', data, fields=('name',))
    return HttpResponse(data, mimetype='application/json')


@get_required
def issue(request):
    """Search for an issue."""
    def search_issues(tracker_id, query, property, added, response):
        account = request.user.account
        try:
            tracker = Tracker.objects.filter(id=tracker_id)
            tracker = tracker[0]
        except (Tracker.DoesNotExist, ValueError, IndexError):
            return added, response
        limit = _clean_int(request.GET.get('max_matches'), 10, 10, 100)
        # TODO: Filter tickets by user according to system config?
        # TODO: Filtering by user only available with user mapping!
        #kwargs = {'issue__%s__contains' % property: query}
        #issue_users = IssueUser.objects.filter(**kwargs)
        ##issue_users = issue_users.filter(user=request.user,
                                         ##issue__tracker=tracker)
        #issue_users = issue_users.order_by('-issue__no')
        #print issue_users.count()
        #for iu in issue_users:
            #if iu.issue.id in added:
                #continue
            #if len(added) >= limit:
                #break
            #added.add(iu.issue.id)
            ##response += '#%s (%s)\n' % (iu.issue.no, iu.issue.title)
            #response.append('#%s (%s)\n' % (iu.issue.no, iu.issue.title))
        kwargs = {'%s__contains' % property: query}
        issues = Issue.objects.filter(**kwargs)
        issues = issues.filter(tracker=tracker)
        issues = issues.order_by('-no')
        for issue in issues:
            if issue.id in added:
                continue
            if len(added) >= limit:
                break
            added.add(issue.id)
            response.append('#%s (%s)\n' % (issue.no, issue.title))

        return added, response
    added = set()
    tracker_id = request.GET.get('tracker')
    query = request.GET.get('token')
    if query.startswith('#'):
        query = query[1:]
    response = cache.get('issue_search:%s/%s->%s' % (request.user.id,
                                                     tracker_id, query))
    if response is None:
        logging.debug('Missing cache entry for issue search: User: %s, Tracker:'
                      ' %s, Query: %s',
                      request.user, tracker_id, query)
        #response = ''
        response = []
        added, response = search_issues(tracker_id, query, 'title', added,
                                        response)
        added, response = search_issues(tracker_id, query, 'no', added,
                                        response)
        cache.set('issue_search:%s/%s->%s' % (request.user.id, tracker_id,
                                              query), response)
    #return HttpResponse(response)
    data = simplejson.dumps(response)
    return HttpResponse(data, mimetype='application/json')


@get_required
def location(request):
    """Provide a list of used location strings for a booking."""
    query = request.GET.get('token')
    added = set()
    limit = _clean_int(request.GET.get('max_matches'), 10, 10, 100)
    bookings = models.Booking.objects.values('location')
    bookings = bookings.filter(day__user=request.user)
    if query:
        bookings = bookings.filter(location__icontains=query)
    bookings = bookings.exclude(location__exact='')
    #bookings = bookings.order_by('location')
    for booking in bookings:
        if booking['location'] in added:
            continue
        if len(added) >= limit:
            break
        added.add(booking['location'])
    data = list(added)
    data.sort()
    data = simplejson.dumps(data)
    return HttpResponse(data, mimetype='application/json')

