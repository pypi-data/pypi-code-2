import logging

from xauth.models import XauthAssociation

logger = logging.getLogger('xauth.service.openid.util')

def save_association(user, xauth_response):
    assoc = XauthAssociation()
    assoc.user = user
    assoc.identity = xauth_response['response'].identity_url
    assoc.service = xauth_response['service']
    assoc.save()
