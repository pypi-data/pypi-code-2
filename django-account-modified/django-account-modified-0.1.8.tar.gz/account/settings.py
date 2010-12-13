from django.utils.translation import ugettext_lazy as _
from django.conf import settings

ACCOUNT_USER_MODEL = getattr(settings, 'ACCOUNT_USER_MODEL','django.contrib.auth.models.User')
ACCOUNT_LOGIN_FORM = getattr(settings, 'ACCOUNT_LOGIN_FORM', 'account.forms.LoginForm')

ACCOUNT_REGISTRATION_REDIRECT_URLNAME = getattr(settings, 'ACCOUNT_REGISTRATION_REDIRECT_URLNAME', 'registration_complete')
ACCOUNT_REGISTRATION_FORM = getattr(settings, 'ACCOUNT_REGISTRATION_FORM', 'account.forms.RegistrationForm')
ACCOUNT_REGISTRATION_ENABLED = getattr(settings, 'ACCOUNT_REGISTRATION_ENABLED', True)
ACCOUNT_ACTIVATION_REQUIRED = getattr(settings, 'ACCOUNT_ACTIVATION_REQUIRED', True)
ACCOUNT_AUTHENTICATION_WITH_EMAIL = getattr(settings, 'ACCOUNT_AUTHENTICATION_WITH_EMAIL', False)

ACCOUNT_PASSWORD_RESET_FORM = getattr(settings, 'ACCOUNT_PASSWORD_RESET_FORM', 'account.forms.PasswordResetForm')
ACCOUNT_PASSWORD_CHANGE_FORM = getattr(settings, 'ACCOUNT_PASSWORD_CHANGE_FORM', 'account.forms.PasswordChangeForm')
ACCOUNT_PASSWORD_CHANGE_REQUIRES_OLD = getattr(settings, 'ACCOUNT_PASSWORD_CHANGE_REQUIRES_OLD', True)

ACCOUNT_CAPTCHA_ENABLED = getattr(settings, 'ACCOUNT_CAPTCHA_ENABLED', False)
ACCOUNT_CAPTCHA_FIELD = getattr(settings, 'ACCOUNT_CAPTCHA_FIELD', 'captcha.fields.CaptchaField')
ACCOUNT_CAPTCHA_LABEL = getattr(settings, 'ACCOUNT_CAPTCHA_LABEL', _('Enter the text on the image'))
