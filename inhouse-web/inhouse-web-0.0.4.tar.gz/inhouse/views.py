# -*- coding: utf-8 -*-

import datetime
import logging
import os
from time import mktime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import (
    login_required,
    permission_required,)
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.db.models import Sum
from django.http import (
    HttpResponse,
    HttpResponseNotFound,
    HttpResponseRedirect,)
from django.shortcuts import get_object_or_404, render_to_response
import django.template
from django.utils.translation import ugettext as _
from django.utils import formats

from decorators import (
    booking_required,
    booking_owner_required,
    booking_key_required,
    get_required,
    post_required,
    timer_required,
    user_key_required)
import forms
import models


DEBUG = 'INHOUSEWEB_DEBUG' in os.environ


def respond(request, template, params=None):
    """Helper to render a response, passing standard stuff to the response.

    :params request: The request object.
    :params template: The template name; '.html' is appended automatically.

    :returns: Whatever render_to_response(template, params) returns.

    :raises:  Whatever render_to_response(template, params) raises.
    """
    #global counter
    #counter += 1
    if params is None:
        params = {}
    must_choose_nickname = False
    if request.user is not None:
        account = models.Account.current_user_account
        #must_choose_nickname = not account.user_has_selected_nickname()
    #params['request'] = request
    #params['counter'] = counter
    #params['user'] = request.user
    #params['account'] = account
    # FIXME: is_dev und debug korrekt ermitteln
    params['is_dev'] = True
    #params['debug'] = DEBUG
    params['debug'] = True

    full_path = request.get_full_path().encode('utf-8')
    #if request.user is None:
        #params['sign_in'] = users.create_login_url(full_path)
    #else:
        #params['sign_out'] = users.create_logout_url(full_path)
    #params['must_choose_nickname'] = must_choose_nickname
    today = datetime.date.today()
    params['today'] = today
    if (not 'calendar_month' in request.session
        or not request.session['calendar_month']):
        request.session["calendar_month"] = today.month
    if (not 'calendar_year' in request.session
        or not request.session['calendar_year']):
        request.session['calendar_year'] = today.year
    if request.method == "GET":
        if "calendar_month" in request.GET:
            request.session["calendar_month"] = request.GET.get(
                "calendar_month", None)
        if "calendar_year" in request.GET:
            request.session["calendar_year"] = request.GET.get(
                "calendar_year", None)
    try:
        return render_to_response(
            template, params,
            context_instance=django.template.RequestContext(request))
    except MemoryError:
        logging.exception('MemoryError')
        return HttpResponse('MemoryError', status=503)
    except AssertionError:
        logging.exception('AssertionError')
        return HttpResponse('AssertionError')


def _booking_popup(request):
    booking = request.booking_to_show
    #popup_html = cache.get("user_popup:%d" % user.id)
    #if popup_html is None:
        #logging.debug("Missing cache entry for user_popup:%d", user.id)
        #popup_html = render_to_response('booking_popup.html',
                                        #{'booking': booking})
        #cache.set("user_popup:%d" % user.id, popup_html, 60)
    popup_html = render_to_response('booking_popup.html',
                                    {'booking': booking})
    return popup_html


@booking_key_required
def booking_popup(request):
    """Pop up to show the user info."""
    try:
        return _booking_popup(request)
    except Exception, err:
        logging.exception('Exception in booking_popup processing:')
        # Return HttpResponse because the JS part expects a 200 status code.
        return HttpResponse('<font color="red">Error: %s; please report!</font>' %
                            err.__class__.__name__)


def index(request):
    """The main index page."""
    if request.user is None:
        return HttpResponseRedirect(settings.LOGIN_URL)
    else:
        return dashboard(request)


@login_required
def company(request):
    """Displays the user`s company information"""
    user_profile = request.user.get_profile()
    if not user_profile.company:
        return HttpResponseNotFound('The user is not assigned with any company')
    company = user_profile.company
    return respond(request, 'company.html', {
        'company': company})


@login_required
def dashboard(request):
    """Show the user`s dashboard."""
    current_news =  models.News.objects.get_current(request.user)
    return respond(request, 'dashboard.html', {'news': current_news})


