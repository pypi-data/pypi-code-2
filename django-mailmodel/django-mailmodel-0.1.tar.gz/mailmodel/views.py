#-*- coding: utf-8 -*-
from annoying.decorators import render_to, ajax_request
from django.views.decorators.http import require_POST
from recaptcha.client import captcha
from forms import MailModelForm
from app_settings import MAILMODEL_CONFIG

def valid_captcha(request):
    challenge = request.POST['recaptcha_challenge_field']
    response = request.POST['recaptcha_response_field']
    remoteip = request.META['REMOTE_ADDR']
    captcha_response = captcha.submit(challenge, response, MAILMODEL_CONFIG["PRIVATE_CAPTCHA_KEY"], remoteip)
    if captcha_response.is_valid:
        return True
    return False

@require_POST
@ajax_request
def mailmodel(request):
    _valid_captcha = True
    if MAILMODEL_CONFIG.get("INCLUDE_CAPTCHA", False):
        _valid_captcha = valid_captcha(request)
    form = MailModelForm(request.POST)
    if form.is_valid() and _valid_captcha:
        form.save()
        return {"ok": True}
    return {"ok": False, "errors": form.errors}

