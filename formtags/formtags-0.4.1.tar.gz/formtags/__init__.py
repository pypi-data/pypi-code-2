import itertools
import logging
import types

import formencode
import formencode.validators
import sqlalchemy.types
import sqlalchemy.orm

from formtags import schema
from formtags import util
from formtags import html

log = logging.getLogger(__name__)

class ValidationError(Exception):
    """
    Exception which is raised when the data is not correctly validated
    by the formencode schema.
    """
    pass

class InvalidField(Exception):
    pass


class State(object):
    pass

class ChainedValidator(object):
    def __init__(self, *objs):
        self._formtag_objs = objs
        self.form_result = {}
        self.form_errors = {}

    def validate(self, data):
        errors = False

        # Keep two separate sets. the processed_keys contains all key's
        # which are 'known' in a processed schema. the extra_keys
        # are keys which are not processed by a schema.
        processed_keys = set()
        extra_keys = set()
        for obj in self._formtag_objs:
            try:
                log.critical('Validating object %s' % obj._instance)
                obj.validate(data)
                log.critical('Validation OK %s' % obj._instance)

                # Only copy key/value pairs which are in the current schema
                for key in obj._schema_class.fields.keys():
                    target_key = obj._get_field_name(key)
                    self.form_result[target_key] = obj.form_result[key]
                    processed_keys.add(target_key)

                    # If the key was in extra_keys set then remove it
                    if target_key in extra_keys:
                        extra_keys.remove(target_key)

                # Add all keys which are not in the processed_keys to the extra
                # set.
                for key in obj.form_result.keys():
                    target_key = obj._get_field_name(key)
                    if target_key not in processed_keys:
                        extra_keys.add(target_key)

            except ValidationError:
                log.critical('Validation failed for object %s' % obj._instance)
                errors = True

                result = dict((obj._get_field_name(key), val) for key, val in
                    obj.form_result.iteritems())

                self.form_errors.update(obj.form_errors)
                self.form_result.update(result)

        # Copy extra keys from the first validator
        obj = self._formtag_objs[0]
        for key in extra_keys:
            if key in obj.form_result:
                self.form_result[key] = obj.form_result[key]

        if errors:
            #  print self.form_errors
            raise ValidationError()

    def from_python(self):
        result = {}
        for obj in self._formtag_objs:
            values = obj.from_python()
            result.update(values)

        return result