@permission_required('inhouse.change_userprofile')
def _edit_profile(request):
    """Edit the user`s profile."""
    user = request.user
    if request.method != 'POST':
        try:
            user_profile = user.get_profile()
        except models.UserProfile.DoesNotExist:
            user.account.create_profile()
            user_profile = user.get_profile()
        initial = {'first_name': user.first_name,
                   'last_name': user.last_name,
                   'email': user.email,
                   'street': user_profile.address.street,
                   'zip_code': user_profile.address.zip_code,
                   'city': user_profile.address.city,
                   'country': user_profile.address.country.id,
                   'birthday': user_profile.birthday,
                   'phone_landline': user_profile.communication.phone_landline,
                   'phone_mobile': user_profile.communication.phone_mobile,
                   'fax': user_profile.communication.fax,
                   'url': user_profile.communication.url,
                   'job': user_profile.job,
                   'personnel_no': user_profile.personnel_no}
        if user_profile.company is not None:
            initial.update({'company': user_profile.company.id})
        form = forms.UserProfileForm(initial=initial)
        form.set_country_choices()
        form.set_company_choices()
        return respond(request, 'profile.html', {
            'form': form})
    form = forms.UserProfileForm(request.POST)
    form.set_country_choices()
    form.set_company_choices()
    if form.is_valid():
        user_profile = user.get_profile()
        user.first_name = form.cleaned_data['first_name']
        user.last_name = form.cleaned_data['last_name']
        user.email = form.cleaned_data['email']
        user_profile.job = form.cleaned_data['job']
        user_profile.company = models.Company.get_by_id(form.cleaned_data['company'])
        address = user_profile.address
        if user.first_name and user.last_name:
            address.name1 = '%s %s' % (user.first_name, user.last_name)
            user_profile.short_name = models.Account.get_short_name(user)
        address.street = form.cleaned_data['street']
        address.zip_code = form.cleaned_data['zip_code']
        address.city = form.cleaned_data['city']
        country = models.Country.get_by_id(form.cleaned_data['country'])
        address.country = country
        address.save(user=user)
        communication = user_profile.communication
        communication.email = user.email
        communication.phone_landline = form.cleaned_data['phone_landline']
        communication.phone_mobile = form.cleaned_data['phone_mobile']
        communication.fax = form.cleaned_data['fax']
        communication.url = form.cleaned_data['url']
        communication.save(user=user)
        user_profile.save(user=user)
        user.save()
        messages.success(request,
                         _(u'Your profile has been sucessfully updated.'))
        #return HttpResponseRedirect(reverse('inhouse.views.dashboard'))
        return respond(request, 'profile.html', {'form': form})
    else:
        return respond(request, 'profile.html', {'form': form})


@booking_owner_required
@permission_required('inhouse.change_booking')
def edit_booking(request):
    booking = request.booking
    if request.method == 'POST':
        if 'cancel' in request.POST:
            messages.add_message(request, messages.INFO,
                                 _(u'Your changes have been discarded.'))
            return HttpResponseRedirect('/time/%s' % booking.day.slugify())
        form = _save_booking(request, booking.id)
        if form.is_valid():
            messages.add_message(request, messages.INFO,
                                 _(u'Booking %s has been updated.')
                                 % booking.get_key())
            return HttpResponseRedirect('/time/%s' % booking.day.slugify())
    else:
        hours, minutes = booking.split_duration()
        initial = {
            'customer': booking.project.customer.id,
            'project': booking.project.id,
            'step': booking.step.id,
            'date': booking.day.date,
            'hours': hours,
            'minutes': minutes / 15,
            'title': booking.title,
            'description': booking.description,
            'location': booking.location}
        if booking.issue:
            initial.update({
                'tracker': booking.issue.tracker.id,
                'issue_no': booking.issue.no})
        form = forms.BookingForm(initial=initial, request=request)
        form.set_customer_choices(request.user)
        form.set_project_choices(request.user, booking.project.customer)
        form.set_step_choices(request.user, booking.project)
        form.set_tracker_choices(request.user, booking.project)
    return respond(request, 'booking.html', {
        'form': form,
        'booking': booking,
        'expand_boxes': True,
        'page_title': _(u'Edit booking'),
        'cancel_value': _(u'Cancel'),
        'submit_value': _(u'Save booking') })


@login_required
def edit_profile(request):
    """Edit the user`s profile"""
    return _edit_profile(request)


