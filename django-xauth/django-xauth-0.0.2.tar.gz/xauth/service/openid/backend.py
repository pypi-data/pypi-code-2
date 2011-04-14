from xauth.models import XauthAssociation

def authenticate(xauth_response):
    identity = xauth_response['response'].identity_url

    try:
        assoc = XauthAssociation.objects.get(identity=identity)
    except XauthAssociation.DoesNotExist:
        return None
    else:
        return assoc.user
