import logging
from models import Consumer, Token
from django import forms


class AuthenticatedRequest(forms.Form):
    """
    This forms validate an authenticated request.

    Based on: http://tools.ietf.org/html/rfc5849#section-3.1

    """
    oauth_consumer_key = forms.CharField()

    oauth_token = forms.CharField(required=False)

    SIGNATURE_METHODS_CHOICES = (
        ('HMAC-SHA1', ""),
        ('RSA-SHA1', ""),
        ('PLAINTEXT', ""),
        )
    oauth_signature_method = forms.ChoiceField(
        choices=SIGNATURE_METHODS_CHOICES)

    oauth_timestamp = forms.IntegerField(min_value=0, required=False)

    oauth_nonce = forms.CharField(required=False)

    oauth_version = forms.CharField(required=False)

    oauth_signature = forms.CharField(required=True)

    def clean_oauth_consumer_key(self):
        try:
            Consumer.objects.get(key=self.cleaned_data['oauth_consumer_key'])
        except Consumer.DoesNotExist, e:
            logging.error(e)
            raise forms.ValidationError("Consumer Not Found.")

    def clean_oauth_token(self):
        try:
            Token.objects.get(key=self.cleaned_data['oauth_token'])
        except Token.DoesNotExist, e:
            logging.error(e)
            raise forms.ValidationError("Token Not Found.")


class TemporaryCredential(AuthenticatedRequest):
    """
    This forms validate a temporary credential request.

    Based on: http://tools.ietf.org/html/rfc5849#section-2.1
    """

    oauth_callback = forms.CharField()
