# -*- coding: utf-8 -*-

"""Validation forms and widgets"""

from datetime import datetime, time

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from issues.models import Issue
from library import format_minutes_to_time
import models


CHOICE_HOURS = [(x, str(x)) for x in range(0, 13)]
CHOICE_MINUTES = [(x, str(x * 15)) for x in range(0, 4)]

CHOICE_TIME = [(x, format_minutes_to_time(x * 15)) for x in range(0, 96)]

def add_first_label(choices):
    if len(choices) > 0:
        choices.insert(0, ('', _(u'Please select')))


class DateInput(forms.TextInput):
    """Datepicker widget"""

    class Media:

        pass

        #css = {
            #'all': ('/static/datepicker/jquery-ui-1.8.6.custom.css',)
        #}
        #js = (
            #'/static/datepicker/jquery-ui-1.8.6.custom.min.js',
        #)

    def __init__(self, *args, **kwargs):
        attrs = kwargs.get('attrs', {})
        self.change_year = attrs.get('change_year', True) and 'true' or 'false'
        self.change_month = attrs.get('change_month', True) and 'true' or 'false'
        super(DateInput, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None):
        output = super(DateInput, self).render(name, value, attrs)
        output += mark_safe(DateInput().media)
        return output + mark_safe(u'''<script>
        var formatter = new goog.i18n.DateTimeFormat('MM/dd/yyyy');
        var parser = new goog.i18n.DateTimeParse('MM/dd/yyyy');
        var idp_%(name)s = new goog.ui.InputDatePicker(formatter, parser);
        idp_%(name)s.decorate(goog.dom.getElement('id_%(name)s'));
        </script>''' % {'name': name})


class BookingLocationInput(forms.TextInput):

    def render(self, name, value, attrs=None):
        output = super(BookingLocationInput, self).render(name, value, attrs)
        output += mark_safe(BookingLocationInput().media)
        return output + mark_safe(u'''<script type="text/javascript">
        var input = goog.dom.getElement("id_%(name)s");
        var ac_%(name)s = new goog.ui.AutoComplete.Remote("/json/location", input, false);
        </script>''' % {'name': name})


class IssueInput(forms.TextInput):
    """Issue search with autocompletion."""

    def render(self, name, value, attrs=None):
        output = super(IssueInput, self).render(name, value, attrs)
        output += mark_safe(IssueInput().media)
        return output + mark_safe(u'''<script type="text/javascript">
        var ac_%(name)s = new goog.ui.AutoComplete.Remote("/json/issue", goog.dom.getElement("id_%(name)s"), false);
        goog.events.listen(ac_%(name)s, goog.ui.AutoComplete.EventType.UPDATE, function(e) {
        goog.dom.forms.setValue(goog.dom.getElement("id_%(name)s"), e.row.replace(/ (\(.+?\))/gi, ''));
        });
        var focusHandler = new goog.events.FocusHandler(document.getElementById("id_%(name)s"));
        goog.events.listen(focusHandler, goog.events.FocusHandler.EventType.FOCUSIN, function(e) {
        var tracker = goog.dom.getElement("id_tracker");
        // TODO: use a URL Matcher for URL manipulation?
        ac_%(name)s.matcher_.url_ = "/json/issue?tracker=" + goog.dom.getElement("id_tracker").value;
        });
        </script>''' % {'name': name})


class IssueNumber(forms.CharField):
    """Validates issue number values.

    Possible values are e.g. '1234' or '#1234'
    """

    default_error_messages = {
        'invalid': _(u'Enter a valid issue number.'),
    }

    def to_python(self, value):
        if not isinstance(value, basestring):
            value = str(value)
        value = value.replace('#', '')
        value = value.strip()
        try:
            value = int(value)
        except (ValueError, TypeError):
            value = 0
        return value

    def validate(self, value):
        if not isinstance(value, (int, long)):
            raise ValidationError(self.error_messages['invalid'])
        return value


class LabelInput(forms.TextInput):
    """TextInput Implementation for :class:`goog.ui.LabelInuput`."""

    def __init__(self, *args, **kwargs):
        if 'label' in kwargs:
            self.label = kwargs['label']
            del kwargs['label']
        super(LabelInput, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None):
        output = super(LabelInput, self).render(name, value, attrs)
        output += mark_safe(LabelInput().media)
        return output + mark_safe(u'''<script type="text/javascript">
        var li_%(name)s = new goog.ui.LabelInput('%(text)s');
        li_%(name)s.decorate(goog.dom.getElement('id_%(name)s'));
        </script>''' % {'name': name, 'text': self.label})


