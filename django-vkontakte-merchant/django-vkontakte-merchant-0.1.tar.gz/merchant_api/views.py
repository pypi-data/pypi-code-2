#coding: utf-8
import logging
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.transaction import commit_on_success
from merchant_api.forms import order_form
from merchant_api.api import error, status_change_success

@csrf_exempt
@commit_on_success
def merchant_callback(request):
    form = order_form(request.POST)
    if form.is_valid():
        order = form.save()
        return HttpResponse(status_change_success(order.order_id, order.pk))
    return HttpResponse(error(form.vk_error_code(), form.plain_errors(), request.POST))
