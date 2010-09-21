# -*- coding: utf-8 -*-

from django import forms
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _

import models


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
                ps = models.ProjectStep()
                ps.name = tpl.name
                ps.description = tpl.description
                ps.project = project
                ps.status = models.ProjectStepStatus.get_by_id(
                    models.STEP_STATUS_OPEN)
                ps.next_position()
                ps.save(user=request.user)
            messages.success(request, _(u'The project steps have beend'
                                        u' successfully added.'))
            return HttpResponseRedirect(reverse(
                'admin:inhouse_project_changelist'))
    return render_to_response(
        'admin/inhouse/project/default_steps.html', {
            'form': form, 'project': project},
        RequestContext(request, {}),)

default_steps = staff_member_required(default_steps)