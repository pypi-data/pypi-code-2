from __future__ import absolute_import

import re

from django.conf import settings
from django.contrib.localflavor.us.forms import (
    USPhoneNumberField,
    USStateField,
    USZipCodeField)
from django.forms import (
    BooleanField,
    CharField,
    CheckboxSelectMultiple,
    ChoiceField,
    EmailField,
    FloatField,
    Form,
    FileField,
    IntegerField,
    MultipleChoiceField,
    RadioSelect,
    Select,
    Textarea,
    ValidationError,
    )
from django.forms.forms import BoundField

from .models import OPTION_TYPE_CHOICES


class BaseAnswerForm(Form):

    def __init__(self,
                 question,
                 entry=None,
                 *args,
                 **kwargs):
        self.question = question
        self.entry = entry
        super(BaseAnswerForm, self).__init__(*args, **kwargs)
        self._configure_answer_field()

    def as_template(self):
        """Helper function for fieldsting fields data from form."""
        bound_fields = [BoundField(self, field, name) \
                      for name, field in self.fields.items()]
        c = Context(dict(form=self, bound_fields=bound_fields))
        t = loader.get_template('emailform/form.html')
        return t.render(c)

    def _configure_answer_field(self):
        answer = self.fields['answer']
        q = self.question
        answer.required = q.required
        answer.label = q.question
        answer.help_text = q.help_text
        return answer


class USPhoneNumberAnswer(BaseAnswerForm):
    answer = USPhoneNumberField()


class USStateAnswer(BaseAnswerForm):
    answer = USStateField()


class USZipCodeAnswer(BaseAnswerForm):
    answer = USZipCodeField()


class TextInputAnswer(BaseAnswerForm):
    answer = CharField()


class IntegerInputAnswer(BaseAnswerForm):
    answer = IntegerField()


class FloatInputAnswer(BaseAnswerForm):
    answer = FloatField()


class BooleanInputAnswer(BaseAnswerForm):
    answer = BooleanField(initial=False)

    def clean_answer(self):
        value = self.cleaned_data['answer']
        if not value:
            return False
        return value


class TextAreaAnswer(BaseAnswerForm):
    answer = CharField(widget=Textarea)


class EmailAnswer(BaseAnswerForm):
    answer = EmailField()


class FileUpload(BaseAnswerForm):
    answer = FileField()


class BaseOptionAnswer(BaseAnswerForm):

    def __init__(self, *args, **kwargs):
        super(BaseOptionAnswer, self).__init__(*args, **kwargs)
        choices = [(x, x) for x in self.question.parsed_options]
        if not self.question.required and not isinstance(self, OptionCheckbox):
            choices = [('', '---------',)] + choices
        self.fields['answer'].choices = choices

    def clean_answer(self):
        key = self.cleaned_data['answer']
        if not key and self.fields['answer'].required:
            raise ValidationError, _('This field is required.')
        if not isinstance(key, (list, tuple)):
            key = (key,)
        return key


class OptionAnswer(BaseOptionAnswer):
    answer = ChoiceField()


class OptionRadio(BaseOptionAnswer):
    answer = ChoiceField(widget=RadioSelect)


class OptionCheckbox(BaseOptionAnswer):
    answer = MultipleChoiceField(widget=CheckboxSelectMultiple)


## each question gets a form with one element, determined by the type
## for the answer.
QTYPE_FORM = {
    OPTION_TYPE_CHOICES.TEXT_FIELD:        TextInputAnswer,
    OPTION_TYPE_CHOICES.INTEGER:           IntegerInputAnswer,
    OPTION_TYPE_CHOICES.FLOAT:             FloatInputAnswer,
    OPTION_TYPE_CHOICES.BOOLEAN:           BooleanInputAnswer,
    OPTION_TYPE_CHOICES.TEXT_AREA:         TextAreaAnswer,
    OPTION_TYPE_CHOICES.SELECT_ONE_CHOICE: OptionAnswer,
    OPTION_TYPE_CHOICES.RADIO_LIST:        OptionRadio,
    OPTION_TYPE_CHOICES.CHECKBOX_LIST:     OptionCheckbox,
    OPTION_TYPE_CHOICES.EMAIL_FIELD:       EmailAnswer,
    OPTION_TYPE_CHOICES.FILE_UPLOAD:       FileUpload,
    OPTION_TYPE_CHOICES.PHONE_NUMBER:      USPhoneNumberAnswer,
    OPTION_TYPE_CHOICES.US_STATE:          USStateAnswer,
    OPTION_TYPE_CHOICES.ZIPCODE:           USZipCodeAnswer}


def forms_for_emailform(emailform, request='testing', entry=None):
    testing = 'testing' == request
    post = None if testing else request.POST or None
    files = None if testing else request.FILES or None
    return [_form_for_question(q, entry, post, files)
        for q in emailform.questions.all().order_by("order")]


def _form_for_question(question,
                       entry=None,
                       data=None,
                       files=None):
    return QTYPE_FORM[question.option_type](
        question=question,
        entry=entry,
        prefix='%s_%s' % (question.emailform.id,
                        question.id),
        data=data,
        files=files)
