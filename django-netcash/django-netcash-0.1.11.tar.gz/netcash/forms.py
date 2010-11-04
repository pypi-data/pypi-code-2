from django import forms

from netcash.conf import *
from netcash.models import NetcashOrder

class HiddenForm(forms.Form):
    """ A form with all fields hidden """
    def __init__(self, *args, **kwargs):
        super(HiddenForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget = forms.HiddenInput()


class NetcashForm(HiddenForm):
    """ NetCash helper form.
    It is not for validating data.
    It can be used to output html. """

    target = NETCASH_TARGET_URL

    # these params are handled automatically
    m_1 = forms.CharField(max_length = 50, initial = NETCASH_USERNAME)
    m_2 = forms.CharField(max_length = 50, initial = NETCASH_PASSWORD)
    m_3 = forms.CharField(max_length = 50, initial = NETCASH_PIN)
    p1 = forms.CharField(max_length = 50, initial = NETCASH_TERMINAL_NUMBER)
    p2 = forms.CharField(max_length = 25)

    # The description of the goods sent for payment
    p3 = forms.CharField(max_length = 50)

    # Transactional Amount that is to be settled to the Card
    p4 = forms.DecimalField(min_value=0, decimal_places=2, max_digits=8)

    # Cancel Button URL. This is the URL the client will be directed
    # to when at anytime the client clicks the cancel button.
    p10 = forms.URLField(max_length=255, verify_exists=False, required=False)

    # 'Y' will display the budget option in the Gateway popup
    # 'N' will not display the budget option in the Gateway popup
    Budget = forms.ChoiceField(choices=('Y', 'N'), initial='N')

    # Extra fields that can contain any data that you require
    # back from the gateway once the settlement has been done
    m_4 = forms.CharField(max_length=50, required=False)
    m_5 = forms.CharField(max_length=50, required=False)
    m_6 = forms.CharField(max_length=50, required=False)

    # Card holders email address should you want an email sent to the cardholder
    m_9 = forms.CharField(max_length=100, required=False)

    # Any text sent in this parameter is returned to the Accept and Reject
    # return URL's. This is usually used with basket products like
    # OSCommerce and VirtueMart
    m_10 = forms.CharField(max_length=100, required=False)

    def __init__(self, *args, **kwargs):
        super(NetcashForm, self).__init__(*args, **kwargs)

        # new order reference number is issued each time form is instantiated
        self.order = NetcashOrder.objects.create()
        self.fields['p2'].initial = self.order.pk


class DataHandlerForm(forms.ModelForm):

    # This fields are named differently on data page for some reason
    m_4 = forms.CharField(max_length=50, required=False)
    m_5 = forms.CharField(max_length=50, required=False)
    m_6 = forms.CharField(max_length=50, required=False)

    TransactionAccepted = forms.CharField()

    def plain_errors(self):
        ''' plain error list (without the html) '''
        return '|'.join(["%s: %s" % (k, (v[0])) for k, v in self.errors.items()])

    def clean_TransactionAccepted(self):
        accepted = self.cleaned_data['TransactionAccepted']
        if accepted == 'true':
            return True
        elif accepted == 'false':
            return False
        else:
            raise forms.ValidationError('Invalid value')

    def save(self, *args, **kwargs):
        self.cleaned_data['Extra1'] = self.cleaned_data['m_4']
        self.cleaned_data['Extra2'] = self.cleaned_data['m_5']
        self.cleaned_data['Extra3'] = self.cleaned_data['m_6']
        return super(DataHandlerForm, self).save(*args, **kwargs)

    class Meta:
        model = NetcashOrder
        exclude = ['created_at', 'updated_at']
