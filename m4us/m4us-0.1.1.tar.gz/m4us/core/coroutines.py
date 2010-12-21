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


"""Provides support for using regular Python_ `coroutines`.

.. _Python: http://python.org

"""


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
import weakref

#---  Third-party imports
## pylint: disable=E0611
from zope import interface, component
## pylint: enable=E0611
import decorator

#---  Project imports
from . import utils, interfaces
# This is imported directly for the sample coroutine
from .utils import is_shutdown


#---Globals--------------------------------------------------------------------


#---Functions------------------------------------------------------------------

def _init_coroutines():
    """Initialize `coroutine` `interface` support."""
    # All Python coroutines provide ICoroutine.
    interface.classImplements(types.GeneratorType, interfaces.ICoroutine)
    # non-lazy Python coroutines need to be adapted to INotLazy.
    component.provideAdapter(_icoroutine_to_inotlazy_adapter)


@component.adapter(interfaces.ICoroutine)
@interface.implementer(interfaces.INotLazy)
def _icoroutine_to_inotlazy_adapter(coroutine_):
    """`Adapter` `factory` to adapt Python_ `coroutines` to :class:`INotLazy`.

    `Components` and other classes that implement
    :class:`~m4us.core.interfaces.ICoroutine` can just (and are expected to)
    implement :class:`~m4us.core.interfaces.INotLazy` directly.  They do not
    need this adapter.

    Python_ `coroutines`, on the other hand are really instances of
    :class:`~types.GeneratorType`.  They cannot be made to directly provide
    :class:`~m4us.core.interfaces.INotLazy` because one cannot add additional
    attributes to the `generator` object.  That is where this `adapter` comes
    in.

    This `adapter` just checks to see if the `coroutine` has been registered as
    non-`lazy` by the :func:`_register_non_lazy_coroutine` function.  If it
    has, the `coroutine` is returned unchanged.  Otherwise, :obj:`None` is
    returned, which signals that adaptation was not possible.

    Since the :func:`coroutine` decorator automatically registers non-`lazy`
    `coroutines`, adaptation to :class:`~m4us.core.interfaces.INotLazy` happens
    transparently.

    :param coroutine_: The `coroutine` to adapt.
    :type coroutine_: :class:`~m4us.core.interfaces.ICoroutine`

    :returns: The given `coroutine` if it is non-`lazy`, :obj:`None` otherwise.
    :rtype: :class:`~m4us.core.interfaces.ICoroutine` or :obj:`None`

    """
    if _NonLazyCoroutineRegistry().is_non_lazy(coroutine_):
        return coroutine_


def coroutine(lazy=True):
    """Decorator factory to automatically activate Python_ `coroutines`.

    Before a Python_ `coroutine` can be used, it needs to be activated by
    sending :obj:`None` as it's first `message`.  This decorator does this
    automatically.

    `Coroutines` are presumptively `lazy`.  This decorator can flag the
    given `coroutine` as not `lazy` by making it adaptable to the
    :class:`~m4us.core.interfaces.INotLazy` marker `interface`.

    This decorator also registers the function as providing
    :class:`~m4us.core.interfaces.ICoroutineFactory`.

    :param lazy: Specifies whether or not the `coroutine` is `lazy`.
    :type lazy: :class:`bool`

    :returns: A wrapper function that will activate and return the `coroutine`
      when called.
    :rtype: :class:`~types.FunctionType`

    """
    def _coroutine_factory(function, *args, **kwargs):
        """Return an activated coroutine, with/without `lazy` registration."""
        coroutine_ = function(*args, **kwargs)
        coroutine_.send(None)
        if not lazy:
            _NonLazyCoroutineRegistry().register(coroutine_)
        return coroutine_

    def _coroutine_decorator(function):
        """Decorator for creating `coroutine` factories."""
        coroutine_factory = decorator.decorator(_coroutine_factory, function)
        interface.directlyProvides(coroutine_factory,
          interfaces.ICoroutineFactory)
        return coroutine_factory
    return _coroutine_decorator


#---Classes--------------------------------------------------------------------