def _save_booking(request, booking_id=None):
    """Creates a new booking entry.

    :param request: Request instance
    """
    form = forms.BookingForm(request.POST, request=request)
    form.set_customer_choices(request.user)
    form.set_project_choices(request.user,
                             request.POST.get('customer', None))
    form.set_step_choices(request.user,
                          request.POST.get('project', None))
    form.set_tracker_choices(request.user,
                             request.POST.get('project', None))
    if form.is_valid():
        if booking_id:
            booking = models.Booking.get_by_id(booking_id)
        else:
            booking = models.Booking()
        day = request.user.account.get_day(form.cleaned_data['date'])
        booking.day = day
        project = models.Project.get_by_id(form.cleaned_data['project'])
        step = models.ProjectStep.get_by_id(form.cleaned_data['step'])
        booking.project = project
        booking.step = step
        booking.duration = int(form.cleaned_data['minutes']) \
               * 15 + int(form.cleaned_data['hours']) * 60
        booking.from_time = form.cleaned_data['from_time']
        booking.to_time = form.cleaned_data['to_time']
        booking.title = form.cleaned_data['title']
        booking.description = form.cleaned_data['description']
        booking.location = form.cleaned_data['location']
        try:
            issue_no = int(form.cleaned_data.get('issue_no'))
        except:
            issue_no = 0
        try:
            tracker = int(form.cleaned_data.get('tracker'))
        except:
            tracker = 0
        if issue_no and tracker:
            booking.set_issue(tracker, issue_no)
        booking.next_position()
        coefficient = project.get_coefficient(step, day)
        # TODO: Different external coefficient?
        booking.coefficient = coefficient
        booking.external_coefficient = coefficient
        booking.save(user=request.user)
    return form


@login_required
@permission_required('inhouse.add_booking')
def new_booking(request, year=None, month=None, day=None):
    """Create a new booking entry.

    :param year: Year of the booking
    :param month: Month of the booking
    :param day: Day of the booking
    """
    try:
        date = datetime.date(int(year), int(month), int(day))
    except ValueError:
        return HttpResponseNotFound()
    day = request.user.account.get_day(date)
    if day.locked:
        return HttpResponseNotFound()
    expand_boxes = False
    timer = None
    if request.method == 'POST':
        if 'cancel' in request.POST:
            messages.add_message(request, messages.INFO,
                                 _(u'Your changes have been discarded.'))
            return HttpResponseRedirect('/time/%s' % day.slugify())
        form = _save_booking(request)
        if form.is_valid():
            messages.add_message(request, messages.INFO,
                                 _(u'Booking has been added.'))
            return HttpResponseRedirect('/time/%s' % day.slugify())
    else:
        initial = {}
        if 'timer_id' in request.GET:
            timer = models.Timer.get_by_id(request.GET['timer_id'])
            if timer.created_by != request.user:
                return HttpResponseNotFound(
                    'Timer doesn\'t belong to the current user.')
            hours, minutes = timer.get_time_tuple()
            initial.update({'title': timer.title,
                            'hours': hours,
                            'minutes': minutes / 15})
        initial.update({'date': date})
        form = forms.BookingForm(initial=initial, request=request)
        form.set_customer_choices(request.user)
        form.set_project_choices(request.user)
        form.set_step_choices(request.user)
        form.set_tracker_choices(request.user)
    if form.errors:
        expand_boxes = True
    return respond(request, 'booking.html', {
        'form': form,
        'expand_boxes': expand_boxes,
        'date': date,
        'page_title': _(u'New booking'),
        'cancel_value': _(u'Cancel'),
        'submit_value': _(u'Save booking'),})


@login_required
def phone_list(request):
    """Display employee contact information for the user's company."""
    user_profile = request.user.get_profile()
    if not user_profile.company:
        return HttpResponseNotFound(
            'The user is not assigned with any company')
    userids = []
    company = user_profile.company
    query = User.objects.all().order_by('last_name')
    for user in query:
        try:
            profile = user.get_profile()
            if profile.company != company:
                continue
            userids.append(user.id)
        except models.UserProfile.DoesNotExist:
            continue
    employees = User.objects.filter(id__in=userids)
    return respond(request, 'phone_list.html', {
        'employees': employees})


def _delete_bookings(request):
    """Delete on or more bookings."""
    booking_ids = request.POST.getlist('booking_ids')
    request.session['undo_bookings'] = []
    for id in booking_ids:
        request.session['undo_bookings'].append(id)
    query = models.Booking.objects.filter(id__in=booking_ids)
    query.delete()


