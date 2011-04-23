#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf8

from unittest import TestCase, main
from pystateful.stateful import StateBroker, MissingFunctionError

class TestStateBroker(TestCase):
    def setUp(self):
        sb = StateBroker("first", "second")

        class MyObject(object):
            @sb.on_state("first")
            def do_something(self):
                self._state.jump("second")
                return "first_state"

            @sb.on_state("second")
            def do_something(self):
                return "second_state"

        MyObject = sb.stateful(MyObject)

        self.stateful_class = MyObject
        self.stateful_object = MyObject()

    def test_basic_state_switching_changes_states(self):
        stateful_object = self.stateful_object

        self.assertEquals("first_state", stateful_object.do_something())
        self.assertEquals("second_state", stateful_object.do_something())

    def test_inherited_classes_are_stateful(self):
        class Inherited(self.stateful_class):
            pass
        
        stateful_object = Inherited()

        self.assertEquals("first_state", stateful_object.do_something())
        self.assertEquals("second_state", stateful_object.do_something())

    def test_invalid_state_names_arent_allowed(self):
        self.assertRaises(ValueError, StateBroker, "oksksskààà")
        self.assertRaises(ValueError, StateBroker, "1234aaa")
        self.assertRaises(ValueError, StateBroker, "a" * 65)
        self.assertRaises(ValueError, StateBroker, "")

    def test_empty_statebroker_isnt_allowed(self):
        self.assertRaises(ValueError, StateBroker)

    def test_invalid_on_state_names_arent_allowed(self):
        sb = StateBroker("first", "second")
        self.assertRaises(ValueError, sb.on_state, "third")

    def test_duplicate_statenames_arent_allowed(self):
        self.assertRaises(ValueError, StateBroker, "first", "first")

    def test_fallback_state_is_employed_if_unspecified(self):
        sb = StateBroker("first", "second", fallback="first")

        class MyObject(object):
            @sb.on_state("first")
            # TODO: qualcosa per cambiare lo stato "just before returning"?
            def do_something(self):
                self._state.jump("second")
                return "first_state"

        MyObject = sb.stateful(MyObject)
              
        stateful_object = MyObject()

        self.assertEquals("first_state", stateful_object.do_something())
        self.assertEquals("first_state", stateful_object.do_something())

    def test_default_state_wins_on_fallback(self):
        sb = StateBroker("first", "second", "third", fallback="third")

        class MyObject(object):
            @sb.on_state("first", default=True)
            # TODO: qualcosa per cambiare lo stato "just before returning"?
            def do_something(self):
                self._state.jump("second")
                return "first_state"

        MyObject = sb.stateful(MyObject)

        stateful_object = MyObject()

        self.assertEquals("first_state", stateful_object.do_something())
        self.assertEquals("first_state", stateful_object.do_something())

    def test_fallback_state_breaks_if_unspecified(self):
        sb = StateBroker("first", "second", "third", fallback="third")

        class MyObject(object):
            @sb.on_state("first")
            # TODO: qualcosa per cambiare lo stato "just before returning"?
            def do_something(self):
                self._state.jump("second")
                return "first_state"

        MyObject = sb.stateful(MyObject)

        stateful_object = MyObject()

        self.assertEquals("first_state", stateful_object.do_something())
        self.assertRaises(MissingFunctionError, stateful_object.do_something)

    def test_theres_no_default_fallback(self):
        sb = StateBroker("first", "second")

        class MyObject(object):
            @sb.on_state("first")
            # TODO: qualcosa per cambiare lo stato "just before returning"?
            def do_something(self):
                self._state.jump("second")
                return "first_state"

        MyObject = sb.stateful(MyObject)

        stateful_object = MyObject()

        self.assertEquals("first_state", stateful_object.do_something())
        self.assertRaises(MissingFunctionError, stateful_object.do_something)

    def test_previous_next_state_switching_changes_states_accordingly(self):
        sb = StateBroker("first", "second")

        class MyObject(object):
            @sb.on_state("first")
            # TODO: qualcosa per cambiare lo stato "just before returning"?
            def do_something(self):
                self._state.go_next()
                return "first_state"

            @sb.on_state("second")
            # TODO: qualcosa per cambiare lo stato "just before returning"?
            def do_something(self):
                self._state.go_previous()
                return "second_state"

        MyObject = sb.stateful(MyObject)

        stateful_object = MyObject()

        self.assertEquals("first_state", stateful_object.do_something())
        self.assertEquals("second_state", stateful_object.do_something())
        self.assertEquals("first_state", stateful_object.do_something())

    def test_transition_switches_states_on_successful_method_invocation(self):
        sb = StateBroker("first", "second")


        class MyObject(object):

            @sb.on_state("first")
            @sb.transition("second")
            def do_something(self):
                return "first_state"

            @sb.on_state("second")
            @sb.transition("first")
            def do_something(self):
                return "second_state"

        MyObject = sb.stateful(MyObject)

        stateful_object = MyObject()

        self.assertEquals("first_state", stateful_object.do_something())
        self.assertEquals("second_state", stateful_object.do_something())
        self.assertEquals("first_state", stateful_object.do_something())

    def test_transition_decorators_cannot_be_outside_on_state_decorators(self):
        sb = StateBroker("first", "second")

        class MyObject(object):
            def do_something(self):
                return "first_state"
            do_something = sb.on_state("first")(do_something)
            self.assertRaises(ValueError, sb.transition("second"), do_something)



if __name__ == "__main__":
    main()

