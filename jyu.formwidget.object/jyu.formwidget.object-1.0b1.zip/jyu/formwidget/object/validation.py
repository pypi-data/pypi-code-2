# -*- coding: utf-8 -*-
"""Adds subform support for Dexterity"""

from Acquisition import aq_inner

from zope.interface import alsoProvides

from zope.i18n import translate
from zope.i18nmessageid import Message

from kss.core import kssaction

from z3c.form.interfaces import IFormLayer
from z3c.form.error import MultipleErrorViewSnippet

from plone.z3cform.interfaces import IFormWrapper
from plone.z3cform import z2

from plone.app.kss.plonekssview import PloneKSSView


def validate_and_issue_message(ksscore, error, fieldname, fieldset,
                               kssplone=None):
    """A helper method also used by the inline editing view
    """
    if fieldset is not None:
        fieldId = '#fieldset-%s #formfield-%s' % (str(fieldset),
                                                  fieldname.replace('.', '-'))
        errorId = '#fieldset-%s #formfield-%s > div.fieldErrorBox' % \
                                                 (str(fieldset),
                                                  fieldname.replace('.', '-'))
    else:
        fieldId = '#formfield-%s' % fieldname.replace('.', '-')
        errorId = '#formfield-%s > div.fieldErrorBox' % fieldname.replace('.',
                                                                        '-')
    field_div = ksscore.getCssSelector(fieldId)
    error_box = ksscore.getCssSelector(errorId)

    if error:
        ksscore.replaceInnerHTML(error_box, error)
        ksscore.addClass(field_div, 'error')
    else:
        ksscore.clearChildNodes(error_box)
        ksscore.removeClass(field_div, 'error')
        if kssplone is not None:
            kssplone.issuePortalMessage('')

    return bool(error)


class Z3CFormValidation(PloneKSSView):
    """KSS actions for z3c form inline validation
    """

    @kssaction
    def validate_input(self, formname, fieldname, fieldset=None, value=None):
        """Given a form (view) name, a field name and the submitted
        value, validate the given field.
        """

        # Abort if there was no value changed. Note that the actual value
        # comes along the submitted form, since a widget may require more than
        # a single form field to validate properly.
        if value is None:
            return

        context = aq_inner(self.context)
        request = aq_inner(self.request)
        alsoProvides(request, IFormLayer)

        # Find the form, the field and the widget

        form = request.traverseName(context, formname)
        if IFormWrapper.providedBy(form):
            formWrapper = form
            form = form.form_instance
            if not z2.IFixedUpRequest.providedBy(request):
                z2.switch_on(form, request_layer=formWrapper.request_layer)

        form.update()
        data, errors = form.extractData()

        #if we validate a field in a group we operate on the group
        if fieldset is not None:
            fieldset = int(fieldset)
            form = form.groups[fieldset]

        prefix = form.prefix + form.widgets.prefix
        raw_fieldnames = [fieldname[len(prefix):]]
        while raw_fieldnames[-1].rfind(".widgets.") > -1:
            raw_fieldnames.append(raw_fieldnames[-1][\
                    :raw_fieldnames[-1].rfind(".widgets.")])
        raw_fieldnames.reverse()

        # Resolve all widgets from form and its subforms
        widgets = {}

        def resolve(form, widgets, prefix=u""):
            for key in form.widgets:
                obj = form.widgets.get(key)
                widgets[prefix + key] = obj
                if hasattr(obj, "subform"):
                    resolve(getattr(obj, "subform"), widgets,
                            prefix + key + u".widgets.")
        resolve(form, widgets)

        errors_extended = []
        for error in errors:
            if isinstance(error, MultipleErrorViewSnippet):
                default_widget = error.widget
                for e in [e for e in error.error.errors
                          if e.widget is None]:
                    e.widget = default_widget
                errors_extended.extend(error.error.errors)
            else:
                errors_extended.append(error)

        errors_paired = {}
        for widget in widgets:
            for error in errors_extended:
                if error.widget == widgets[widget]:
                    errors_paired[widget] = error

        # Attempt to convert the value - this will trigge validation
        ksscore = self.getCommandSet('core')
        kssplone = self.getCommandSet('plone')

        for raw_fieldname in raw_fieldnames:
            validationError = None

            if raw_fieldname in errors_paired:
                validationError = errors_paired[raw_fieldname].message

            if isinstance(validationError, Message):
                validationError = translate(
                    validationError, context=self.request)

            if validationError is None and\
                    [e for e in errors_paired if e.startswith(raw_fieldname)]:
                continue

            validate_and_issue_message(ksscore, validationError,
                                       prefix + raw_fieldname, fieldset,
                                       kssplone)
