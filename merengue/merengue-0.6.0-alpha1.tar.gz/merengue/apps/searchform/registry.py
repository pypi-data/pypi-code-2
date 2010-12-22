from searchform.utils import import_module


class SearchFormNotRegistered(Exception):
    pass


class SearchFormFilterError(Exception):
    pass


class SearchFormRegistration(object):

    def __init__(self, key, name, search_form, filters=[]):
        self.key = key
        self.name = name
        self.search_form = search_form
        self.filters = []

        # filter validation
        for filter in filters:
            field = self.search_form.fields.get(filter, None)
            if field is None:
                raise SearchFormFilterError("The filter '%s' is not a field "
                                            "of the search form '%s'"
                                            % (filter, unicode(self.name)))

            options = getattr(field, 'options', None)
            if options is None:
                raise SearchFormFilterError("The filter '%s' is not a valid "
                                            "filter because is does not have "
                                            "an options attribute" % filter)

        self.filters.extend(filters)

        if not self.filters:
            # auto fill the filters
            for field_name, field in self.search_form.fields.items():
                # we don't use hasattr(field, 'options') to avoid
                # database queries that increases the import time a lot
                if 'options' in dir(field):
                    self.filters.append(field_name)

    def get_filter_options(self, filter_name):
        if filter_name not in self.filters:
            raise SearchFormFilterError("The filter '%s' is not available in "
                                        "this search form registration: '%s'"
                                        % (filter_name, unicode(self.name)))
        field = self.search_form.fields[filter_name]
        return [option for option in field.options if option[0] != '']

    def can_select_multiple_options(self, filter_name):
        if filter_name not in self.filters:
            raise SearchFormFilterError("The filter '%s' is not available in "
                                        "this search form registration: '%s'"
                                        % (filter_name, unicode(self.name)))
        field = self.search_form.fields[filter_name]
        for op, label in field.operators:
            if op == 'in':
                return True
        return False


class SearchFormRegistry(object):
    REGISTERING = False

    def __init__(self):
        self._registry = []

    def register_form(self, search_form, key=None, name=None, filters=[]):
        if key is None:
            key = search_form.__name__.lower()

        if name is None:
            name = key

        if self.is_registered(key):
            raise ValueError('Another form is already registered '
                             'with the key %s' % key)

        setattr(search_form, 'class_name', key)
        registration = SearchFormRegistration(key, name, search_form, filters)
        self._registry.append(registration)

    def _get_registration(self, key):
        for registration in self._registry:
            if registration.key == key:
                return registration
        all_registered_keys = [r.key for r in self._registry]
        raise SearchFormNotRegistered(
            'Search form %s not registered. Options are: %s'
            % (key, ', '.join(all_registered_keys)),
        )

    def get_form_class(self, key):
        registration = self._get_registration(key)
        return registration.search_form

    def get_filters(self, key):
        registration = self._get_registration(key)
        return registration.filters

    def get_filter_options(self, key, filter_name):
        registration = self._get_registration(key)
        return registration.get_filter_options(filter_name)

    def can_select_multiple_options(self, key, filter_name):
        registration = self._get_registration(key)
        return registration.can_select_multiple_options(filter_name)

    def is_registered(self, key):
        try:
            self.get_form_class(key)
        except SearchFormNotRegistered:
            return False
        else:
            return True

    def get_choices(self):
        for registration in self._registry:
            yield (registration.key, registration.name)

    def autodiscover(self):
        if SearchFormRegistry.REGISTERING:
            return
        SearchFormRegistry.REGISTERING = True

        import imp
        from django.conf import settings

        for app in settings.INSTALLED_APPS:
            try:
                app_path = import_module(app).__path__
            except AttributeError:
                continue

            # use imp.find_module to find the app's forms.py
            try:
                imp.find_module('forms', app_path)
            except ImportError:
                continue

            # import the app's forms.py file
            forms_module = import_module("%s.forms" % app)
            register_forms_func = getattr(forms_module, 'register_search_forms', None)
            if register_forms_func and callable(register_forms_func):
                # do app's search forms registration
                register_forms_func()

        # autodiscover was successful, reset loading flag.
        SearchFormRegistry.REGISTERING = False

search_form_registry = SearchFormRegistry()
