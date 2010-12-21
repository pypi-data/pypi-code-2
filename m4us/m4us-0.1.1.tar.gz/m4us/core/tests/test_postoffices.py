# -*- coding: utf-8 -*-

#---Header---------------------------------------------------------------------

# This file is part of Message For You Sir (m4us).
# Copyright © 2010 Krys Lawrence
#
# Message For You Sir is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# Message For You Sir is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License
# for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Message For You Sir.  If not, see <http://www.gnu.org/licenses/>.


"""Tests for m4us.core.postoffices."""


#---Imports--------------------------------------------------------------------

#---  Standard library imports
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
## pylint: disable=W0622, W0611
from future_builtins import ascii, filter, hex, map, oct, zip
## pylint: enable=W0622, W0611

#---  Third-party imports
import mock
import strait

#---  Project imports
from . import support
## pylint: disable=E0611
from .. import postoffices, exceptions, interfaces
## pylint: enable=E0611


#---Globals--------------------------------------------------------------------


#---Functions------------------------------------------------------------------


#---Classes--------------------------------------------------------------------

#---  Support classes

class IPostOfficeTestSupportTrait(object):

    #---  Support methods

    def make_mock_link(self, source=None, outbox='outbox', sink=None,
      inbox='inbox'):
        if source is None:
            source = mock.Mock()
        if sink is None:
            sink = mock.Mock()
        return (source, outbox, sink, inbox)

    def make_mock_links(self, count=5):
        return [self.make_mock_link() for _ in range(count)]

    def get_source_outbox(self, link):
        return (link[0], link[1])

    def get_sink_inbox(self, link):
        return (link[2], link[3])


class CheckIPostOfficeFactoryTrait(object):

    # Note: This trait also requires CoreM4USSupportTrait.

    #---  Test case settings

    factory_interfaces = (interfaces.IPostOfficeFactory,)

    #--- Factory tests

    def test_factory_should_accept_argument_link_ignores_duplicates(self):
        with self.assert_not_raises(TypeError):
            self.make_object(link_ignores_duplicates=True)

    def test_factory_should_accept_argument_unlink_ignores_missing(self):
        with self.assert_not_raises(TypeError):
            self.make_object(unlink_ignores_missing=True)


class CheckIPostOfficeTrait(object):

    # Note: This trait also requires CoreM4USSupportTrait and
    # IPostOfficeTestSupportTrait.

    #---  Test case settings

    object_interfaces = (interfaces.IPostOffice,)

    #---  Link tests

    def test_link_should_accept_a_single_link_argument(self):
        post_office = self.make_object()
        link = self.make_mock_link()
        with self.assert_not_raises(TypeError):
            post_office.link(link)

    def test_link_should_accept_multiple_links_in_one_call(self):
        post_office = self.make_object()
        links = self.make_mock_links()
        with self.assert_not_raises(TypeError):
            post_office.link(*links)

    def test_link_should_raise_linkexistserror_if_link_already_exists(self):
        post_office = self.make_object()
        link = self.make_mock_link()
        with self.assert_raises(exceptions.LinkExistsError):
            post_office.link(link, link)

    def test_link_should_not_raise_linkexistserror_if_link_is_idempotent(self):
        post_office = self.make_object(link_ignores_duplicates=True)
        link = self.make_mock_link()
        with self.assert_not_raises(exceptions.LinkExistsError):
            post_office.link(link, link)

    #---  Unlink tests

    def test_unlink_should_accept_a_single_link_argument(self):
        post_office = self.make_object()
        link = self.make_mock_link()
        post_office.link(link)
        with self.assert_not_raises(TypeError):
            post_office.unlink(link)

    def test_unlink_should_accept_multiple_links_in_one_call(self):
        post_office = self.make_object()
        links = self.make_mock_links()
        post_office.link(*links)
        with self.assert_not_raises(TypeError):
            post_office.unlink(*links)

    def test_unlink_should_raise_nolinkerror_if_source_outbox_not_linked(self):
        post_office = self.make_object()
        link = self.make_mock_link()
        with self.assert_raises(exceptions.NoLinkError):
            post_office.unlink(link)

    def test_unlink_should_raise_nolinkerror_if_sink_inbox_not_linked(self):
        post_office = self.make_object()
        link_1 = self.make_mock_link()
        source, outbox = self.get_source_outbox(link_1)
        # Link 2 has same source and outbox as link 1
        link_2 = self.make_mock_link(source=source, outbox=outbox)
        post_office.link(link_1)
        with self.assert_raises(exceptions.NoLinkError):
            post_office.unlink(link_2)

    def test_unlink_should_not_raise_nolinkerror_if_unlink_is_idempotent(self):
        post_office = self.make_object(unlink_ignores_missing=True)
        link = self.make_mock_link()
        with self.assert_not_raises(exceptions.NoLinkError):
            post_office.unlink(link)

    #---  Post tests

    def test_post_should_raise_nolinkerror_if_source_outbox_not_linked(self):
        message = 'Some message'
        post_office = self.make_object()
        link = self.make_mock_link()
        source, outbox = self.get_source_outbox(link)
        with self.assert_raises(exceptions.NoLinkError):
            post_office.post(source, outbox, message)

    #---  Retrieve tests

    def test_retrieve_should_return_an_iterable_of_accumulated_messages(self):
        message_1, message_2 = messages = ('Some message', 'Another message')
        post_office = self.make_object()
        link = self.make_mock_link()
        source, outbox = self.get_source_outbox(link)
        sink, inbox = self.get_sink_inbox(link)
        post_office.link(link)
        post_office.post(source, outbox, message_1)
        post_office.post(source, outbox, message_2)
        for inbox_and_message, expected_message in zip(post_office.retrieve(
          sink), messages):
            self.assert_equal(inbox_and_message, (inbox, expected_message))

    def test_retrieve_should_return_an_empty_iterable_if_no_messages(self):
        post_office = self.make_object()
        link = self.make_mock_link()
        sink, _ = self.get_sink_inbox(link)
        post_office.link(link)
        # Retrieve returns an interable, not necessarily a sequence.  (i.e. it
        # may not directly support len().)
        self.assert_equal(len(list(post_office.retrieve(sink))), 0)

    def test_retrieve_should_raise_notasinkerror_if_coroutine_not_a_sink(self):
        post_office = self.make_object()
        with self.assert_raises(exceptions.NotASinkError):
            post_office.retrieve(mock.Mock())

    def test_retrieve_should_return_remaining_messages_after_unlink(self):
        post_office = self.make_object()
        link = self.make_mock_link()
        message = 'Some message'
        source, outbox = self.get_source_outbox(link)
        sink, inbox = self.get_sink_inbox(link)
        post_office.link(link)
        post_office.post(source, outbox, message)
        post_office.unlink(link)
        with self.assert_not_raises(exceptions.NotASinkError):
            # First call after unlink returns any left over messages.
            messages = post_office.retrieve(sink)
        self.assert_items_equal(messages, [(inbox, message)])

    def test_retrieve_should_raise_notasinkerror_if_coroutine_unlinked(self):
        post_office = self.make_object()
        link = self.make_mock_link()
        sink, _ = self.get_sink_inbox(link)
        post_office.link(link)
        post_office.unlink(link)
        # First call after unlink returns any left over messages.
        post_office.retrieve(sink)
        with self.assert_raises(exceptions.NotASinkError):
            # Second call should raise the exception.
            post_office.retrieve(sink)

    def test_retrieve_should_empty_message_queue(self):
        post_office = self.make_object()
        link = self.make_mock_link()
        message = 'Some message'
        source, outbox = self.get_source_outbox(link)
        sink, _ = self.get_sink_inbox(link)
        post_office.link(link)
        post_office.post(source, outbox, message)
        post_office.retrieve(sink)
        empty_messages = post_office.retrieve(sink)
        self.assert_items_equal(empty_messages, [])


