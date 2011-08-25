"""
Test webhelper html wrappers.
"""
from pepperedform.render import (build_id, sequence_getter, mapping_getter,
        rename_getter, make_start_token, field_error, input_tag, checkbox_tag,
        radio_tag, textarea_tag, select_tag, mapping, sequence, rename)


class MockCallerStack(object):
    def _push_frame(*args, **kwargs):
        pass

    def _pop_frame(*args, **kwargs):
        pass


class MockContext(object):
    
    def __init__(self, caller=None):
        self.attrs = {}
        self.out = []
        if caller:
            self.attrs['caller'] = caller
        self.caller_stack = MockCallerStack()

    def __getitem__(self, k):
        return self.attrs[k]

    def write(self, s):
        self.out.append(s)
    
    def serialize(self):
        return (u''.join(self.out)).encode('utf8')


class MockCaller(object):

    def __init__(self, body_text):
        self.body_text = body_text

    def body(self, *args, **kwargs):
        return self.body_text

    def caller_stack(*args, **kwargs):
        pass


class TestRender(object):

    def _get_mock_getter(self):
        def _mock_getter(items, name, if_missing=None):
            if items:
                return items.get(name, if_missing)
            return if_missing
        return _mock_getter

    def test_build_id(self):
        render_kwargs = {
            'id_stack': ['dates', '1']
        }
        name = 'day'
        assert build_id(render_kwargs, name) == 'dates_1_day'

    def test_sequence_getter_missing(self):
        items = None
        if_missing = tuple()
        name = 'day'
        result = sequence_getter(items, name, if_missing=if_missing)
        assert result is if_missing, \
                'Should return if_missing if items is falsy.'
        
    def test_sequence_getter(self):
        items = '15'
        if_missing = tuple()
        name = 'day'
        result = sequence_getter(items, name, if_missing=if_missing)
        assert result == '15', \
            'Should return items if items is not falsy.'


    def test_rename_getter_missing(self):
        items = None
        if_missing = tuple()
        name = 'day'
        result = rename_getter(items, name, if_missing=if_missing)
        assert result is if_missing, \
                'Should return if_missing if items is falsy.'
        
    def test_rename_getter(self):
        items = '15'
        if_missing = tuple()
        name = 'day'
        result = rename_getter(items, name, if_missing=if_missing)
        assert result == '15', \
            'Should return items if items is not falsy.'

    def test_mapping_getter_missing(self):
        items = {}
        if_missing = tuple()
        name = 'day'
        result = mapping_getter(items, name, if_missing=if_missing)
        assert result is if_missing, \
                'Should return if_missing if name not in items.'
        
    def test_mapping_getter(self):
        items = {
            'day': '15'
        }
        if_missing = tuple()
        name = 'day'
        result = mapping_getter(items, name, if_missing=if_missing)
        assert result == '15', \
            'Should return value for key name in items if it exists.'

    def test_make_start_token(self):
        name = 'days'
        type_ = 'sequence'
        assert make_start_token(name, type_) == 'days:sequence'
        
    def test_field_error_missing(self):
        render_kwargs = {
            'getter': self._get_mock_getter(),
            'errors': {},
            'id_stack': []
        }
        name = 'day'
        error = field_error(render_kwargs, name)
        assert not error, 'No error should exist'

    def test_field_error(self):
        day_error = 'Today is the wrong day'
        render_kwargs = {
            'getter': self._get_mock_getter(),
            'errors': {
                'day': day_error
             },
            'id_stack': []
        }
        name = 'day'
        error = field_error(render_kwargs, name)
        assert error and error == day_error

    def test_input_tag_brainless(self):
        """
        Do a brainless test to see if these have runtime errors.
        """
        render_kwargs = {
            'getter': self._get_mock_getter(),
            'defaults': {
                'day': '15'
            },
            'id_stack': []
        }
        name = 'day'
        assert input_tag(render_kwargs, name)

    def test_checkbox_tag_brainless(self):
        name = 'is_today'
        render_kwargs = {
            'getter': self._get_mock_getter(),
            'defaults': {
                name: True
            },
            'id_stack': []
        }
        assert checkbox_tag(render_kwargs, name)

    def test_radio_tag_brainless(self):
        """  """
        # This thing is real odd because we have to wrap in rename.
        name = 'monday'
        render_kwargs = {
            'getter': self._get_mock_getter(),
            'defaults': {
                name: True
            },
            'id_stack': []
        }
        value = name
        assert radio_tag(render_kwargs, name, value)

    def test_textarea_tag_brainless(self):
        render_kwargs = {
            'getter': self._get_mock_getter(),
            'defaults': {
                'coffee': 'I think I will.'
            },
            'id_stack': []
        }
        name = 'coffee'
        assert textarea_tag(render_kwargs, name)

    def test_select_tag_brainless(self):
        render_kwargs = {
            'getter': self._get_mock_getter(),
            'defaults': {
                'roast': ['dark']
            },
            'id_stack': []
        }
        name = 'roast'
        options = [('dark', 'Dark'), ('light', 'Light'), ('medium', 'Medium')]
        assert select_tag(render_kwargs, options, name)

    def test_mapping_brainless(self):
        render_kwargs = {
            'getter': self._get_mock_getter(),
            'defaults': {
                'roast': ['dark']
            },
            'errors': None,
            'id_stack': [],
            'closed': True
        }
        caller = MockCaller(u'Body Text')
        context = MockContext(caller=caller)
        assert mapping(context, render_kwargs, 'coffee') == ''
        assert context.serialize()