class BookingForm(forms.Form):

    customer = forms.ChoiceField(
        label=_(u'Customer'), required=True,
        widget=forms.Select(
            attrs={'onchange': 'inhouse.tracking.set_projects(this.value);'}))
    project = forms.ChoiceField(
        label=_(u'Project'), required=True,
        widget=forms.Select(
            attrs={'onchange':
                   'inhouse.tracking.set_project_steps(this.value);'}))
    step = forms.ChoiceField(label=_(u'Step'), required=True)
    from_time = forms.TimeField(label=_(u'Start'), required=False,
                                widget=forms.TextInput(
                                    attrs={'size': 5, 'maxlength': 5}))
    to_time = forms.TimeField(label=_(u'End'), required=False,
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
                                  widget=forms.Textarea(attrs={
                                      'cols': 63, 'rows': 5,
                                      'class': 'resizable'}))
    location = forms.CharField(label=_(u'Location'), required=False,
                                widget=BookingLocationInput(attrs={
                                    'size': 35}))
    tracker = forms.ChoiceField(
        label=_(u'Issue tracker'), required=False, widget=forms.Select(
            attrs={'onchange': 'inhouse.tracking.on_select_tracker(this.value);'}))
    issue_no = IssueNumber(label=_(u'Issue no.'), required=False,
                           widget=IssueInput(attrs={'size': 60}))

    def __init__(self, *args, **kwds):
        self.request = kwds.pop('request')
        super(BookingForm, self).__init__(*args, **kwds)

    def clean(self):
        # TODO: Reduce complexity
        data = self.cleaned_data
        print data
        data['title'] = data.get('title', u'').strip()
        data['description'] = data.get('description', u'').strip()
        minutes = int(data['minutes']) * 15 + int(data['hours']) * 60
        # Minimum duration
        if minutes == 0:
            self._errors['minutes'] = _(u'Please select at last 15 minutes.')
            #raise forms.ValidationError(
                #_(u'Please select at last 15 minutes.'))


        from_time = data['from_time']
        to_time = data['to_time']
        if isinstance(from_time, time) and isinstance(to_time, time):
            if to_time < from_time:
                self._errors['to_time'] = _(u'The end time must be greater'
                                            u' than the start time.')
            date = data['date']
            start = datetime(date.year, date.month, date.day, from_time.hour,
                             from_time.minute)
            end = datetime(date.year, date.month, date.day, to_time.hour,
                           to_time.minute)
            delta = end - start
            if delta.seconds / 60 != minutes:
                raise forms.ValidationError(
                    _(u'The given start/end input doesn\'t match the duration.'))
            # TODO: Check for unique start/end imputs


        day = self.request.user.account.get_day(data['date'])
        #print day.get_booking_sum()

        # Issue required?
        try:
            project_id = int(data['project'])
            project = models.Project.get_by_id(project_id)
        except:
            project = None
        if project:
            tracker = data.get('tracker', None)
            issue_no = data.get('issue_no', None)
            title = data.get('title', None)
            description = data.get('description', None)
            if project.has_trackers() and (not tracker or not issue_no):
                raise forms.ValidationError(
                    _(u'Please select a tracker and issue.'))
            if not project.has_trackers() and (not title or not description):
                raise forms.ValidationError(
                    _(u'Please support a title and description.'))
        # Validate issue / tracker information
        if 'issue_no' in data and 'tracker' in data:
            tracker = None
            issue_no = data['issue_no']
            try:
                tracker = int(data['tracker'])
            except:
                pass
            if issue_no and tracker:
                issue = Issue.by_tracker_id(data['tracker'],
                                            data['issue_no'])
                if issue.id == None:
                    raise forms.ValidationError(
                        _(u'The issue %s cannot be found or is not valid.')
                        % data['issue_no'])
        return data

    def set_customer_choices(self, user):
        choices = []
        bound_field = self['customer']
        for customer in user.account.get_bookable_customers():
            choices.append((customer.id, customer.name))
        add_first_label(choices)
        bound_field.field.choices = choices

    def set_project_choices(self, user, customer=None):
        choices = []
        bound_field = self['project']
        if customer:
            for project in models.Project.objects.get_by_customer(
                customer, active_only=True, user=user).order_by('name'):
                if project.get_project_steps(active_only=True).count() > 0:
                    choices.append((project.id, project.name))
        add_first_label(choices)
        bound_field.field.choices = choices

    def set_step_choices(self, user, project=None):
        bound_field = self['step']
        choices = []
        if project:
            query = models.ProjectStep.objects.filter(project=project)
            query = query.filter(status__in=(models.STEP_STATUS_OPEN,))
            for step in query:
                choices.append((step.id, step.name))
        add_first_label(choices)
        bound_field.field.choices = choices

    def set_tracker_choices(self, user, project=None):
        choices = []
        bound_field = self['tracker']
        if project:
            query = models.ProjectTracker.objects.filter(project=project)
            for rel in query:
                choices.append((rel.tracker.id, rel.tracker.name))
        add_first_label(choices)
        bound_field.field.choices = choices


