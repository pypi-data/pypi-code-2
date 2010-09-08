from zope.i18nmessageid import MessageFactory

from AccessControl import allow_module, ModuleSecurityInfo
from Products.CMFCore.utils import ToolInit

from quintagroup.captcha.core import config
from quintagroup.captcha.core import CaptchaTool

ProductMessageFactory = MessageFactory('quintagroup.captcha.core')
ModuleSecurityInfo('quintagroup.captcha.core').declarePublic("ProductMessageFactory")

allow_module('quintagroup.captcha.core.utils')
allow_module('quintagroup.captcha.core.config')

def initialize(context):
    ToolInit(meta_type="CaptchaTool",
             tools=(CaptchaTool.CaptchaTool, ),
             icon=config.TOOL_ICON,).initialize(context)
