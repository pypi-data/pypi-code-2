from gae import template
from gae import webapp
from apps.user.forms import UserLoginForm, UserRegistrationForm

register = template.create_template_register()

@register.simple_tag
def login_form():
    """Render the user login form"""
    form = UserLoginForm()
    return webapp.instance.render("user/login_form", {'form': form})

@register.simple_tag
def registration_form():
    """Render the user registration form"""
    form = UserRegistrationForm()
    return webapp.instance.render("user/registration_form", {'form': form})