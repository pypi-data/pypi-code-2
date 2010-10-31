from django.conf import settings
from django.utils import importlib

SHOP_ID = settings.MERCHANT_API_SHOP_ID
SHOP_SECRET_KEY = settings.MERCHANT_API_SHOP_SECRET_KEY

forms_module = getattr(settings, 'MERCHANT_API_ORDER_FORMS', 'merchant_api.forms')

def order_form_cls():
    module = importlib.import_module(forms_module)
    return module.OrderForm