class _NonLazyCoroutineRegistry(object):

    """.. todo:: document me and create tests."""

    # Borg pattern to avoid using a global and to make pylint happy.  Arguably,
    # it is also a better compartmentalized solution.

    _non_lazy_coroutines = weakref.WeakValueDictionary()

    def register(self, coroutine_):
        """Register a Python_ `coroutine` as being not `lazy`.

        Registering a `coroutine` as non-`lazy` allows it to be adapted to
        :class:`~m4us.core.interfaces.INotLazy`.

        :param coroutine_:  The `coroutine` to register.
        :type coroutine_: :class:`~m4us.core.interfaces.ICoroutine`

        .. note:: Registration works through `weak references`_ so it should
            not cause any memory leaks.

        .. seealso:: The :class:`~m4us.core.interfaces.INotLazy` marker
            `interface` for more information about `lazy` and non-`lazy`
            `coroutines`.

        .. _`weak references`: http://docs.python.org/library/weakref.html

        """
        self._non_lazy_coroutines[id(coroutine_)] = coroutine_

    def is_non_lazy(self, coroutine_):
        """Return :obj:`True` if the `coroutine` is registered as non-`lazy`.

        :param coroutine_:  The `coroutine` to check.
        :type coroutine_: :class:`~m4us.core.interfaces.ICoroutine`

        :returns: :obj:`True` if the `coroutine` is not `lazy`, :obj:`False`
          otherwise.
        :rtype: :class:`bool`

        .. seealso:: The :meth:`_register` method for details about registering
            Python_ `coroutines` as being non-`lazy`.

        .. seealso:: The :class:`~m4us.core.interfaces.INotLazy` marker
            `interface` for more information about `lazy` and non-`lazy`
            `coroutines`.

        """
        return id(coroutine_) in self._non_lazy_coroutines


#---Module initialization------------------------------------------------------

_init_coroutines()


#---Late Imports---------------------------------------------------------------


#---Late Globals---------------------------------------------------------------


#---Late Functions-------------------------------------------------------------

# [[start sample_coroutine]]
@coroutine()
def sample_coroutine():
    """Pass all messages through."""
    inbox, message = (yield)
    while True:
        if is_shutdown(inbox, message):
            yield 'signal', message
            break
        ## Your code goes here.
        inbox, message = (yield 'outbox', message)
# [[end sample_coroutine]]

# The docstring for sample_coroutine is set like this so that it can include
# it's own source code in the docs.  The literalinclude directive won't work
# completely correctly if the docstring is inline.
## pylint: disable=W0622
sample_coroutine.__doc__ = """Pass all `messages` through.

    This `coroutine` is meant to provide a canonical example of what a
    `coroutine` used with this project looks like.

    Any `messages` sent to it on any `inbox` will be sent back out on it's
    ``outbox`` `outbox`.  It is also well behaved in that it will shutdown on
    any :class:`~m4us.core.interfaces.IShutdown` `message`, forwarding it on
    before quitting.

    The full code for this `coroutine` is:

    .. literalinclude:: ../../../../m4us/core/coroutines.py
        :linenos:
        :start-after: # [[start sample_coroutine]]
        :end-before: # [[end sample_coroutine]]

    :returns: A pass-through `coroutine`
    :rtype: :class:`~types.GeneratorType`

    :Implements: :class:`~m4us.core.interfaces.ICoroutine`
    :Provides: :class:`~m4us.core.interfaces.ICoroutineFactory`

    .. note:: `Producers` and `filters` need a minimum of 2 :keyword:`yield`
        statements as the output of the first one is always thrown away.  The
        output of the second one is the first `message` delivered.  On the
        other hand, the first :keyword:`yield` will be the one that gets the
        first incoming `message`.

    """
## pylint: enable=W0622


@coroutine()
def null_sink():
    """Swallow all messages except :class:`~m4us.core.interfaces.IShutdown`.

    This `coroutine` can serve as an end point in a series of connected
    `coroutines`.  All `messages` sent to it, except
    :class:`~m4us.core.interfaces.IShutdown` `messages` are ignored and not
    re-emitted.

    The `coroutine` will shutdown on any
    :class:`~m4us.core.interfaces.IShutdown` `message`, forwarding it on before
    quitting.

    :returns: A null sink `coroutine`
    :rtype: :class:`~types.GeneratorType`

    :Implements: :class:`~m4us.core.interfaces.ICoroutine`
    :Provides: :class:`~m4us.core.interfaces.ICoroutineFactory`

    """
    while True:
        inbox, message = (yield)
        if utils.is_shutdown(inbox, message):
            yield 'signal', message
            break


#---Late Classes---------------------------------------------------------------


#---Late Module initialization-------------------------------------------------
