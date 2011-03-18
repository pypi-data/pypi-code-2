# -*- coding: utf-8 -*-

from django import forms
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _

from issues.models import Issue, Tracker
from forms import DateInput, IssueInput, IssueNumber
import models


CHOICE_HOURS = [(x, str(x)) for x in range(0, 13)]
CHOICE_HOURS.insert(0, ('', u'---'))
CHOICE_MINUTES = [(x, str(x * 15)) for x in range(0, 4)]
CHOICE_MINUTES.insert(0, ('', u'---'))


class CopyProjectForm(forms.Form):

    name = forms.CharField(label=_(u'Name'), required=False,
                           widget=forms.TextInput(attrs={'size': 80}))
    steps = forms.BooleanField(label=_(u'Steps'), required=False,
                               help_text=_(u'Adopt the project\'s steps in'
                                           u' their current order.'))
    members = forms.BooleanField(label=_(u'Members'), required=False,
                                 help_text=_(u'Copies all project members.'))
    tracker = forms.BooleanField(label=_(u'Tracker'), required=False,
                                 help_text=_(u'Copies all issue tracker'
                                             u' assignments.'))


def copy_project(request, project_id):
    """Create a new project by adopting other project's members.

    :params project_id: Id of the project to be copied
    """
    project = models.Project.get_by_id(project_id)
    form = CopyProjectForm(initial={'name': u'%s \'%s\'' % (_(u'Copy of'),
                                                            project.name)})
    steps = project.get_project_steps(False)
    members = project.get_members()
    trackers = project.get_trackers()
    if request.method == 'POST':
        if '_cancel' in request.POST:
            return HttpResponseRedirect(reverse('admin:inhouse_project_change',
                                                args=(project.id,)))
        with_steps = bool(request.POST.get('steps'))
        with_members = bool(request.POST.get('members'))
        with_trackers = bool(request.POST.get('tracker'))
        name = request.POST.get('name')
        p = models.Project.copy(project, name=name)
        p.save(user=request.user)
        p.master = p
        p.save(user=request.user)
        if with_steps:
            steps = models.ProjectStep.objects.filter(project=project)
            for step in steps:
                new = models.ProjectStep.copy(step)
                new.project = p
                new.next_position()
                new.save(user=request.user)
        if with_members:
            members = models.ProjectUser.objects.filter(project=project)
            for project_user in members:
                new = models.ProjectUser()
                new.project = p
                new.user = project_user.user
                if project_user.default_step:
                    # Retrieve the user's default step, if possible
                    query = models.ProjectStep.objects.get_by_name(
                        p, project_user.default_step.name)
                    if query.count() == 1:
                        new.default_step = query[0]
                    else:
                        new.default_step = None
                new.save(user=request.user)
        if with_trackers:
            project_trackers = models.ProjectTracker.objects.filter(
                project=project)
            for project_tracker in project_trackers:
                new = models.ProjectTracker()
                new.project = p
                new.tracker = project_tracker.tracker
                new.save(user=request.user)
        messages.success(request, _(u'The project has been'
                                    u' successfully copied.'))
        return HttpResponseRedirect(reverse(
            'admin:inhouse_project_changelist'))
    return render_to_response(
        'admin/inhouse/project/copy_project.html', {
            'form': form, 'project': project, 'steps': steps,
            'members': members, 'trackers': trackers},
        RequestContext(request, {}),)


class DefaultStepForm(forms.Form):

    steps = forms.MultipleChoiceField(label=_(u'Steps'))

    def set_step_choices(self):
        bound_field = self['steps']
        steps = models.ProjectStepTemplate.objects.all().order_by('name')
        choices = [(step.id, step.name) for step in steps]
        bound_field.field.choices = choices


def default_steps(request, project_id):
    """Assign default project steps to a project.

    :params project_id: Id of the project to be edited
    """
    project = models.Project.get_by_id(project_id)
    form = DefaultStepForm()
    form.set_step_choices()
    if request.method == 'POST':
        if '_cancel' in request.POST:
            return HttpResponseRedirect(reverse('admin:inhouse_project_change',
                                                args=(project.id,)))
        #if form.is_valid():
        ids = request.POST.getlist('steps')
        if len(ids) == 0:
            messages.warning(request, _(u'No steps have been selected.'))
        else:
            tpls = models.ProjectStepTemplate.objects.filter(id__in=ids)
            for tpl in tpls:
                query = models.ProjectStep.objects.filter(project=project,
                                                          name=tpl.name)
                if query.count() != 0:
                    continue
                new = models.ProjectStep.copy(tpl)
                new.project = project
                new.next_position()
                new.save(user=request.user)
            messages.success(request, _(u'The project steps have been'
                                        u' successfully added.'))
            return HttpResponseRedirect(reverse(
                'admin:inhouse_project_changelist'))
    return render_to_response(
        'admin/inhouse/project/default_steps.html', {
            'form': form, 'project': project},
        RequestContext(request, {}),)


