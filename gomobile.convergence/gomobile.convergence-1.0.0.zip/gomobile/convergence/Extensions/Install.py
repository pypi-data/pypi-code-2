"""


    Old-fashioned uninstall script.
    
"""


from StringIO import StringIO

from Products.CMFCore.utils import getToolByName

from gomobile.mobile.setuphandlers import clean_up_content_annotations

def uninstall(portal, reinstall=False):

    output = StringIO()
    if not reinstall:

        try:
            report = clean_up_content_annotations(portal, ["multichannel"])
        except Exception, e:
            print >> str(e), output
        
        print >> output, report
        
        print >> output, "Ran all uninstall steps."
        
        return output.getvalue()
