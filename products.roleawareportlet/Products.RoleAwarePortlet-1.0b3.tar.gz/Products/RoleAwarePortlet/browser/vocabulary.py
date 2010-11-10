from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.component import getSiteManager

def roles(context):
    if context is None:
        context = getSiteManager()
    roles = context.acl_users.portal_role_manager.listRoleIds()
    return SimpleVocabulary([SimpleTerm(r, r, r.decode('UTF-8')) for r in roles])