class BookingsForm(forms.Form):
    """Form class for booking mass editing."""

    project = forms.ChoiceField(label=_(u'Project'), required=False,
        widget=forms.Select(attrs={'onchange':
            'inhouse.admin.set_project_steps(this.value);'}))
    step = forms.ChoiceField(label=_(u'Step'), required=False)
    date = forms.DateField(label=_(u'Date'), required=False,
                           widget=DateInput(attrs={'size': 10}))
    user = forms.ChoiceField(label=_(u'User'), required=False)
    hours = forms.ChoiceField(choices=CHOICE_HOURS, label=_(u'Hours'),
                              required=False)
    minutes = forms.ChoiceField(choices=CHOICE_MINUTES, required=False,
                                label=_(u'Minutes'))
    title = forms.CharField(label=_(u'Title'), required=False,
        widget=forms.TextInput(attrs={'size': 60}))
    description = forms.CharField(label=_(u'Description'), required=False,
        widget=forms.Textarea(attrs={'cols': 63, 'rows': 5,
                                    'class': 'resizable'}))
    tracker = forms.ChoiceField(
        label=_(u'Issue tracker'), required=False, widget=forms.Select(
            attrs={'onchange': 'inhouse.tracking.on_select_tracker(this.value);'}))
    issue_no = IssueNumber(label=_(u'Issue no.'), required=False,
                           widget=IssueInput(attrs={'size': 60}))
    clear_issue = forms.BooleanField(label=_(u'Clear issue information?'),
                                     required=False)

    def set_project_choices(self):
        bound_field = self['project']
        choices = [('', _(u'No selection'))]
        query = models.Project.objects.all().order_by('name')
        for project in query:
            choices.append((project.id, project.name))
        bound_field.field.choices = choices

    def set_tracker_choices(self):
        bound_field = self['tracker']
        choices = [('', _(u'No selection'))]
        query = Tracker.objects.all()
        for tracker in query:
            choices.append((tracker.id, tracker.name))
        bound_field.field.choices = choices

    def set_user_choices(self):
        bound_field = self['user']
        choices = [('', _(u'No selection'))]
        # TODO: Filter by department?
        query = User.objects.all()
        for user in query:
            choices.append((user.id, user.username))
        bound_field.field.choices = choices


def edit_bookings(request):
    """Edit one or more bookings."""
    form = BookingsForm()
    form.set_project_choices()
    form.set_tracker_choices()
    form.set_user_choices()
    bookings = models.Booking.objects.filter(id__in=request.GET.getlist('id'))
    if request.method == 'POST':
        if 'cancel' in request.POST:
            return HttpResponseRedirect(reverse(
                    'admin:inhouse_booking_changelist'))
        form = BookingsForm(request.POST)
        form.set_project_choices()
        form.set_tracker_choices()
        form.set_user_choices()
        print request.POST
        print form.is_valid()
        print form.errors
        if form.is_valid():
            data = form.cleaned_data
            clear_issue = data.get('clear_issues', None)
            title = data.get('title')
            description = data.get('description')
            tracker = data.get('tracker')
            issue_no = data.get('issue_no')
            try:
                minutes = int(data.get('minutes'))
            except (ValueError, TypeError):
                minutes = 0
            try:
                hours = int(data.get('hours'))
            except (ValueError, TypeError):
                hours = 0
            try:
                tracker = int(data.get('tracker'))
            except:
                tracker = None
            date = data.get('date')
            user = data.get('user')
            if user:
                user = User.objects.filter(id=user)[0]
            for booking in bookings:
                creator = booking.day.user
                duration = 0
                if clear_issue:
                    booking.issue = None
                if title:
                    booking.title = title
                if description:
                    booking.description = description
                if minutes:
                    duration += minutes * 15
                if hours:
                    duration += hours * 60
                if duration > 0:
                    booking.duration = duration
                if user != creator:
                    creator = user
                if not date:
                    date = booking.day.date
                if date:
                    account = models.Account.get_account_for_user(creator)
                    day = account.get_day(date)
                    booking.day = day
                if issue_no and tracker:
                    issue = Issue.by_tracker_id(tracker, issue_no)
                    if issue.id != None:
                        booking.set_issue(tracker, issue_no)
                booking.save(user=request.user)
            messages.success(request, _(u'%d bookings have been successfully'
                u' updated.' % bookings.count()))
            return HttpResponseRedirect(reverse(
                    'admin:inhouse_booking_changelist'))
    return render_to_response(
        'admin/inhouse/booking/mass_edit.html', {
            'form': form, 'bookings': bookings},
        RequestContext(request, {}),)


copy_project = staff_member_required(copy_project)
default_steps = staff_member_required(default_steps)
edit_bookings = staff_member_required(edit_bookings)
