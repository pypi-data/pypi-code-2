#coding: utf-8
from django.http import HttpResponse, Http404
from django.views.generic.simple import direct_to_template
from django.shortcuts import get_object_or_404

try:
    from django.views.decorators.csrf import csrf_exempt
except ImportError: # django < 1.2
    from django.contrib.csrf.middleware import csrf_exempt

from netcash.forms import DataHandlerForm
from netcash.models import NetcashOrder, NetcashGateway
from netcash import signals
from netcash.conf import NETCASH_IP_HEADER

@csrf_exempt
def data_handler(request, secret):
    """
    Data URL handler.

    This view is secured by 40-byte random secret string in the URL and
    the ip address limiting.

    On successful access 'netcash.signals.data' signal is sent.
    Orders should be processed in signal handler.
    """
    gateway = get_object_or_404(NetcashGateway, secret=secret)

    if gateway.netcash_ip:
        # deny query if it come from untrusted ip
        ip = request.META.get(NETCASH_IP_HEADER, None)
        if ip != gateway.netcash_ip:
            raise Http404

    reference = request.POST.get('Reference', None)
    order = get_object_or_404(NetcashOrder, pk=reference)
    form = DataHandlerForm(request.POST, instance = order)
    if form.is_valid():
        order = form.save(commit=False)
        order.gateway = gateway
        order.save()
        signals.data.send(sender = data_handler, order=order)
        return HttpResponse('OK')
    return HttpResponse('error')


@csrf_exempt
def result_handler(request, template_name, extra_context=None):
    """
    Accept or Reject URL handler.

    There is no signing in Netcash protocol and these URLs are
    visible to user so processing orders on Accept/Reject URL access is very
    insecure and must be avoided. That's why django-netcash just renders a
    template and doesn't provide a hook for order processing here.
    """
    reference = request.REQUEST.get('Reference', False)
    order = get_object_or_404(NetcashOrder, pk=reference)
    context = {'order': order}
    context.update(extra_context or {})
    return direct_to_template(request, template_name, context)

