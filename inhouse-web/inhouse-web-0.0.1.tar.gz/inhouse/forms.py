# -*- coding: utf-8 -*-

"""Validation forms"""

from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from issues.models import Issue
from library import format_minutes_to_time
import models


CHOICE_HOURS = [(x, str(x)) for x in range(0, 13)]
CHOICE_MINUTES = [(x, str(x * 15)) for x in range(0, 4)]

CHOICE_TIME = [(x, format_minutes_to_time(x * 15)) for x in range(0, 96)]


class DateInput(forms.TextInput):
    """Datepicker widget"""

    class Media:

        css = {}
        js = {}

    def render(self, name, value, attrs=None):
        output = super(DateInput, self).render(name, value, attrs)
        output += mark_safe(DateInput().media)
        return output + mark_safe(u'''<script type="text/javascript">
        jQuery("#id_%s").datepicker({});
        </script>''' % name)


class TicketInput(forms.TextInput):
    """Ticket search with autocompletion.

    http://docs.jquery.com/Plugins/Autocomplete
    """

    class Media:

        css = {
            'all': ('/static/autocomplete/jquery.autocomplete.css',)
        }
        js = (
            '/static/autocomplete/lib/jquery.js',
            '/static/autocomplete/lib/jquery.bgiframe.min.js',
            '/static/autocomplete/lib/jquery.ajaxQueue.js',
            '/static/autocomplete/jquery.autocomplete.js'
        )

    def render(self, name, value, attrs=None):
        output = super(TicketInput, self).render(name, value, attrs)
        output += mark_safe(TicketInput().media)
        return output + mark_safe(u'''<script type="text/javascript">
        jQuery("#id_%s").autocomplete("/json/issue", {
        max: 10,
        highlight: false,
        multiple: false,
        multipleSeparator: ", ",
        scroll: true,
        scrollHeight: 300,
        matchContains: true,
        formatResult : function(row) {
        return row[0].replace(/ (\(.+?\))/gi, '');
        },
        extraParams: { tracker: function() { return $("#id_tracker").val(); } },
        });
        </script>''' % name)


class BookingForm(forms.Form):

    customer = forms.ChoiceField(
        label=_(u'Customer'), required=True,
        widget=forms.Select(attrs={'onchange': 'JS_setProjects(this.value);'}))
    project = forms.ChoiceField(
        label=_(u'Project'), required=True,
        widget=forms.Select(attrs={'onchange': 'JS_setProjectsteps(this.value);'}))
    step = forms.ChoiceField(label=_(u'Step'), required=True)
    from_time = forms.CharField(label=_(u'Start'), required=False,
                                widget=forms.TextInput(
                                    attrs={'size': 5, 'maxlength': 5}))
    #from_time = forms.ChoiceField(label=_(u'Start'), choices=CHOICE_TIME)
    to_time = forms.CharField(label=_(u'End'), required=False,
                              widget=forms.TextInput(
                                  attrs={'size': 5, 'maxlength': 5}))
    hours = forms.ChoiceField(choices=CHOICE_HOURS, label=_(u'Hours'))
    minutes = forms.ChoiceField(choices=CHOICE_MINUTES, label=_(u'Minutes'))
    date = forms.DateField(label=_(u'Date'),
                           widget=DateInput(attrs={'size': 10}))
    #date = forms.DateField(label=_(u'Date'),
                           #widget=forms.DateInput())
    title = forms.CharField(label=_(u'Title'), required=False,
                            widget=forms.TextInput(attrs={'size': 60}))
    description = forms.CharField(label=_(u'Description'), required=False,
                                  widget=forms.Textarea(attrs={'cols': 63,
                                                               'rows': 5}))
    tracker = forms.ChoiceField(label=_(u'Issue tracker'), required=False)
    issue_no = forms.CharField(label=_(u'Issue no.'), required=False,
                                widget=TicketInput(attrs={'size': 35}))

    def clean(self):
        data = self.cleaned_data
        data['title'] = data['title'].strip()
        data['description'] = data['description'].strip()
        minutes = int(data['minutes']) * 15 + int(data['hours']) * 60
        if minutes == 0:
            raise forms.ValidationError(
                _(u'Please select at last 15 minutes.'))
        if 'issue_no' in data:
            data['issue_no'] = data['issue_no'].replace('#', '')
            issue = Issue.by_tracker_id(data['tracker'],
                                        data['issue_no'])
            if issue.id == None:
                raise forms.ValidationError(
                    _(u'The issue #%s cannot be found or is not valid.')
                    % data['issue_no'])
        # No title and issue input
        if not data.get('issue_no', None):
            if not data.get('title', None) or not data.get('description',
                                                           None):
                raise forms.ValidationError(
                    _(u'Please support a title and description or select a issue.'))
        return data

    def set_customer_choices(self, user):
        choices = [('', _(u'Please select'))]
        bound_field = self['customer']
        for customer in user.account.get_bookable_customers():
            choices.append((customer.id, customer.name))
        bound_field.field.choices = choices

    def set_project_choices(self, user, customer=None):
        choices = [('', _(u'Please select'))]
        bound_field = self['project']
        if customer:
            for project in models.Project.objects.get_by_customer(
                customer, active_only=True, user=user):
                choices.append((project.id, project.name))
        bound_field.field.choices = choices

    def set_step_choices(self, user, project=None):
        bound_field = self['step']
        choices = [('', _(u'Please select'))]
        if project:
            query = models.ProjectStep.objects.filter(project=project)
            query = query.filter(status__in=(models.STEP_STATUS_OPEN,))
            for step in query:
                choices.append((step.id, step.name))
        bound_field.field.choices = choices

    def set_tracker_choices(self, user, project=None):
        choices = [('', _(u'Please select'))]
        bound_field = self['tracker']
        if project:
            query = models.ProjectTracker.objects.filter(project=project)
            for rel in query:
                choices.append((rel.tracker.id, rel.tracker.name))
        bound_field.field.choices = choices


