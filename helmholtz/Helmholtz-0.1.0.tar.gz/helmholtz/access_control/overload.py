#encoding:utf-8
from helmholtz.access_control.dependencies import get_dependencies, get_all_dependencies
from helmholtz.access_control.conditions import is_under_access_control, is_deletable_by
from helmholtz.access_control.lifecycle import remove_all_permissions

def delete_selection(obj, selection, fields=None, starting_point=True):
    """Realize the secure_delete function."""
    if starting_point :
        if not fields :
            fields = get_dependencies(obj.__class__)
    #go recursively into the object hierarchy in order to remove links 
    #if objects are not in selection and avoiding cascaded deletion implied by foreign keys
    for field in fields :
        relation_type = getattr(obj.__class__, field)
        if (relation_type.__class__.__name__ != 'SingleRelatedObjectDescriptor') :
            attr = getattr(obj, field)
            if attr.__class__.__name__ in ['RelatedManager', 'ManyRelatedManager', 'GenericRelatedObjectManager'] :
                new_fields = get_dependencies(attr.model)
                objects = attr.all() 
                for sub_obj in objects : 
                    #unlink sub objects if they are not selected
                    object_field = getattr(sub_obj.__class__, fields[field]['field'])
                    if attr.__class__.__name__ != 'GenericRelatedObjectManager' :
                        not_required = object_field.field.null
                    else :
                        not_required = False
                    if not (sub_obj in selection) and not_required : 
                        if fields[field]['type'] != 'reverse_m2m' :
                            attr.clear()
                            setattr(sub_obj, fields[field]['field'], None)
                        else :
                            m2m = getattr(sub_obj, fields[field]['field'])
                            m2m.remove(obj)
                    if new_fields :
                        delete_selection(sub_obj, selection, new_fields, False)          
            else :
                if not (attr in selection) : 
                    setattr(obj, field, None)
                new_fields = get_dependencies(attr.__class__)
                if new_fields :
                    delete_selection(attr, selection, new_fields, False) 
        else :
            try :
                attr = getattr(obj, field)
                if not (attr in selection) :
                    setattr(attr, fields[field]['field'], None)
                new_fields = get_dependencies(attr.related.model)
                if new_fields :
                    delete_selection(attr, selection, new_fields, False) 
            except :
                pass  
    #finally remove objects stored in selection 
    if starting_point :
        for selected in selection :
            if is_under_access_control(obj.__class__) :
                remove_all_permissions(selected)
            selected.delete()       
   
def secure_delete(obj, user, selection=None, filter=False):
    """
    Delete an object and all depending objects recursively only if the specified user 
    has the 'can_delete' permission on these objects. Else objects are not deleted but link 
    to their parents will be broken.
    """
    if is_deletable_by(obj, user) :
        fields = get_dependencies(obj.__class__)
        if selection is None :
            deletable = [k[1] for k in get_all_dependencies(obj, fields, user)]
        else :
            if selection :
                #see if all objects of the selection are deletable by the user
                deletable = [k for k in selection if is_deletable_by(k, user)]
                #filter is here to trigger an exception if needed
                if not filter and (len(deletable) != len(selection)) :
                    not_deletable = [k for k in selection if not k in deletable]
                    raise Exception("Delete permission required on objects %s" % (not_deletable)) 
            else :
                deletable = list()
        delete_selection(obj, deletable, fields=fields)    
        if is_under_access_control(obj.__class__) :
            remove_all_permissions(obj)
        obj.delete()
    else :
        raise Exception("Delete permission required on %s." % (obj))
