# Copyright (C) 2010 by the Free Software Foundation, Inc.
#
# This file is part of GNU Mailman.
#
# GNU Mailman is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# GNU Mailman is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# GNU Mailman.  If not, see <http://www.gnu.org/licenses/>.

"""REST for domains."""

from __future__ import absolute_import, unicode_literals

__metaclass__ = type
__all__ = [
    'ADomain',
    'AllDomains',
    ]


from restish import http, resource
from zope.component import getUtility

from mailman.interfaces.domain import (
    BadDomainSpecificationError, IDomainManager)
from mailman.rest.helpers import CollectionMixin, etag, path_to
from mailman.rest.validator import Validator



class _DomainBase(resource.Resource, CollectionMixin):
    """Shared base class for domain representations."""

    def _resource_as_dict(self, domain):
        """See `CollectionMixin`."""
        return dict(
            base_url=domain.base_url,
            contact_address=domain.contact_address,
            description=domain.description,
            email_host=domain.email_host,
            self_link=path_to('domains/{0}'.format(domain.email_host)),
            url_host=domain.url_host,
            )

    def _get_collection(self, request):
        """See `CollectionMixin`."""
        return list(getUtility(IDomainManager))


class ADomain(_DomainBase):
    """A domain."""

    def __init__(self, domain):
        self._domain = domain

    @resource.GET()
    def domain(self, request):
        """Return a single domain end-point."""
        domain = getUtility(IDomainManager).get(self._domain)
        if domain is None:
            return http.not_found()
        return http.ok([], self._resource_as_json(domain))


class AllDomains(_DomainBase):
    """The domains."""

    @resource.POST()
    def create(self, request):
        """Create a new domain."""
        domain_manager = getUtility(IDomainManager)
        try:
            validator = Validator(email_host=unicode,
                                  description=unicode,
                                  base_url=unicode,
                                  contact_address=unicode,
                                  _optional=('description', 'base_url',
                                             'contact_address'))
            domain = domain_manager.add(**validator(request))
        except BadDomainSpecificationError:
            return http.bad_request([], b'Domain exists')
        except ValueError as error:
            return http.bad_request([], str(error))
        location = path_to('domains/{0}'.format(domain.email_host))
        # Include no extra headers or body.
        return http.created(location, [], None)

    @resource.GET()
    def collection(self, request):
        """/domains"""
        resource = self._make_collection(request)
        return http.ok([], etag(resource))