def _copy_bookings(request):
    """Copy on or more bookings to the next day."""
    booking_ids = request.POST.getlist('booking_ids')
    for id in booking_ids:
        booking = models.Booking.get_by_id(id)
        copy = booking.copy(request.user)
        copy.save(user=request.user)


@login_required
def show_day(request, year=None, month=None, day=None):
    """Display the bookings of a day and provide actions.

    :param year: Year of the date to be displayed
    :param month: Month of the date to be displayed
    :param day: Day of the date to be displayed
    """
    booking_ids = request.POST.getlist('booking_ids')
    if request.method == 'POST' and len(booking_ids) > 0:
        if 'delete' in request.POST:
            _delete_bookings(request)
            messages.add_message(request, messages.INFO,
                                 u'%s <a href="/time/undo">%s</a>'
                                 % (_(u'The booking(s) have been successfully'
                                      u' deleted.'),
                                    _(u'Undo')))
        elif 'copy' in request.POST:
            _copy_bookings(request)
            messages.add_message(request, messages.INFO,
                                 _(u'The booking(s) have been copied to the'
                                   u' next day.'))
    try:
        date = datetime.date(int(year), int(month), int(day))
    except ValueError:
        return HttpResponseNotFound()
    _prev = date - datetime.timedelta(days=1)
    _next = date + datetime.timedelta(days=1)
    day = request.user.account.get_day(date)
    bookings = models.Booking.objects.select_related().filter(
        day=day).order_by('position')
    return respond(request, 'day.html', {
        'date': date, 'bookings': bookings, 'day': day, 'prev_date': _prev,
        'next_date': _next})


def _revert_booking(request, history_id):
    history = models.BookingHistory.get_by_id(history_id)
    try:
        booking = history.booking
    except models.Booking.DoesNotExist:
        # Create the booking if it has been deleted
        # FIXME: Das Erstellen in die BookingHistory Klasse legen
        booking = models.Booking()
        booking.created = datetime.datetime.now()
        booking.created_by = request.user
    booking.revert(history)
    booking.save(user=request.user)
    history.booking_id = booking.id
    history.save(user=request.user)


@login_required
@booking_required
def show_history(request):
    booking = request.booking
    if request.method == 'POST':
        if 'cancel' in request.POST:
            return HttpResponseRedirect('/time/%s' % booking.day.slugify())
        elif 'revert' in request.POST:
            if not 'history_id' in request.POST:
                messages.warning(request,
                                 _(u'No history entry selected.'))
            else:
                _revert_booking(request, request.POST['history_id'])
                messages.success(
                    request, _(u'The booking has been successfully reverted.'))
                return HttpResponseRedirect('/time/%s' % booking.day.slugify())
    histories = models.BookingHistory.objects.filter(booking_id=booking.id)
    histories = histories.order_by('-created')
    return respond(request, 'booking_history.html', {
        'booking': booking,
        'cancel_value': _(u'Go back'),
        'histories': histories})

@login_required
def show_projects(request):
    """Displays the user's projects."""
    form = forms.ProjectRequestForm()
    form.set_project_choices(request.user)
    projects = models.Project.objects.get_by_user(request.user,
                                                  active_only=False)
    projects = projects.order_by('project__customer')
    inactive_projects = projects.filter(status__in=models.PROJECT_INACTIVE_STATUS)
    active_projects = projects.filter(status__in=models.PROJECT_ACTIVE_STATUS)
    return respond(request, 'projects.html', {
        'form': form,
        'active_projects': active_projects,
        'inactive_projects': inactive_projects})

@login_required
def show_project(request, project_id):
    try:
        project = models.Project.get_by_id(project_id)
    except models.Project.DoesNotExist:
        return HttpResponseNotFound('No project found with that key (%s)'
                                    % project_id)
    participants = project.get_members().order_by('username')
    return respond(request, 'project.html', {'project': project,
                                             'participants': participants})


@login_required
def show_yesterday(request):
    date = datetime.date.today() - datetime.timedelta(days=1)
    return HttpResponseRedirect(reverse('inhouse.views.show_day',
                                        args=[date.year, date.month,
                                              date.day]))

@login_required
def show_today(request):
    """Redirect to the current date."""
    date = datetime.date.today()
    return HttpResponseRedirect(reverse('inhouse.views.show_day',
                                        args=[date.year, date.month,
                                              date.day]))

