

from registration.forms import RegistrationForm, RegistrationFormUniqueEmail, \
    RegistrationFormTermsOfService
from recaptcha_works.fields import RecaptchaField
from traxauth import settings

class TraxAuthRegistrationForm(RegistrationFormUniqueEmail, RegistrationFormTermsOfService):
    if settings.TRAXAUTH_PROTECT_REGISTRATION_FORM:
        recaptcha = RecaptchaField(label='Human test', required=True)



