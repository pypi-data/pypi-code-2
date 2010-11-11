from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

if 'demo.middleware.DemoMiddleware' in settings.MIDDLEWARE_CLASSES:
    raise ImproperlyConfigured(
        "For security reasons you cannot use the `demo_controller` app with "
        "the `DemoMiddleware` middleware."
    )