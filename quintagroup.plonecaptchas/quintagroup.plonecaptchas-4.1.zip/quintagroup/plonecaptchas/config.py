GLOBALS = globals()
PRODUCT_NAME = 'quintagroup.plonecaptchas'
CAPTCHA_NAME = 'plonecaptchas'

HAS_APP_DISCUSSION = True
try:
    import plone.app.discussion
except ImportError:
    HAS_APP_DISCUSSION = False

#TOOL_ICON = 'tool.gif'
