#-*- coding: utf-8 -*-
from django import template
from recaptcha.client import captcha
from templatetag_sugar.register import tag
from templatetag_sugar.parser import Name, Variable, Constant, Optional, Model
from django.template import loader, Context
from mailmodel.forms import MailModelForm
from mailmodel.app_settings import MAILMODEL_CONFIG

register = template.Library()

@tag(register, [Variable(), Variable()])
def mailmodel(context, model, id):
    form = MailModelForm(initial={"content_type": model, "object_pk": id})
    
    if MAILMODEL_CONFIG.get("INCLUDE_CAPTCHA", False):
        context["recaptcha_html"] = captcha.displayhtml(MAILMODEL_CONFIG["PUBLIC_CAPTCHA_KEY"])
    context["form"] = form
    context["id"] = id
    return loader.get_template('mailmodel/form.html').render(context)