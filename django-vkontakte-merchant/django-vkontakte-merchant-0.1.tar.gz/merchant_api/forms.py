#coding: utf-8
import vkontakte
from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from merchant_api.models import Order
from merchant_api import conf

class OrderForm(forms.ModelForm):
    sig = forms.CharField()

    def clean_sig(self):
        params = self.data.copy()
        params.pop('sig')
        correct_signature = vkontakte.signature(conf.SHOP_SECRET_KEY, params)
        if self.cleaned_data['sig'] != correct_signature:
            raise forms.ValidationError('Invalid signature.', 10)
        return correct_signature

    def clean_merchant_id(self):
        merchant_id = self.cleaned_data['merchant_id']
        if str(merchant_id) != str(conf.SHOP_ID):
            raise forms.ValidationError("Merchant id doesn't match: %s" % merchant_id, 11)
        return merchant_id

    def clean_new_state(self):
        new_state = self.cleaned_data['new_state']
        if new_state != 'chargeable':
            raise forms.ValidationError('Invalid state: %s' % new_state, 11)
        return new_state

    def clean_user_id(self):
        user_id = self.cleaned_data['user_id']

        # if vk_iframe auth is used then django_user should be required
        if 'vk_iframe' in settings.INSTALLED_APPS:
            try:
                self.cleaned_data['django_user'] = User.objects.get(username=str(user_id))
            except User.DoesNotExist:
                raise forms.ValidationError('User does not exist', 21)

        return user_id

    def vk_error_code(self):
        if 'sig' in self.errors:
            return 10
        if 'user_id' in self.errors:
            return 21
        if self.errors:
            return 11
        return 0

    def plain_errors(self):
        return '|'.join(["%s: %s" % (k, (v[0])) for k, v in self.errors.items()])

    def _item_dict(self, i):
        return dict(
            number = i,
            item_id = self.cleaned_data['item_id_%d' % i],
            price = self.cleaned_data['item_price_%d' % i],
            quantity = self.cleaned_data['item_quantity_%d' % i],
            currency = self.cleaned_data['item_currency_%d' % i],
            currency_str = self.cleaned_data['item_currency_str_%d' % i]
        )

    def __init__(self, data, *args, **kwargs):
        # we can't use formsets so create fields on fly
        super(OrderForm, self).__init__(data, *args, **kwargs)
        self.item_count = get_quantity(data, 'item_id')
        self.custom_field_count = get_quantity(data, 'custom')
        self.create_fields()

    def create_fields(self):
        for i in range(1, self.item_count+1):
            self.fields['item_id_%d' % i] = forms.CharField(max_length=100)
            self.fields['item_price_%d' % i] = forms.DecimalField()
            self.fields['item_quantity_%d' % i] = forms.IntegerField(min_value=0)
            self.fields['item_currency_%d' % i] = forms.CharField(max_length=3)
            self.fields['item_currency_str_%d' % i] = forms.CharField(max_length=3)

        for i in range(1, self.custom_field_count+1):
            self.fields['custom_%d' % i] = forms.CharField()

    def save_extra_fields(self, order):
        order.items.all().delete()
        for i in range(1, self.item_count+1):
            order.items.create(**self._item_dict(i))

        order.custom_fields.all().delete()
        for i in range(1, self.custom_field_count+1):
            order.custom_fields.create(number=i, value=self.cleaned_data['custom_%d' % i])

    def clean_item(self, item):
        """ hook for cleaning items data. `item` is a dict here. """
        pass

    def clean(self):
        total = 0
        for i in range(1, self.item_count+1):
            data = self._item_dict(i)
            total += float(data['price'])*float(data['quantity'])
            self.clean_item(data)

        if 'amount' in self.cleaned_data:
            if int(total*10) != int(float(self.cleaned_data['amount'])*10):
                raise forms.ValidationError('Amount is incorrect: %s != %s' % (total, self.cleaned_data['amount']))

        return self.cleaned_data

    def save(self, *args, **kwargs):
        order = super(OrderForm, self).save(*args, **kwargs)
        self.save_extra_fields(order)
        return order

    class Meta:
        model = Order


def order_form(data, *args, **kwargs):
    return conf.order_form_cls()(data, *args, **kwargs)


def get_quantity(data, prefix):
    """ считает, сколько записей вида prefix_N в словаре """
    n = 1
    while True:
        name = "%s_%s" % (prefix, n)
        if name not in data:
            return n-1
        n += 1


#NOTIFICATION_TYPES = (
#    ('check-items-availability', u'проверка наличия и стоимости товаров'),
#    ('item-reservation', u'резервирование товара'),
#    ('calculate-shipping-cost', u'запрос на вычисление стоимости доставки'),
#    ('order-state-change', u'изменение статуса заказа'),
#)