@login_required
def show_tomorrow(request):
    date = datetime.date.today() + datetime.timedelta(days=1)
    return HttpResponseRedirect(reverse('inhouse.views.show_day',
                                        args=[date.year, date.month,
                                              date.day]))


@login_required
def show_user(request, user_id):
    """Displays the public user information.

    :param user_id: Id of the user to show
    """
    user = User.objects.filter(id=user_id)
    if user.count() == 0:
        return HttpResponseNotFound('The user cannot be found')
    else:
        user = user[0]
    projects = models.Project.objects.get_by_user(
        user, active_only=False).order_by('name')
    departments = models.Department.objects.get_by_user(user).order_by('name')
    return respond(request, 'user.html', {
        'user_to_show': user,
        'projects': projects,
        'departments': departments})


@login_required
def show_week(request, year, month, day):
    """Displays a weekly overview."""
    days = []
    day_data = []
    sum_data = []
    week_sum = 0
    try:
        day = datetime.date(int(year), int(month), int(day))
    except ValueError:
        return HttpResponseNotFound()
    #day = datetime.date.today()
    week_day = day.weekday()
    first_day = day - datetime.timedelta(days=week_day)
    last_day = day + datetime.timedelta(days=7 - (week_day + 1))
    for n in xrange(0, 7):
        date = first_day + datetime.timedelta(days=n)
        days.append(date)
        day_data.append([date, []])
        x = request.user.account.get_day(date)
        sum_data.append(x.get_booking_sum())
        week_sum += x.get_booking_sum()
    bookings = models.Booking.objects.select_related().filter(
        day__user=request.user,
        day__date__gte=first_day,
        day__date__lte=last_day)
    bookings = bookings.order_by('position')
    for booking in bookings:
        day_data[booking.day.date.weekday()][1].append(booking)
    next_day = first_day + datetime.timedelta(days=7)
    previous_day = first_day - datetime.timedelta(days=7)
    return respond(request, 'week.html', {
        'days': days,
        'day_data': day_data,
        'first_day': first_day,
        'last_day': last_day,
        'sum_data': sum_data,
        'week_sum': week_sum,
        'next_day': next_day,
        'previous_day': previous_day})


#@post_required
@login_required
@booking_required
def star_booking(request):
    account = models.Account.current_user_account
    if account.starred_bookings is None:
        account.starred_bookings = []
    id = request.booking.id
    if id not in account.starred_bookings:
        account.starred_bookings.append(id)
    return respond(request, 'booking_star.html', {'booking': request.booking})


@login_required
def starred_bookings(request):
    account = models.Account.current_user_account
    bookings = account.get_starred_bookings().order_by('-day__date')
    return respond(request, 'starred_bookings.html', {
        'bookings': bookings})


@post_required
@login_required
def add_timer(request):
    timer = models.Timer()
    timer.start_time = datetime.datetime.now()
    timer.title = 'Timer'
    timer.status = models.TIMER_STATUS_STOPPED
    timer.save(user=request.user)
    return HttpResponse('OK', status=200)


@post_required
@login_required
@timer_required
@permission_required('inhouse.delete_timer')
def remove_timer(request):
    request.timer.delete()
    return HttpResponse('OK', status=200)


@post_required
@login_required
@timer_required
@permission_required('inhouse.add_timer')
def start_timer(request):
    request.timer.start()
    request.timer.save(user=request.user)
    return HttpResponse('OK', status=200)


@post_required
@login_required
@timer_required
@permission_required('inhouse.change_timer')
def pause_timer(request):
    request.timer.stop()
    request.timer.save(user=request.user)
    return HttpResponse('OK', status=200)


@post_required
@login_required
@timer_required
@permission_required('inhouse.change_timer')
def clear_timer(request):
    request.timer.clear()
    request.timer.save(user=request.user)
    return HttpResponse('OK', status=200)


@post_required
@login_required
def edit_timer(request):
    """Edit the timer's title."""
    timer = models.Timer.get_by_id(request.POST['timer_id'])
    timer.title = request.POST['title']
    timer.save(user=request.user)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])
    #return HttpResponse('OK', status=200)


