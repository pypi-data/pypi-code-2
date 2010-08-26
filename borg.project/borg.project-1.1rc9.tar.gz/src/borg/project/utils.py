from Products.CMFCore.utils import getToolByName

def default_addable_types(context):
    """Return all globally allowed types where the factory permission
    is given to the Owner role.
    """
    portal_types = getToolByName(context, 'portal_types')
    
    dispatcher = getattr(context, 'manage_addProduct', None)
    types = set()

    for fti in portal_types.listTypeInfo():
        if getattr(fti, 'globalAllow', lambda: False)() == True:            
            role_permission = _get_role_permission_for_fti(context, fti)
            if role_permission is not None:
                if 'Owner' in role_permission.__of__(context):
                    types.add(fti.getId())
    
    return types

        
def get_factory_permission(context, fti):
    """Return the factory perimssion of the given type information object.
    """
    role_permission = _get_role_permission_for_fti(context, fti)
    if role_permission is None:
        return None
    return role_permission.__name__

def _get_role_permission_for_fti(context, fti):
    """Helper method to get hold of a RolePermission for a given FTI.
    """
    factory = getattr(fti, 'factory', None)
    product = getattr(fti, 'product', None)
    dispatcher = getattr(context, 'manage_addProduct', None)

    if factory is None or product is None or dispatcher is None:
        return None

    try:
        product_instance = dispatcher[product]
    except AttributeError:
        return None

    factory_method = getattr(product_instance, factory, None)
    if factory_method is None:
        return None

    factory_instance = getattr(factory_method, 'im_self', None)
    if factory_instance is None:
        return None

    factory_class = factory_instance.__class__
    role_permission = getattr(factory_class, factory+'__roles__', None)
    if role_permission is None:
        return None

    return role_permission
