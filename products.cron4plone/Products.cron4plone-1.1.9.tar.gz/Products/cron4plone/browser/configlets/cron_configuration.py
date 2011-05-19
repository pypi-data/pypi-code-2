from zope import schema
from zope.schema import ValidationError
from zope.interface import Interface
from zope.formlib import form
#from zope.app.form import CustomWidgetFactory
from zope.i18nmessageid import MessageFactory
from plone.app.controlpanel.form import ControlPanelForm
from DateTime import DateTime
#from Products.Five.formlib import formbase

from Products.cron4plone.tools.crontab_utils import splitJob, getNextScheduledExecutionTime

_ = MessageFactory('Products.cron4plone')


def checkJob(jobs):
    for id, job in enumerate(jobs):
        try:
            data = splitJob(job)
            getNextScheduledExecutionTime(data['schedule'], DateTime('UTC'))
        except:
            raise JobInvalid # can we be a bit more verbose, say which job is invalid

    return True


class JobInvalid(ValidationError):
    """One or more jobs are invalid."""


class ICronConfiguration(Interface):
    """ This interface defines the configlet """

    cronjobs = schema.List(title=_(u"Cron jobs"),
                           description=_(u"List your cron jobs here. Syntax: m h dom mon command."),
                           value_type=schema.TextLine(),
                           default=[],
                           constraint=checkJob,
                           required=False)


class CronConfigurationForm(ControlPanelForm):

    form_fields = form.Fields(ICronConfiguration)

    label = _(u"cron4plone configuration form")
    description = _(u"Add cron jobs here. Syntax is came as cron except day of month is missing.")
    form_name = _(u"cron4plone settings")
