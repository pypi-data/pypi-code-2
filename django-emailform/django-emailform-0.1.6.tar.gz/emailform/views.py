from __future__ import absolute_import

import logging
import smtplib

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.urlresolvers import reverse, NoReverseMatch
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext as _rc
from django.template.loader import render_to_string

from .forms import forms_for_emailform, BaseOptionAnswer
from .models import EmailForm, Entry, OPTION_TYPE_CHOICES

from .util import ChoiceEnum
from . import settings as emailform_settings


def _get_remote_ip(request):
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded:
        return forwarded.split(',')[-1].strip()
    return request.META['REMOTE_ADDR']


def _get_emailform_or_404(request, slug):
    mgr = EmailForm.objects if request.user.is_staff else EmailForm.live
    return get_object_or_404(mgr, slug=slug, site=settings.SITE_ID)


def _emailform_submit(request, emailform, embed=False):
    forms = forms_for_emailform(emailform, request)
    if all(form.is_valid() for form in forms):
        all_fields = []
        for field in forms:
            for k, v in field.clean().iteritems():
                if isinstance(field, BaseOptionAnswer):
                    v = ','.join(v)
                all_fields.append('%s : %s' % (field.question.label, v))
        entry = Entry(emailform=emailform,
                      ip_address=_get_remote_ip(request),
                      content=render_to_string(
                        ('emailform/%s_emailform_completed.html'
                         % (emailform.slug),
                        'emailform/emailform_completed.html'),
                        dict(all_fields=all_fields)))
        entry.save()
        if emailform.email:
            _send_emailform_email(request, emailform, entry)
        return _emailform_show_form(request,
                                       emailform,
                                       (),
                                       entered=True,
                                       embed=embed)
    else:
        return _emailform_show_form(request,
                                       emailform,
                                       forms,
                                       embed=embed)


def _url_for_edit(request, obj):
    view_args = (obj._meta.app_label, obj._meta.module_name,)
    try:
        edit_url = reverse("admin:%s_%s_change" % view_args, args=(obj.id,))
    except NoReverseMatch:
        edit_url = "/admin/%s/%s/%d/" % (view_args + (obj.id,))
    admin_url = emailform_settings.EMAILFORM_ADMIN_SITE
    if not admin_url:
        admin_url = "http://" + request.META["HTTP_HOST"]
    elif len(admin_url) < 4 or admin_url[:4].lower() != "http":
        admin_url = "http://" + admin_url
    return admin_url + edit_url


def _send_emailform_email(request, emailform, entry):
    subject = emailform.title
    sender = emailform_settings.EMAILFORM_EMAIL_FROM
    recipients = list(set(x.strip() for x in emailform.email.split(',')))
    links = [(_url_for_edit(request, entry), "Edit Submission"),
             (_url_for_edit(request, emailform), "Edit Email Form"), ]
    html_email = entry.content
    email_msg = EmailMultiAlternatives(subject,
                                       html_email,
                                       sender,
                                       recipients)
    email_msg.attach_alternative(html_email, 'text/html')
    try:
        email_msg.send()
    except smtplib.SMTPException as ex:
        logging.exception("SMTP error sending email: %s" % str(ex))
    except Exception as ex:
        logging.exception("Unexpected error sending email: %s" % str(ex))


def _emailform_show_form(request,
                            emailform,
                            forms,
                            entered=False,
                            embed=False):
    if embed:
        specific_template = ('emailform/%s_emailform_detail_embed.html' %
                        emailform.slug)
        return render_to_response([specific_template,
                               'emailform/emailform_detail_embed.html'],
                              dict(emailform=emailform,
                                   forms=forms,
                                   entered=entered,
                                   embed=embed),
                              _rc(request))
    specific_template = ('emailform/%s_emailform_detail.html' %
                    emailform.slug)
    return render_to_response([specific_template,
                           'emailform/emailform_detail.html'],
                          dict(emailform=emailform,
                               entered=entered,
                               forms=forms,
                               embed=embed),
                          _rc(request))


def emailform_detail(request, slug, embed=False):
    emailform = _get_emailform_or_404(request, slug)
    if request.method == 'POST':
        return _emailform_submit(request, emailform, embed=embed)
    forms = forms_for_emailform(emailform, request)
    return _emailform_show_form(request, emailform, forms, embed=embed)
