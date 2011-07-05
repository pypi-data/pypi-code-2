# Copyright 2011 Terena. All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:

#    1. Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.

#    2. Redistributions in binary form must reproduce the above copyright notice,
#       this list of conditions and the following disclaimer in the documentation
#        and/or other materials provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY TERENA ``AS IS'' AND ANY EXPRESS OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
# EVENT SHALL TERENA OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# The views and conclusions contained in the software and documentation are those
# of the authors and should not be interpreted as representing official policies,
# either expressed or implied, of Terena.

from datetime import datetime

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _

from vff.field import VersionedFileField
from customfields import SafeCharField
from domain.models import Domain


class Entity(models.Model):

    name = SafeCharField(_(u'Entity name'), max_length=100)
    metadata = VersionedFileField(verbose_name=_(u'Entity metadata'),
                                blank=True, null=True,)
    owner = models.ForeignKey(User, verbose_name=_('Owner'),
                              blank=True, null=True)
    domain = models.ForeignKey(Domain, verbose_name=_('Domain'))
    delegates = models.ManyToManyField(User, verbose_name=_('Delegates'),
                                       related_name='permission_delegated',
                                       through='PermissionDelegation')

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('entity_view', (str(self.id), ))

    class Meta:
        verbose_name = _(u'Entity')
        verbose_name_plural = _(u'Entities')


class PermissionDelegation(models.Model):

    entity = models.ForeignKey(Entity, verbose_name=_(u'Entity'))
    delegate = models.ForeignKey(User, verbose_name=_('Delegate'),
                                       related_name='permission_delegate')
    date = models.DateTimeField(_(u'Delegation date'), default=datetime.now)

    def __unicode__(self):
        return ugettext(
            u'%(user)s delegates permissions for %(entity)s entity') % {
            'user': self.entity.owner.username, 'entity': self.entity.name}

    class Meta:
        verbose_name = _(u'Permission delegation')
        verbose_name_plural = _(u'Permission delegations')
