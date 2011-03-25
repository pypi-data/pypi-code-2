# -*- coding: utf-8 -*-

from django.contrib import messages

import models


class AddAccountToRequestMiddleware(object):

    def process_request(self, request):
        account = None
        if not request.user.is_anonymous():
            account = models.Account.get_account_for_user(request.user)
            models.Account.current_user_account = account
        request.user.account = account


class AdminMiddleware(object):

    def process_request(self, request):
        if request.path.startswith('/admin/'):
            pass
        # rest of method

    def process_response(self, request, response):
        if request.path.startswith('/admin/'):
            #response["test"] = 1
            return response
        # rest of method
