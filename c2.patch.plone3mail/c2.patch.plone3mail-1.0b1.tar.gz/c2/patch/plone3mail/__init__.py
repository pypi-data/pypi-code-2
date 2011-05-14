
try:
    from Products.CMFPlone.RegistrationTool import get_member_by_login_name
    HAS_PLONE4 = True
except ImportError:
    HAS_PLONE4 = False

import HotfixRegistrationTool

if HAS_PLONE4:
    import HotfixPasswordResetTool
else:
    import HotfixSecureMailHost