class FormTags(object):
    """
    Example usage for pylons::

        import formtags
        import webhelpers.html.builder as builder

        user = model.User()
        # or to edit fetch a user object:
        # user = model.meta.Session.query(model.User).get(id)

        c.usertags = formtags.FormTags(user)

        if request.POST:
            try:
                user = c.usertags.merge(request.POST)
                model.meta.Session.add(user)
                model.meta.Session.commit()
                redirect_to()

            except formtags.ValidationError:
                content = builder.literal(render('/my_template.mako'))
                return formencode.htmlfill.render(content,
                                                  c.usertags.form_result,
                                                  c.usertags.form_errors)
        return render('/my_template.mako')

    In your template you can then use the following::

        ${c.holdingtags.label('name', 'name')}
        ${c.holdingtags.text('name', class_='css-class')}

    """
    def __init__(self, instance, schema_class=None, state=None, fields=[],
                 class_=None, prefix=None):
        """
        Pass an sqlalchemy orm instance and optionally a formencode schema
        class. If no schema class is given then one is automatically generated
        based on the sqlalchem orm instance.
        """
        self._instance = instance
        self._class = class_
        self.prefix = prefix
        if self._class and self._instance:
            raise ValueError("can't specify both the instance and the class "
                             "type.")
        try:
            self._properties = self._find_properties()
        except AttributeError, e:
            raise
            #raise AttributeError('No valid sqlalchemy orm instance given')
        self._htmlbuilder = html.HTMLBuilder()

        if not schema_class:
            self._schema = None
            self._schema_class = schema.generate(fields, self._properties)
        else:
            self._schema = None
            self._schema_class = schema_class
            schema.set_string_maxlength(schema_class, self._properties)

        self._schema_state = state
        self._attribute_aliases = {}
        self._select_options = {}
        self._compare_funcs = {}
        self.form_result = None
        self.form_errors = None
        self._validated = False

    @property
    def errors(self):
        if self.form_errors and self._validated:
            return True
        return False

    def _find_properties(self):
        """ Create a dictionary with all properties of the instance or class """
        properties = util.PropertyDict()

        if self._instance:
            mapper = sqlalchemy.orm.object_mapper(self._instance)
        else:
            mapper = sqlalchemy.orm.class_mapper(self._class)

        properties.update(mapper.class_manager.items())
        return properties

    def set_state(self, key, value):
        if self._schema_state is None:
            self._schema_state = State()
        setattr(self._schema_state, key, value)

    def from_python(self):
        if not self.form_errors:
            return self._schema_class().from_python(self.form_result,
                                                    self._schema_state)
        else:
            return self.form_result

    def validate(self, data):

        # Strip off the prefix name for the keys if set
        if self.prefix:
            data = dict((key[len(self.prefix)+1:], value) for key, value in
                data.iteritems() if key.startswith(self.prefix))

        # Validates
        try:
            result = self._schema_class().to_python(data, self._schema_state)
            self.form_result = result
            return result

        except formencode.Invalid, error:
            self.form_result = error.value
            self.form_errors = error.error_dict or {}

            # And prepend the prefix for the error_dict for htmlfill..
            if self.prefix:
                self.form_errors = dict((self._get_field_name(key), val) for
                    key, val in self.form_errors.iteritems())
                print self.form_errors
            raise ValidationError('invalid data input')
        finally:
            self._validated = True
        return None

    def merge(self, data, instance=None, exceptions=None):
        """
        Merge the data (for example request.POST) to the instance given on
        initialization and return it.

        The formencode resultset is available in self.form_result. If the
        formencode validation doesn't succeed then a ValidatorError exception
        is thrown. The errors are in self.form_errors and the results in
        self.form_results.
        """
        if not self._validated:
            self.validate(data)

        if not instance:
            instance = self._instance

        # Iterate over the properties in the schema class. DON'T iterate over
        # the data dictionary or the instance properties since that is
        # not secure...
        for key in self._schema_class.fields:
            if exceptions and key in exceptions:
                continue

            if key in self.form_result:
                setattr(instance, key, self.form_result[key])
            else:
                log.warning('attribute %r not found in POST %r' % (
                    key, instance))
        return instance

    def bind_options(self, attribute_name, options, prepend=None):
        """
        Bind options to the given attribute_name. This is used for
        html select and radiobutton elements.

        Options should be a list (or preferably a generator) with tuples of
        (value, label).
        """
        if prepend:
           options = itertools.chain(prepend, options)

        self._select_options[attribute_name] = options

    def set_alias(self, alias, target):
        """
        Set an alias to another attribute. For example when you want to
        display a password field twice for confirmation, you do::
            .set_alias('password_confirm', 'password")
        """
        self._attribute_aliases[alias] = target

    def set_validator(self, field, validator):
        """
        Set a formencode validator upon a specific field.
        """
        if field not in self._properties.keys():
            raise IndexError('given field not found in database')
        sql_field = self._properties[field]
        if isinstance(validator, formencode.validators.String):
            validator.max = sql_field.type.length
        self._schema_class.add_field(field, validator)

    @util.html_tag
    def label(self, attribute_name, value, html_attributes):
        """
        Create a html label tag for the given attribute_name.
        """
        html_attributes['for'] = self._unique_id(attribute_name)
        return self._htmlbuilder.label(html_attributes, value)

    @util.html_tag
    def text(self, attribute_name, html_attributes):
        """
        Create an input type=text html tag
        """
        self._generic_input_tag(attribute_name, html_attributes)
        html_attributes.overwrite('type', 'text')
        return self._htmlbuilder.input(html_attributes)

    @util.html_tag
    def password(self, attribute_name, html_attributes):
        """
        Create an input type=password html tag
        """
        self._generic_input_tag(attribute_name, html_attributes)
        html_attributes.overwrite('type', 'password')
        return self._htmlbuilder.input(html_attributes)

    @util.html_tag
    def hidden(self, attribute_name, html_attributes):
        """
        Create an input type=password html tag
        """
        self._generic_input_tag(attribute_name, html_attributes)
        html_attributes.overwrite('type', 'hidden')
        return self._htmlbuilder.input(html_attributes)

    @util.html_tag
    def checkbox(self, attribute_name, html_attributes):
        """
        Create a checkbox html tag
        """
        result = self._find_attribute(attribute_name)
        if result:
            html_attributes['checked'] = 'checked'

        html_attributes.overwrite('type', 'checkbox')
        html_attributes['name'] = self._get_field_name(attribute_name)
        html_attributes['id'] = self._unique_id(attribute_name)

        self._set_type_as_class(attribute_name, html_attributes)
        self._set_if_required(attribute_name, html_attributes)
        return self._htmlbuilder.input(html_attributes)

    @util.html_tag
    def radio(self, attribute_name, html_attributes):
        """
        Create a checkbox html tag
        """
        result = self._find_attribute(attribute_name)
        if result == html_attributes['value']:
            html_attributes['checked'] = 'checked'


        if isinstance(html_attributes['value'], bool):
            html_attributes.overwrite('value',
                'true' if html_attributes['value'] else 'false')

        html_attributes.overwrite('type', 'radio')
        html_attributes['name'] = self._get_field_name(attribute_name)
        html_attributes['id'] = self._unique_id(attribute_name)

        self._set_type_as_class(attribute_name, html_attributes)
        self._set_if_required(attribute_name, html_attributes)

        return self._htmlbuilder.input(html_attributes)


    @util.html_tag
    def textarea(self, attribute_name, html_attributes):
        """
        Create a textarea html tag
        """
        value = self._find_attribute(attribute_name)
        self._set_type_as_class(attribute_name, html_attributes)
        self._set_if_required(attribute_name, html_attributes)
        html_attributes['rows'] = 3
        html_attributes['cols'] = 20
        html_attributes['name'] = self._get_field_name(attribute_name)
        html_attributes['id'] = self._unique_id(attribute_name)
        return self._htmlbuilder.textarea(html_attributes, value)

    @util.html_tag
    def select(self, attribute_name, html_attributes):
        """
        Create a select element. To bind options to this element see
        bind_options()
        """
        value = self._find_attribute(attribute_name)
        self._set_type_as_class(attribute_name, html_attributes)
        self._set_if_required(attribute_name, html_attributes)

        html_attributes['name'] = self._get_field_name(attribute_name)
        html_attributes['id'] = self._unique_id(attribute_name)

        options = self._select_options.get(attribute_name, [])
        return self._htmlbuilder.select(html_attributes, options, value)

    @util.html_tag
    def radiogroup(self, attribute_name, html_attributes):
        """
        Yields a html.RadioButtonCtrl for each binded option (see
        bind_option()).

        see html.RadioButtonCtrl()
        """
        value = self._find_attribute(attribute_name)

        self._set_type_as_class(attribute_name, html_attributes)
        self._set_if_required(attribute_name, html_attributes)

        html_attributes['name'] = attribute_name
        html_attributes['id'] = self._unique_id(attribute_name)

        options = self._select_options.get(attribute_name, [])
        for i, (opt_value, opt_label) in enumerate(options):

            # Create a copy of the html attributes and modify for option
            opt_attributes = util.HTMLAttributes(html_attributes)
            opt_attributes.overwrite('id', '%s-%d' % (html_attributes['id'], i))
            opt_attributes.overwrite('value', opt_value)
            if opt_value == value:
                opt_attributes['checked'] = 'checked'

            yield html.RadioButtonCtrl(opt_attributes, opt_label)

    @util.html_tag
    def checkboxgroup(self, attribute_name, html_attributes):
        """
        Yields a html.CheckboxCtrl for each binded option (see
        bind_option()).

        see html.CheckboxCtrl()
        """
        value = self._find_attribute(attribute_name)
        #self._set_type_as_class(attribute_name, html_attributes)
        self._set_if_required(attribute_name, html_attributes)

        html_attributes['name'] = attribute_name
        html_attributes['id'] = self._unique_id(attribute_name)

        options = self._select_options.get(attribute_name, [])
        for i, (opt_value, opt_label) in enumerate(options):

            # Create a copy of the html attributes and modify for option
            opt_attributes = util.HTMLAttributes(html_attributes)
            opt_attributes.overwrite('id', '%s-%d' % (html_attributes['id'], i))
            opt_attributes.overwrite('value', opt_value)

            if self.compare(attribute_name, value, opt_value):
                opt_attributes['checked'] = 'checked'

            yield html.CheckboxCtrl(opt_attributes, opt_label)


    def compare(self, attribute_name, sql_val, option_val):
        func = self._compare_funcs.get(attribute_name, lambda x,y: x == y)
        return func(sql_val, option_val)

    def compare_function(self, attribute_name, func):
        self._compare_funcs[attribute_name] = func


    def _get_field_name(self, attribute_name):
        if self.prefix:
            return '%s-%s' % (self.prefix, attribute_name)
        return attribute_name

    def _generic_input_tag(self, attribute_name, html_attributes):
        """
        Create a HTML input element. This method is used by .text(),
        .password() and .hidden().
        """
        result = self._find_attribute(attribute_name)

        self._set_type_as_class(attribute_name, html_attributes)
        self._set_if_required(attribute_name, html_attributes)

        # Convert python value via formencode schema
        if attribute_name in self._schema_class.fields:
            validator = self._schema_class.fields[attribute_name]
            result = validator.from_python(result)

        html_attributes['value'] = result
        html_attributes['name'] = self._get_field_name(attribute_name)
        html_attributes['id'] = self._unique_id(attribute_name)


    def _set_type_as_class(self, attribute_name, html_attributes):
        """
        Add a css class with the type of the attribute_name to the html
        tag.
        """
        # De-alias
        if attribute_name in self._attribute_aliases:
            attribute_name = self._attribute_aliases[attribute_name]

        try:
            #result = util.walk_object(self._properties, attribute_name)
            result = self._properties[attribute_name].property.columns[0]
        except AttributeError:
            raise InvalidField('The field "%s" is not available in %s '
                               'formencode schema' % (attribute_name,
                                                      self._schema_class))
        except KeyError:
            result = None

        classname = 'type-unknown'

        if result is None:
            classname = 'type-none'

        elif isinstance(result.type, (sqlalchemy.types.Unicode,
                                    sqlalchemy.types.String)):
            classname = 'type-string'

        elif isinstance(result.type, sqlalchemy.types.Integer):
            classname = 'type-integer'

        elif isinstance(result.type, sqlalchemy.types.Boolean):
            classname = 'type-boolean'

        html_attributes['class'].add(classname)

    def _set_if_required(self, attribute_name, html_attributes):
        """
        Add the css class 'required' to html fields which are required
        see _is_required()
        """
        if self._is_required(attribute_name):
            html_attributes['class'].add('required')

    def _find_attribute(self, attribute_name):
        """
        Return the value of the given attribute_name
        """
        # De-alias
        #if attribute_name in self._attribute_aliases:
        #    attribute_name = self._attribute_aliases[attribute_name]
        result = None
        try:
            if self._instance:
                result = util.walk_object(self._instance, attribute_name)
            else:
                result = util.walk_object(self._class, attribute_name)
                property = types.__builtins__['property']
                if result and result.__class__ == property:
                    return None

        except AttributeError:
            if (attribute_name not in self._attribute_aliases and
                attribute_name not in self._schema_class.fields):
                raise AssertionError('Attribute "%s" does not exist.' %
                                     attribute_name)

        if self._instance is None or result == self._instance or result is None:
            return ''
        return result

    def _is_required(self, attribute_name):
        """
        Return True if the given attribute_name is required.
        """
        if attribute_name in self._schema_class.fields:
            validator = self._schema_class.fields[attribute_name]
            if validator.not_empty:
                return True
        else:
            if attribute_name not in self._attribute_aliases:
                raise InvalidField('The field "%s" is not available in %s '
                                   'formencode schema' % (attribute_name,
                                                          self._schema_class))

        return False

    def _unique_id(self, attribute_name):
        """
        Generate a unique id for an instance. This is used for the 'id'
        attribute in the html tags.
        """
        instance = self._properties.get(attribute_name, attribute_name)
        uid = 'field-%s-%s' % (id(self), id(instance))
        return uid

