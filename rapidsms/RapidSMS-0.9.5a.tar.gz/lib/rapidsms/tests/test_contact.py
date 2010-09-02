#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from nose.tools import assert_equals
from ..models import Backend, Connection, Contact


def test_contact_is_messageable():

    mock_backend, created = Backend.objects.get_or_create(name="mock")
    contact = Contact.objects.create(name="aaa")

    mock_connection = Connection.objects.create(
        contact=contact,
        backend=mock_backend,
        identity="111")

    args = []
    kwargs = []

    def _stub(self,*args, **kwargs):
        args = args
        kwargs = kwargs

    mock_connection.message = _stub

    contact.message("bbb", c=1)
    assert kwargs == {"c": 1 }
    assert args == ["bbb"]
