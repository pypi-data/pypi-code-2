def initialize(context):
    from pfg.drafts.tool import PFGDraftStorage
    from Products.CMFCore.permissions import ManagePortal
    
    context.registerClass(
        PFGDraftStorage,
        permission = ManagePortal,
        constructors = (PFGDraftStorage,),
        )