@login_required
def time(request):
    today = datetime.date.today()
    query = models.Booking.objects.select_related().filter(
        created_by=request.user).order_by('-created')
    bookings_today = query.filter(created__gte=today)
    bookings_last_week = query.filter(
        created__lt=today,
        created__gte=today - datetime.timedelta(days=7))
    bookings_last_month = query.filter(
        created__lt=today - datetime.timedelta(days=7),
        created__gte=today - datetime.timedelta(days=30))
    return respond(request, 'timeline.html', {
        'bookings_today': bookings_today,
        'bookings_last_week': bookings_last_week,
        'bookings_last_month': bookings_last_month})


@login_required
@permission_required('inhouse.change_booking')
def undo_booking_change(request):
    """Revert the starred bookings to their last, versioned state."""
    account = models.Account.current_user_account
    booking_ids = request.session.get('undo_bookings', [])
    # FIXME: Das Erstellen in die BookingHistory Klasse legen
    day = None
    for id in booking_ids:
        hst = models.BookingHistory.get_by_booking_id(id)
        if hst.action == models.HISTORY_ACTION_DELETE:
            booking = models.Booking()
            # Use the old booking id, so we can keep the history
            booking.id = hst.booking_id
            booking.revert(hst)
            booking.created = datetime.datetime.now()
            booking.created_by = request.user
            booking.save(user=request.user)
            hst.save(user=request.user)
        else:
            booking = hst.booking
            booking.revert(hst)
            booking.save(user=request.user)
        # The undo feature only works per day. So we can use the first booking
        # to retrieve the day and redirect to it after the undo.
        if day == None:
            day = booking.day
    del request.session['undo_bookings']
    return HttpResponseRedirect('/time/%s' % day.slugify())


#@post_required
@login_required
@booking_required
def unstar_booking(request):
    account = models.Account.current_user_account
    if account.starred_bookings is None:
        account.starred_bookings = []
    id = request.booking.id
    if id in account.starred_bookings:
        account.starred_bookings[:] = [i for i in account.starred_bookings if i != id]
    return respond(request, 'booking_star.html', {'booking': request.booking})


def _user_popup(request):
    user = request.user_to_show
    popup_html = cache.get('user_popup:%d' % user.id)
    if popup_html is None:
        logging.debug('Missing cache entry for user_popup:%d', user.id)
        popup_html = render_to_response('user_popup.html', {'user': user})
        cache.set('user_popup:%d' % user.id, popup_html, 60)
    return popup_html


@user_key_required
def user_popup(request):
    """Pop up to show the user info."""
    try:
        return _user_popup(request)
    except Exception, err:
        logging.exception('Exception in user_popup processing: %s' % err)
        # Return HttpResponse because the JS part expects a 200 status code.
        return HttpResponse('<font color="red">Error: %s; please report!</font>' %
                            err.__class__.__name__)


@login_required
@get_required
def overview(request):
    form = forms.SearchForm(request.GET)
    form.set_customer_choices(request.user)
    form.set_project_choices(request.user, request.GET.get('customer', None))
    form.set_step_choices(request.user, request.GET.get('project', None))
    form.set_tracker_choices(request.user, request.GET.get('project', None))
    query = []
    if 'search' in request.GET:
        if form.is_valid():
            query = models.Booking.objects.all().select_related()
            query = query.filter(day__user=request.user)
            #data = form.cleaned_data
            #if 'customer' in data:
                #query = query.filter(project__customer=data['customer'])
            #if 'project' in data:
                #query = query.filter(project=data['project'])
            #if 'step' in data:
                #query = query.filter(step=data['step'])
            query = query.order_by('-day__date')
            #messages.add_message(request, messages.INFO,
                                 #_(u'%d booking(s) matches found.')
                                 #% query.count())
    duration_sum = 0
    # Compute the overall duration time
    # TODO: use aggregation?
    for booking in query:
        duration_sum += booking.duration
    return respond(request, 'overview.html', {
        'form': form, 'bookings': query, 'sum': duration_sum})

@login_required
@post_required
def request_projectuser(request):
    """Requests a project membership."""
    if request.method == 'POST':
        form = forms.ProjectRequestForm(request.POST)
        form.set_project_choices(request.user)
        if form.is_valid():
            project = get_object_or_404(models.Project,
                                        id=form.cleaned_data['project'])
            if project and project.id:
                messages.success(request, _(u'Your request for project "%s" has'
                u' been sent.') % project.name)
    return HttpResponseRedirect(reverse('inhouse.views.show_projects'))