class UserProfileForm(forms.Form):

    first_name = forms.CharField(label=_(u'First name'), max_length=30,
                                 required=False)
    last_name = forms.CharField(label=_(u'Last name'), max_length=30,
                                required=False)
    email = forms.EmailField(label=_(u'E-mail'), required=True,
                             widget=forms.TextInput(attrs={'size': 40}))
    birthday = forms.DateField(label=_(u'Birthday'), required=False,
                           widget=DateInput(attrs={'size': 10,
                                                   'change_year': False}))
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
                                     max_length=40, required=False,
                                     help_text=_(u'E.g. +049/1234-56789'))
    phone_mobile = forms.CharField(label=_(u'Phone no. (mobile)'),
                                   max_length=40, required=False,
                                   help_text=_(u'E.g. +049/1234-56789'))
    fax = forms.CharField(label=_(u'Fax no.'),
                          max_length=40, required=False)
    url = forms.URLField(label=_(u'URL'), max_length=200, required=False,
                         widget=forms.TextInput(attrs={'size': 40}),
                         help_text=_(u'E.g. http://www.test.com'))
    job = forms.CharField(label=_(u'Job'), max_length=80, required=False,
                          widget=forms.TextInput(attrs={'size': 40}))
    company = forms.ChoiceField(label=_(u'Company'), required=False)
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
        add_first_label(choices)
        bound_field.field.choices = choices

    def set_company_choices(self):
        choices = []
        bound_field = self['company']
        companies = models.Company.objects.all().order_by('name')
        for company in companies:
            choices.append([company.id, company.name])
        add_first_label(choices)
        bound_field.field.choices = choices


class SearchForm(forms.Form):

    #from_date = forms.CharField(label=_(u'From'), required=False,
                                #widget=forms.DateInput())
    from_date = forms.DateField(label=_(u'From'), required=False,
                                widget=DateInput(attrs={'size': 10}))
    #to_date = forms.CharField(label=_(u'To'), required=False,
                                #widget=forms.DateInput())
    to_date = forms.DateField(label=_(u'To'), required=False,
                           widget=DateInput(attrs={'size': 10}))
    customer = forms.ChoiceField(
        label=_(u'Customer'), required=False,
        widget=forms.Select(attrs={'onchange': 'JS_setProjects(this.value);'}))
    project = forms.ChoiceField(
        label=_(u'Project'), required=False,
        widget=forms.Select(attrs={'onchange': 'JS_setProjectsteps(this.value);'}))
    step = forms.ChoiceField(label=_(u'Step'), required=False)
    tracker = forms.ChoiceField(label=_(u'Issue tracker'), required=False)
    issue_no = IssueNumber(label=_(u'Issue no.'), required=False,
                           widget=IssueInput(attrs={'size': 10}))

    def set_customer_choices(self, user):
        choices = [('', _(u'All customers'))]
        bound_field = self['customer']
        for customer in user.account.get_bookable_customers():
            choices.append((customer.id, customer.name))
        bound_field.field.choices = choices

    def set_project_choices(self, user, customer=None):
        choices = [('', _(u'All projects'))]
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

class ProjectRequestForm(forms.Form):

    project = forms.ChoiceField(label=_(u'Project'), required=True)

    def set_project_choices(self, user):
        choices = [('', _(u'No selection'))]
        bound_field = self['project']
        query = models.Project.objects.exclude(projectuser__user=user)
        query = query.distinct()
        query = query.order_by('name')
        for project in query:
            choices.append((project.id, project.name))
        bound_field.field.choices = choices