#---Module initialization------------------------------------------------------


#---Late Imports---------------------------------------------------------------


#---Late Globals---------------------------------------------------------------

STANDARD_IPOSTOFFICE_TRAITS = (
  IPostOfficeTestSupportTrait,
  CheckIPostOfficeFactoryTrait,
  CheckIPostOfficeTrait,
)


#---Late Functions-------------------------------------------------------------


#---Late Classes---------------------------------------------------------------

#---  Test classes

class TestPostOffice(support.TestCase):

    __metaclass__ = strait.include(
      *(STANDARD_IPOSTOFFICE_TRAITS +
      support.STANDARD_CLASS_TRAITS))

    #---  Test case settings

    factory = postoffices.PostOffice

    #---  Support methods

    def assert_link_in_postoffice(self, link, post_office):
        source_outbox = self.get_source_outbox(link)
        sink_inbox = self.get_sink_inbox(link)
        self.assert_in(source_outbox, post_office._links)
        self.assert_in(sink_inbox, post_office._links[source_outbox])

    #---  Link tests

    def test_link_should_link_coroutine_mailboxes(self):
        post_office = self.make_object()
        link = self.make_mock_link()
        post_office.link(link)
        self.assert_link_in_postoffice(link, post_office)

    def test_link_should_link_multiple_coroutine_mailboxes(self):
        post_office = self.make_object()
        links = self.make_mock_links()
        post_office.link(*links)
        for link in links:
            self.assert_link_in_postoffice(link, post_office)

    def test_link_should_not_adapt_source_or_sink_to_an_interface(self):
        post_office = self.make_object()
        link = ('producer', 'outbox', 'consumer', 'inbox')
        post_office.link(link)
        self.assert_link_in_postoffice(link, post_office)

    #---  Unlink tests

    def test_unlink_should_unlink_mailboxes(self):
        post_office = self.make_object()
        link_1 = self.make_mock_link()
        source, outbox = source_outbox = self.get_source_outbox(link_1)
        sink_inbox_1 = self.get_sink_inbox(link_1)
        # Link 2 has same source and outbox as link 1
        link_2 = self.make_mock_link(source=source, outbox=outbox)
        sink_inbox_2 = self.get_sink_inbox(link_2)
        post_office.link(link_1, link_2)
        post_office.unlink(link_1)
        self.assert_in(source_outbox, post_office._links)
        self.assert_not_in(sink_inbox_1, post_office._links[source_outbox])
        self.assert_in(sink_inbox_2, post_office._links[source_outbox])

    def test_unlink_should_unlink_multiple_coroutine_mailboxes(self):
        post_office = self.make_object()
        links = self.make_mock_links()
        post_office.link(*links)
        post_office.unlink(*links)
        self.assert_items_equal(post_office._links, [])

    def test_unlink_should_forget_source_outboxes_with_no_links(self):
        post_office = self.make_object()
        link = self.make_mock_link()
        post_office.link(link)
        self.assert_link_in_postoffice(link, post_office)
        post_office.unlink(link)
        source_outbox = self.get_source_outbox(link)
        self.assert_not_in(source_outbox, post_office._links)

    #---  Post tests

    def test_post_should_store_messages(self):
        message = 'Some message'
        post_office = self.make_object()
        link = self.make_mock_link()
        source, outbox = self.get_source_outbox(link)
        sink, inbox = self.get_sink_inbox(link)
        post_office.link(link)
        post_office.post(source, outbox, message)
        self.assert_in((inbox, message), post_office._message_queues[sink])


#---Late Module initialization-------------------------------------------------
