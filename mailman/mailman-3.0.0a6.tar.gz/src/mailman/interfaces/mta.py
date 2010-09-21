# Copyright (C) 2009-2010 by the Free Software Foundation, Inc.
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

"""Interface for mail transport agent integration."""

from __future__ import absolute_import, unicode_literals

__metaclass__ = type
__all__ = [
    'IMailTransportAgentAliases',
    'IMailTransportAgentDelivery',
    ]


from zope.interface import Interface

from mailman.core.errors import MailmanError



class SomeRecipientsFailed(MailmanError):
    """Delivery to some or all recipients failed"""
    def __init__(self, temporary_failures, permanent_failures):
        HandlerError.__init__(self)
        self.temporary_failures = temporary_failures
        self.permanent_failures = permanent_failures



class IMailTransportAgentAliases(Interface):
    """Interface to the MTA aliases generator."""

    def create(mlist):
        """Tell the MTA that the mailing list was created."""

    def delete(mlist):
        """Tell the MTA that the mailing list was deleted."""

    def regenerate(output=None):
        """Regenerate the full aliases file.

        :param output: The file name or file object to send the output to.  If
            not given or None, and MTA specific file is used.
        :type output: string, file object, None
        """



class IMailTransportAgentDelivery(Interface):
    """Interface to the MTA delivery strategies."""

    def deliver(mlist, msg, msgdata):
        """Deliver a message to a mailing list's recipients.

        Ordinarily the mailing list is consulted for delivery specifics,
        however the message metadata dictionary can contain additional
        directions to control delivery.  Specifics are left to the
        implementation, but there are a few common keys:

        * envelope_sender - the email address of the RFC 2821 envelope sender;
        * decorated - a flag indicating whether the message has been decorated
            with headers and footers yet;
        * recipients - the set of all recipients who should receive this
            message, as a set of email addresses;

        :param mlist: The mailing list being delivered to.
        :type mlist: `IMailingList`
        :param msg: The original message being delivered.
        :type msg: `Message`
        :param msgdata: Additional message metadata for this delivery.
        :type msgdata: dictionary
        :return: delivery failures as defined by `smtplib.SMTP.sendmail`
        :rtype: dictionary
        """
