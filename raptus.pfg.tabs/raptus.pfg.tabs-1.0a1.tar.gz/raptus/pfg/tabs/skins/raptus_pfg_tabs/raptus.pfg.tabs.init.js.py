## Script (Python) "raptus.pfg.tabs.js.py"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=foo=None,bar=None
##title=
##

from Products.CMFCore.utils import getToolByName
tool = getToolByName(context, 'translation_service')

return """
  (function($) {
    
    $(document).ready(function() {
      
      var settings = {
        nextLabel: "%(next)s",
        prevLabel: "%(prev)s",
        infoLabel: "%(info)s"
      };
      $('.pfg-form form').pfgTabs(settings);
      
    });
    
  })(jQuery);""" % {
    'next': tool.translate('continue', 'raptus.pfg.tabs', context=context),
    'prev': tool.translate('back', 'raptus.pfg.tabs', context=context),
    'info': tool.translate('step {current} of {total}', 'raptus.pfg.tabs', context=context)
  }
