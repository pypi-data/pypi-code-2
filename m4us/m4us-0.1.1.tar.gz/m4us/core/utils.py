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


"""Provides common utilities for the rest of the project."""


#---Imports--------------------------------------------------------------------

#---  Standard library imports
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
## pylint: disable=W0622, W0611
from future_builtins import ascii, filter, hex, map, oct, zip
## pylint: enable=W0622, W0611

import types

#---  Third-party imports

#---  Project imports
from . import interfaces


#---Globals--------------------------------------------------------------------

## pylint: disable=W0105
_DEFAULT_NAME_EXCLUDES = ('filter', 'map', 'zip')
"""The default object names to always exclude from :func:`_is_private_object`.

This global is here so that other modules can use it as a base when needing to
include additional names.

It currently only includes the names of objects in the *future_builtins* module
that do not originate in that module (and so their *__module__* module
attribute is not set to ``future_builtins``.  E.g. ``'filter'``, ``'map'``,
etc.

"""
## pylint: enable=W0105


#---Functions------------------------------------------------------------------

def _is_private_object(object_name, object_, excludes=_DEFAULT_NAME_EXCLUDES):
    """Return :obj:`True` if the object is private.

    Private object means any object that would not be considered part of a
    public API.  Specifically, an object is considered private if:

      * Its name is in the excludes list, or
      * Its name starts with an underscore ("_"), or
      * It is a module, or
      * It is from the *__future__* or *future_builtins* modules.

    :param object_name: The name of the object to check.
    :type object_name: :class:`str` or :class:`unicode`
    :param object_: The object to check.
    :type object_: :class:`object`
    :param excludes: A sequence of object names to always consider as private.
      The default just includes the names from *future_builtins* that original
      elsewhere.
    :type excludes: *sequence* of :class:`str` or :class:`unicode`

    :returns: :obj:`True` if the object is considered non-public, :obj:`False`
      otherwise.
    :rtype: :class:`bool`

    """
    return (
      object_name in excludes or
      object_name.startswith('_') or
      isinstance(object_, types.ModuleType) or
      (hasattr(object_, '__module__') and object_.__module__ in ('__future__',
        'future_builtins')))


def _public_object_names(namespace, excludes=_DEFAULT_NAME_EXCLUDES):
    """`Generator` of public names in a namespace.

    Given a namespace (like the *__dict__* of a module, for example), this
    `generator` will yield the names of all public objects in the namespace.

    Public object is defined as whenever :func:`_is_private_object` returns
    :obj:`False`.

    Example usage:

    >>> import somemodule
    >>> for name in _public_object_names(vars(somemodule)):
    >>>     print(name)

    :param namespace: The namesapce in which to search for objects.
    :type namespace: :class:`dict`
    :param excludes: A sequence of object names to always exclude.
    :type excludes: *sequence* of :class:`str` or :class:`unicode`

    :returns: An iterator of public object names from the given namespace.
    :rtype: :class:`~types.GeneratorType`

    """
    excludes = set(excludes)
    for name, object_ in namespace.items():
        if _is_private_object(name, object_, excludes):
            continue
        yield name


def easy_link(first_coroutine, second_coroutine, *other_coroutines):
    """Return `links` connecting the `coroutines` in the standard way.

    The given `coroutines` are linked in a `pipeline` (not to be confused with
    a :class:`~m4us.core.containers.Pipeline`) of ``outbox`` to ``inbox`` and
    ``signal`` to ``control`` `mailboxes`.  The first `coroutine` will only
    have it's ``outbox`` and ``signal`` `mailboxes` linked and the last
    `coroutine` will only have it's ``inbox`` and ``control`` `mailboxes`
    linked.  `Coroutines` in the middle will be linked to the previous and next
    `coroutines` in order.

    The resulting `links` can then be passed to a `post office`.

    :param first_coroutine: A minimum of two `coroutines` are required. This is
      the first one.
    :type first_coroutine: :class:`~m4us.core.interfaces.ICoroutine`
    :param second_coroutine: The second `coroutine`.
    :type second_coroutine: :class:`~m4us.core.interfaces.ICoroutine`
    :param other_coroutines: Any other `coroutines` to `link` after the second
      one.
    :type other_coroutines: :class:`tuple` of
      :class:`~m4us.core.interfaces.ICoroutine`

    :returns: A set of `mailbox` `links` to be given to a `post office`.
    :rtype: :class:`set` of 4-:class:`tuple`\s

    .. note:: Normally one would just use the
        :class:`~m4us.core.containers.Pipeline` class, but this provides just
        the `links`, which could be useful to other `container` classes.

    .. seealso:: The :class:`~m4us.core.interfaces.IPostOffice` `interface` for
        more information on `links`, `mailboxes` and `post offices`.

    .. seealso:: The :class:`~m4us.core.containers.Pipeline` class for the
        normal way to construct `coroutine` `pipelines`.

    """
    sources = (first_coroutine, second_coroutine) + other_coroutines[:-1]
    sinks = (second_coroutine,) + other_coroutines
    links = set()
    for source, sink in zip(sources, sinks):
        links.update((
          (source, 'outbox', sink, 'inbox'),
          (source, 'signal', sink, 'control'),
        ))
    return links


def is_shutdown(inbox, message, expected_inbox='control'):
    """Return :obj:`True` if the given `message` signals a shutdown.

    `Coroutines` are expected to shutdown when they receive a shutdown
    `message`.  This is a convenience function that returns :obj:`True` if
    `inbox` is ``control`` (by default) and the `message` object provides or is
    adaptable to :class:`~m4us.interfaces.IShutdown`.

    :param inbox: The `inbox` in which with `message` was received.
    :type inbox: :class:`unicode`
    :param message: The `message` object that was received.
    :type message: any
    :param expected_inbox: The `inbox` in which
      :class:`~m4us.interfaces.IShutdown` `messages` are expected.  This
      parameter lets the default be overridden.
    :type expected_inbox: :class:`unicode`

    :returns: :obj:`True` if the `message` signals that the `coroutine` should
      shutdown, :obj:`False` otherwise.
    :rtype: :class:`bool`

    """
    return inbox == expected_inbox and interfaces.IShutdown(message, False)


#---Classes--------------------------------------------------------------------


#---Module initialization------------------------------------------------------


#---Late Imports---------------------------------------------------------------


#---Late Globals---------------------------------------------------------------


#---Late Functions-------------------------------------------------------------


#---Late Classes---------------------------------------------------------------


#---Late Module initialization-------------------------------------------------
