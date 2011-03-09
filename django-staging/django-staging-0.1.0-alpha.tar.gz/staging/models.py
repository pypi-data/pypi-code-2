from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from staging.validators import validate_repository


class StagingServer(models.Model):

    name = models.CharField(
        _('Server name'),
        max_length=100,
    )

    hostname = models.CharField(
        _('Server hostname'),
        max_length=100,
        help_text=_('You have to make sure that a hg server is listening on http://{{ domain }}:8888'),
        validators=[validate_repository],
    )

    def check_repository(self):
        """ Check if there is a HG server listening in its repository """
        try:
            validate_repository(self.hostname)
        except ValidationError, exc:
            return False, ' '.join(exc.messages)
        return True, _('Server seems ok')
