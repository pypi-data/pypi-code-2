# -*- coding: utf-8 -*-

# gh
from glashammer.utils import render_template
# this bundle
from forms import LoginForm


def render_login_form(env):
    request = env['werkzeug.request']
    form = LoginForm(request.form)
    #if request.method == 'POST' and form.validate():
    #    hm.. FormPlugin should have done the job already :)
    result = render_template('login.html', form=form)
    return str(result.encode('utf-8'))
