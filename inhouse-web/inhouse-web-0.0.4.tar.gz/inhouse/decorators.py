# -*- coding: utf-8 -*-

import logging
import urllib

import models

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import (
    HttpResponse,
    HttpResponseNotFound,
    HttpResponseRedirect,
    HttpResponseForbidden)


def booking_required(func):
    """Decorator that processes the booking_id handler argument."""
    def booking_wrapper(request, booking_id, *args, **kwds):
        #booking = models.Booking.objects.filter(id=int(booking_id))
        booking = models.Booking.get_by_id(booking_id)
        if not booking:
            return HttpResponseNotFound('No field exists with that key (%s)' %
                                        booking_id)
        request.booking = booking
        return func(request, *args, **kwds)
    return booking_wrapper


def booking_owner_required(func):
    """Decorator that processes the booking_id argument and insists you own it."""
    @login_required
    @booking_required
    def booking_owner_wrapper(request, *args, **kwds):
        if request.booking.day.user != request.user:
            return HttpResponseForbidden('You do not own this booking')
        return func(request, *args, **kwds)
    return booking_owner_wrapper


def booking_key_required(func):
    """Decorator that processes the user handler argument."""

    def booking_key_wrapper(request, booking_key, *args, **kwds):
        booking_key = urllib.unquote(booking_key)
        #bookings = models.Booking.objects.filter(id=booking_key)
        booking = models.Booking.get_by_id(booking_key)
        #accounts = models.Account.get_accounts_for_nickname(user_key)
        if not booking:
            logging.info("Account not found for nickname %s" % user_key)
            return HttpResponseNotFound('No booking found with that key (%s)' %
                                        booking_key)
        request.booking_to_show = booking
        return func(request, *args, **kwds)
    return booking_key_wrapper


def get_required(func):
    """Decorator that returns an error unless request.method == 'POST'."""

    def get_wrapper(request, *args, **kwds):
        if request.method != 'GET':
            return HttpResponse('This requires a GET request.', status=405)
        return func(request, *args, **kwds)
    return get_wrapper


#def login_required(func):
    #"""Decorator that redirects to the login page if you're not logged in."""

    #def login_wrapper(request, *args, **kwds):
        #if request.user is None or request.user.is_anonymous():
            #return HttpResponseRedirect('/signin')
        #return func(request, *args, **kwds)
    #return login_wrapper


def post_required(func):
    """Decorator that returns an error unless request.method == 'POST'."""

    def post_wrapper(request, *args, **kwds):
        if request.method != 'POST':
            return HttpResponse('This requires a POST request.', status=405)
        return func(request, *args, **kwds)
    return post_wrapper


def timer_required(func):
    def timer_wrapper(request, timer_id, *args, **kwds):
        timer = models.Timer.get_by_id(timer_id)
        if not timer:
            return HttpResponseNotFound('No timer exists with that key (%s)' %
                                        timer_id)
        request.timer = timer
        return func(request, *args, **kwds)
    return timer_wrapper


def user_key_required(func):
    """Decorator that processes the user handler argument."""

    def user_key_wrapper(request, user_key, *args, **kwds):
        user_key = urllib.unquote(user_key)
        if "@" in user_key:
            request.user_to_show = models.Account.objects.filter(email=user_key)[0]
        else:
            users = models.Account.objects.filter(id=user_key)
            if not users:
                logging.info('Account not found for nickname %s' % user_key)
                return HttpResponseNotFound('No user found with that key (%s)' %
                                            user_key)
            request.user_to_show = users[0]
        return func(request, *args, **kwds)
    return user_key_wrapper
