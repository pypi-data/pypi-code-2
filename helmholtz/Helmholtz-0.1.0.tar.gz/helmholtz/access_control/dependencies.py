#encoding:utf-8
from django.utils.datastructures import SortedDict
from helmholtz.core.shortcuts import cast_object_to_leaf_class
from helmholtz.core.schema import generic_relations, reverse_foreign_keys, reverse_one_to_one_keys, reverse_many_to_many_fields
from helmholtz.access_control.conditions import is_under_access_control
from helmholtz.access_control.filters import get_deletable_by

def get_dependencies(cls):
    """docstring needed"""
    dct = SortedDict()
    rfks = reverse_foreign_keys(cls)
    ro2o = reverse_one_to_one_keys(cls)
    rm2m = reverse_many_to_many_fields(cls)
    grel = generic_relations(cls)
    dct.update(rfks)
    dct.update(ro2o)
    dct.update(rm2m)
    dct.update(grel)
    return dct  

def get_all_dependencies(main_object, fields, user, m2m=True, all_dependencies=None, level=0, starting_point=True, recursive=True):
    """Get all objects which life cycle is depending on the specified object."""
    if starting_point :
        all_dependencies = list() 
    for field in fields :
        if (fields[field]['type'] != 'reverse_o2o'):
            if (fields[field]['type'] != 'reverse_m2m') or m2m or (fields[field]['type'] == 'generic_rel') :
                link = getattr(cast_object_to_leaf_class(main_object), field)
                lst = link.all()
                if is_under_access_control(link.model) :
                    lst = get_deletable_by(lst, user)
                lst = list(lst)
            else :
                return
        else :
            try :
                link = getattr(cast_object_to_leaf_class(main_object), field)
                lst = [link]
            except :
                return    
        objects = [(k.__class__.__name__, k, fields[field]['is_required'] if (fields[field]['type'] != 'generic_rel') else True, 20 * level) for k in lst] 
        if not recursive :
            all_dependencies.extend(objects)
        else :
            for item in objects :
                all_dependencies.append(item)
                child_object = item[1]
                cls = child_object.__class__
                new_fields = SortedDict()
                rfks = reverse_foreign_keys(cls)
                ro2o = reverse_one_to_one_keys(cls)
                new_fields.update(rfks)
                new_fields.update(ro2o)
                get_all_dependencies(child_object, new_fields, user, m2m, all_dependencies, level + 1, starting_point=False)  
    if starting_point == True :
        return all_dependencies
