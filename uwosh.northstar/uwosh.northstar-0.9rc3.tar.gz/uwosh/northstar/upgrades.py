from zope.component import getUtility, getMultiAdapter, queryUtility
from plone.contentrules.engine.interfaces import IRuleStorage, \
    IRuleAssignmentManager
from zope.schema.interfaces import IVocabularyFactory
from Products.CMFCore.interfaces._events import IActionSucceededEvent
from plone.app.contentrules.conditions.wftransition import \
    IWorkflowTransitionCondition, WorkflowTransitionCondition
from plone.contentrules.engine import utils
from plone.app.contentrules.rule import Rule, get_assignments
from Products.CMFCore.utils import getToolByName
from plone.contentrules.engine.assignments import RuleAssignment
from actionmanager import ActionManager
from browser.controlpanel import plone_shipped_workflows
from actions import MailerAction
from plone.app.contentrules.actions.mail import MailAction

from setupHandlers import remove_action_icons
from Products.CMFCore.utils import getToolByName
default_profile = 'profile-uwosh.northstar:default'


def upgrade_to_0_3(context):
    context.runImportStepFromProfile(default_profile, 'action-icons')
    
def upgrade_to_0_5b1(context):
    context.runImportStepFromProfile(default_profile, 'controlpanel')
    context.runImportStepFromProfile(default_profile, 'action-icons')
    
    
def upgrade_to_0_8rc1(context):
    context.runImportStepFromProfile(default_profile, 'controlpanel')
    
text_replace_mapping = {
    'object_url' : "url",
    'portal_url' : "absolute_url",
    'object_title' : "title",
    'member_fullname' : "user_fullname",
    'previous_state' : "review_state",
    'transition' : "review_title",
    'site_owner_email' : "owner_emails",
    'authenticated_user_email' : "user_email"
}
    
def mailer_text_replacements(val):
    for k, v in text_replace_mapping.items():
        val = val.replace("{{" + k + "}}", "${" + v + "}")
    return val
    
def upgrade_to_0_9b1(context):
    site = getToolByName(context, 'portal_url').getPortalObject()
    remove_action_icons(context)
    context.runImportStepFromProfile(default_profile, 'controlpanel')
    
    # go through each workflow and transition converting mail action scripts
    # to content rule actions
    
    pw = getToolByName(context, 'portal_workflow')
    ids = pw.portal_workflow.listWorkflows()
    workflows = [pw[id] for id in sorted(ids)]
    
    for workflow in [w for w in workflows if w.id not in plone_shipped_workflows]:
        for transition in [workflow.transitions[t] for t in workflow.transitions.objectIds()]:
            if transition.after_script_name in workflow.scripts.objectIds() and \
                transition.after_script_name == 'transition-%s-mailer-action' % transition.id:
                try:
                    mailer = MailerAction(workflow.scripts[transition.after_script_name])
                except:
                    # skip if it can't parse the script.
                    continue
                    
                am = ActionManager()
                rule = am.create(transition).rule
                
                action = MailAction()
                action.subject = mailer_text_replacements(mailer.subject)
                action.source = mailer_text_replacements(mailer.from_)
                action.recipients = mailer_text_replacements(mailer.to_)
                action.message = mailer_text_replacements(mailer.body)
                
                rule.actions.append(action)
                
                workflow.scripts.manage_delObjects([transition.after_script_name])
                