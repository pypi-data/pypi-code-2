from Products.CMFCore.utils import getToolByName
from uwosh.northstar.utils import generate_id
from OFS.ObjectManager import checkValidId
import re
from Products.validation.validators.BaseValidators import EMAIL_RE
email_validator_re = re.compile(r'^' + EMAIL_RE)
comma_seperated_email_validator_re = re.compile(r'^' + EMAIL_RE[:-1] + '(,\s*' + EMAIL_RE[:-1] + ')*$')

def not_empty(form, name):
    v = form.request.get(name, '').strip()
    if v is None or (type(v) in (str, unicode) and \
     len(v) == 0) or (type(v) in (tuple, set, list) and len(v) == 0):
        form.errors[name] = 'This field is required.'

    return v

def id(form, name, container):
    id = form.request.get(name, '').strip()
    putils = getToolByName(form.context, 'plone_utils')
    id = generate_id(putils.normalizeString(id), container.objectIds())
    try:
        checkValidId(container, id)
    except:
        form.errors[name] = 'Invalid workflow name. Please try another.'
        
    return id

def comma_seperated_email(form, name, required=False):
    v = form.request.get(name)
    if v and len(v) > 0:
        v = v.replace(' ', '')
        membership = getToolByName(form.context, 'portal_membership')
        for email in v.split(','):
            if email in ('{{authenticated_user_email}}', '{{site_owner_email}}'):
                authenticate_replacement_emails(form, name, v)
            elif not email_validator_re.match(email):
                user = membership.getMemberById(email)
                if not user or not user.getProperty('email', False):
                    form.errors[name] = 'The email address "%s" is not a valid email or username.' % email
    else:
        if required:
            form.errors[name] = 'You must enter an email address.'

    return v
    
def authenticate_replacement_emails(form, name, v):
    if v == '{{authenticated_user_email}}':
        pm = getToolByName(form.context, 'portal_membership')
        member = pm.getAuthenticatedMember()
        email = member.getProperty('email')
        
        if not email or len(email) == 0:
            form.errors[name] = "Authenticated user has no email specified."
        
    elif v == '{{site_owner_email}}':
        portal = getToolByName(form.context, 'portal_url').getPortalObject()
        email = portal.email_from_address
        
        if not email or len(email) == 0:
            form.errors[name] = "The site has no email from address setup."
        
    else:
        form.errors[name] = "You specified an incorrect subsitution value here."

def email(form, name, required=False):
    v = form.request.get(name)
    
    # if it's using a check boxed widget, 
    # only take the checkbox value it's its checked
    checked_v = form.request.get(name + '-checkbox', None)
    if checked_v:
        v = checked_v
    
    if v and len(v) > 0:
        v = v.strip().replace(' ', '')
        if v in ('{{authenticated_user_email}}', '{{site_owner_email}}'):
            authenticate_replacement_emails(form, name, v)
        elif not email_validator_re.match(v):
            membership = getToolByName(form.context, 'portal_membership')
            user = membership.getMemberById(v)
            if not user or not user.getProperty('email', False):
                form.errors[name] = \
                    'The email address or username "%s" is not valid.' % v
    else:
        if required:
            form.errors[name] = 'You must enter an email address.'

    return v

def parse_set_value(form, key):
    val = form.request.get(key)
    if val:
        if type(val) in (str, unicode):
            return set(val.split(','))
        elif type(val) in (tuple, list):
            return set(val)
    else:
        return set(())
    return val
    