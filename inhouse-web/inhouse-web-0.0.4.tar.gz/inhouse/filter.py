# -*- coding: utf-8 -*-

from django.contrib.admin.filterspecs import FilterSpec, ChoicesFilterSpec
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext as _


class DepartmentFilterSpec(ChoicesFilterSpec):

    def __init__(self, f, request, params, model, model_admin, field_path):
        super(DepartmentFilterSpec, self).__init__(f, request, params, model,
                                                   model_admin, field_path)
        rel_name = f.rel.get_related_field().name
        self.lookup_kwarg = '%s__%s__exact' % (f.name, rel_name)
        self.lookup_val = request.GET.get(self.lookup_kwarg, None)
        if request.user.is_superuser:
            query = model.objects.all()
        else:
            query = model.objects.filter(department__departmentuser=request.user)
        values_list = query.values_list('department__id', 'department__name')
        self.lookup_choices = list(set((pk, val) for pk, val in values_list if val))
        self.lookup_choices.sort()

    def choices(self, cl):
        yield {'selected': self.lookup_val is None,
                'query_string': cl.get_query_string({}, [self.lookup_kwarg]),
                'display': _('All')}
        for pk, val in self.lookup_choices:
            yield {'selected': smart_unicode(val) == pk,
                    'query_string': cl.get_query_string({self.lookup_kwarg: pk}),
                    'display': val}
    def title(self):
        return _('%(field_name)s') % \
            {'field_name': self.field.verbose_name}


class InvoiceFilterSpec(ChoicesFilterSpec):
    """Filter bookings by invoice no."""

    def __init__(self, f, request, params, model, model_admin, field_path):
        super(InvoiceFilterSpec, self).__init__(f, request, params, model,
                                                model_admin, field_path)
        self.field_generic = '%s__' % self.field.name
        self.params = dict([(k, v) for k, v in params.items() if k.startswith(self.field_generic)])
        print self.params
        self.links = (
            (_('All'), {}),
            (_('With invoice no.'), {'%s__isnull' % self.field.name: False,}),
            (_('Without invoice no.'), {'%s__isnull' % self.field.name: True,}),
        )

    def choices(self, cl):
        for title, param_dict in self.links:
            unicode_param_dict = {}
            for k, v in param_dict.items():
                unicode_param_dict[unicode(k)] = unicode(v)
            #yield {'selected': self.params == param_dict,
            yield {'selected': self.params == unicode_param_dict,
                   'query_string': cl.get_query_string(param_dict, [self.field_generic]),
                   'display': title}

    def title(self):
        return self.field.verbose_name


FilterSpec.filter_specs.insert(0, (lambda f: getattr(
    f, 'department_filter', False), DepartmentFilterSpec))

FilterSpec.filter_specs.insert(1, (lambda f: getattr(
    f, 'invoice_filter', False), InvoiceFilterSpec))
