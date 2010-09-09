# -*- coding: utf-8 -*-

import models

class AddAccountToRequestMiddleware(object):

    def process_request(self, request):
        account = None
        if not request.user.is_anonymous():
            account = models.Account.get_account_for_user(request.user)
            models.Account.current_user_account = account
        request.user.account = account