class UserProfileForm(forms.Form):

    first_name = forms.CharField(label=_(u'First name'), max_length=30,
                                 required=False)
    last_name = forms.CharField(label=_(u'Last name'), max_length=30,
                                required=False)
    email = forms.EmailField(label=_(u'E-mail'), required=True,
                             widget=forms.TextInput(attrs={'size': 40}))
    birthday = forms.CharField(label=_(u'Birthday'), required=False,
                               widget=forms.DateInput())
    street = forms.CharField(label=_(u'Street'), max_length=30,
                             required=False,
                             widget=forms.TextInput(attrs={'size': 40}))
    zip_code = forms.CharField(label=_(u'ZIP code'), max_length=30,
                               help_text=_('E.g. 54321'),
                               required=False,
                               widget=forms.TextInput(attrs={'size': 10}))
    city = forms.CharField(label=_(u'City'), max_length=30,
                           required=False)
    country = forms.ChoiceField(label=_(u'Country'), required=False)
    phone_landline = forms.CharField(label=_(u'Phone no. (landline)'),
                                     max_length=40, required=False)
    phone_mobile = forms.CharField(label=_(u'Phone no. (mobile)'),
                                   max_length=40, required=False)
    fax = forms.CharField(label=_(u'Fax no.'),
                          max_length=40, required=False)
    url = forms.URLField(label=_(u'URL'), max_length=200, required=False,
                         widget=forms.TextInput(attrs={'size': 40}))
    job = forms.CharField(label=_(u'Job'), max_length=80, required=False,
                          widget=forms.TextInput(attrs={'size': 40}))
    personnel_no = forms.CharField(label=_(u'Personell no.'),
                                   required=False,
                                   widget=forms.TextInput(
                                       attrs={'readonly': 'readonly'}))

    def set_country_choices(self):
        choices = []
        bound_field = self['country']
        countries = models.Country.objects.all()
        for country in countries:
            choices.append([country.id, country.printable_name])
        bound_field.field.choices = choices


class SearchForm(forms.Form):

    from_date = forms.CharField(label=_(u'From'), required=False,
                                widget=forms.DateInput())
    to_date = forms.CharField(label=_(u'To'), required=False,
                                widget=forms.DateInput())
    customer = forms.ChoiceField(
        label=_(u'Customer'), required=False,
        widget=forms.Select(attrs={'onchange': 'JS_setProjects(this.value);'}))
    project = forms.ChoiceField(
        label=_(u'Project'), required=False,
        widget=forms.Select(attrs={'onchange': 'JS_setProjectsteps(this.value);'}))
    step = forms.ChoiceField(label=_(u'Step'), required=False)
    tracker = forms.ChoiceField(label=_(u'Issue tracker'), required=False)
    issue_no = forms.CharField(label=_(u'Issue no.'), required=False,
                                widget=TicketInput(attrs={'size': 10}))

    def set_customer_choices(self, user):
        choices = [('', _(u'Please select'))]
        bound_field = self['customer']
        for customer in user.account.get_bookable_customers():
            choices.append((customer.id, customer.name))
        bound_field.field.choices = choices

    def set_project_choices(self, user, customer=None):
        choices = [('', _(u'Please select'))]
        bound_field = self['project']
        if customer:
            for project in models.Project.objects.get_by_customer(
                customer, active_only=True, user=user):
                choices.append((project.id, project.name))
        bound_field.field.choices = choices

    def set_step_choices(self, user, project=None):
        bound_field = self['step']
        choices = [('', _(u'Please select'))]
        if project:
            query = models.ProjectStep.objects.filter(project=project)
            query = query.filter(status__in=(models.STEP_STATUS_OPEN,))
            for step in query:
                choices.append((step.id, step.name))
        bound_field.field.choices = choices

    def set_tracker_choices(self, user, project=None):
        choices = [('', _(u'Please select'))]
        bound_field = self['tracker']
        if project:
            query = models.ProjectTracker.objects.filter(project=project)
            for rel in query:
                choices.append((rel.tracker.id, rel.tracker.name))
        bound_field.field.choices = choices