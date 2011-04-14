import logging

from django.contrib.auth.models import User

logger = logging.getLogger('xauth.backends')

class XauthBackend(object):
    supports_object_permissions = False
    supports_anonymous_user = True
    supports_inactive_user = True

    def authenticate(self, xauth_response):
        service = xauth_response['service']
        logger.debug('Authenticating user with %s xauth service' % service)
        try:
            module = __import__('xauth.service.%s.backend' % service, globals(), locals(), ['foo'])
            auth_func = getattr(module, 'authenticate')
        except (ImportError, AttributeError), ex:
            logger.error('Could not import service authentication backend', exc_info=ex)
        else:
            return auth_func(xauth_response)

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
