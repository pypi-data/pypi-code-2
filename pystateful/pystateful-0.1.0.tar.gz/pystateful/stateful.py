#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf8
# (C) 2010 Alan Franzoni. 
import sys
import re
import inspect

STATEFUL_MARKER = "_stateful__"
FUNC_NAME_SEPARATOR = "_fname"
MAX_STATENAME_LENGTH = 64

class _NoFallbackState(object):
    def __nonzero__(self):
        return False

    def __eq__(self, other):
        return True

_NOFALLBACK = _NoFallbackState()

class StateBroker(object):
    """
    StateBroker object; kind of stateful class builder.
    """
    _statename_pattern = re.compile("^[a-zA-Z][a-zA-Z0-9]{0,%s}$" %
            (MAX_STATENAME_LENGTH - 1))

    def __init__(self, *statenames, **kwargs):
        """
        Each state name must
        begin with an ascii letter and can then continue with ascii letters and
        digits, max 64 chars. No other chars are allowed.

        Even though using this lib makes no sense with just one state, I see no
        point in not letting it work however.
        @param fallback: a state name for fallback func calling.
        """
        if len(statenames) < 1:
            raise ValueError, "At least one states must be passed."

        self.names = []

        for name in statenames:
            if not self._statename_pattern.match(name):
                raise ValueError, "Invalid state name '%s'" % name

            if name in self.names:
                raise ValueError, "Duplicate state name '%s'" % name

            self.names.append(name)

        self.names = statenames

        fallback = kwargs.get("fallback", _NOFALLBACK)
        if (fallback != _NOFALLBACK) and (fallback not in statenames):
                raise ValueError("Fallback state must exists, '%s' doesn't." %
                        fallback)

        self._fallback = fallback

    def stateful(s, klass):
        def new_init(self, *args, **kwargs):
            klass.__init__(self, *args, **kwargs)
            self._state = StateSwitcher(s.names)
            self._caller = StatefulCaller(self, self._state, s._fallback)

        return type(klass.__name__ + "Stateful", (klass, ), {"__init__":new_init})

    def _get_state_aware_dispatcher(s, funcname):
        def method_dispatcher(self, *args, **kwargs):
            return self._caller.call(funcname, *args, **kwargs)
        method_dispatcher.func_name = funcname
        method_dispatcher.is_method_dispatcher = True # this is used to prevent wrong transition decorators.
        return method_dispatcher

    # we can make this a kind of instance func of an object in order to let it
    # work globally this would let us specify a state name.
    def on_state(self, statename, default=False):
        """
        VERY IMPORTANT: since this functions performs some tricky code manipulation, if decorators are chained this one
        should be invoked as the outermost decorator, e.g. the first if using the @syntax or the last if using
        the old syntax.

        Otherwise things won't probably work as expected.
        @param statename: name of the state
        @param default: if True, this state will be the fallback method for JUST THIS
            method name. This will override fallback behaviour.
        """
        # TODO: we might cache the state-aware-dispatcher since it's almost always
        # the same function.
        if statename not in self.names:
            raise ValueError("State '%s' is unknown to this broker." %
                        statename)
        def inner(func):
            if default:
                target_states = self.names
            else:
                target_states = [statename]

            for target_state in target_states:
                def decorated(*args, **kwargs):
                    return func(*args, **kwargs)
                decorated.func_name = self._get_stateful_name(target_state, func.func_name)
                # insert such decorated function into the caller's class dict
                self._insert_func_at_frame(decorated, 2)
            return self._get_state_aware_dispatcher(func.func_name)
        return inner

    @staticmethod
    def _get_stateful_name(statename, funcname):
        return ( STATEFUL_MARKER + statename + FUNC_NAME_SEPARATOR +
                                    funcname )

    @staticmethod
    def _insert_func_at_frame(func, frame_n):
        current_frame = inspect.currentframe()
        if current_frame is None:
            raise ValueError, "this platform doesn't support python stack frames."
        target_frame = inspect.getouterframes(current_frame)[frame_n][0]
        target_frame.f_locals[func.func_name] = func
            
    # TODO: this might be moved outside this object?
    def transition(self, target_state, when="after"):
        def decorator_func(func):
            if getattr(func, "is_method_dispatcher", False):
                raise ValueError, "transition decorators must be internal to on_state decorators."
            def state_changer(s, *args, **kwargs):
                output_value = func(s, *args, **kwargs)
                s._state.jump(target_state)
                return output_value
            state_changer.func_name = func.func_name
            return state_changer
        return decorator_func



class MissingFunctionError(Exception):
    pass

class WrongStateTransition(Exception):
    pass

class StatefulCaller(object):
    def __init__(self, obj, state, fallback):
        self._state = state
        self._obj = obj
        self._fallback = fallback

    def call(self, funcname, *args, **kwargs):
        f = self._get_func_for_state(self._state.current, funcname)
        return f(*args, **kwargs)

    def _get_func_for_state(self, statename, funcname):
        """
        @return: bound method if it exists,
        @raise: MissingFunctionError otherwise
        """
        f =  getattr(self._obj, STATEFUL_MARKER + statename +
                    FUNC_NAME_SEPARATOR + funcname, None)
        if f is None:
            if self._fallback == statename:
                raise MissingFunctionError("No func defined for '%s' and state"
                    " '%s'" % (funcname, statename))
            else:
                f = self._get_func_for_state(self._fallback, funcname)
        return f

class StateSwitcher(object):
    def __init__(self, statenames):
        self.names = statenames
        self.current = self.names[0]
        
    def go_next(self):
        """go to the next state if available. Otherwise, raise
        WrongStateTransition."""
        current_index = self.names.index(self.current)
        try:
            self.jump(self.names[current_index + 1])
        except IndexError:
            raise WrongStateTransition, "'%s' is already the last state." % self.current

    def go_previous(self):
        current_index = self.names.index(self.current)
        if current_index == 0:
            raise WrongStateTransition, "'%s' is already the first state." % self.current
        self.jump(self.names[current_index - 1])

    def jump(self, name):
        if name in self.names:
            self.current = name
        else:
            raise ValueError, "Unknown state %s" % name


