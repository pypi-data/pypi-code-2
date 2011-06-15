# -*- coding:utf-8 -*-

from Products.CMFPlone.interfaces import IPloneSiteRoot
#import transaction

def updatePaths(ob, event):
    """ set parent path to empty reference fields """
    if event.newParent == event.object.getFolderWhenPortalFactory():
        if IPloneSiteRoot.providedBy(event.newParent):
            uid = ob.UID()
        else:
            uid = event.newParent.UID()
        
        # Here we set the actual paths for our content. We check if each of our lists already have existing
        # path. If they are empty we set the path to be our parent object.
        if not ob.getFirst_list_path():
            ob.setFirst_list_path(uid)
            
        if not ob.getSecond_list_path():
            ob.setSecond_list_path(uid)
    
        if not ob.getThird_list_path():
            ob.setThird_list_path(uid)
            
        if not ob.getFourth_list_path():
            ob.setFourth_list_path(uid)
        
#    transaction.savepoint()
