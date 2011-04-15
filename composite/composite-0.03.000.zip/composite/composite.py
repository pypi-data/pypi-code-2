"""Composite -- used instead of multiple inheritance, inspired my Michele Simionato's Simple Traits experiment

Python Version: 3.x

Intended use:
    To combine a single base class, as many Parts as needed/desired, glue code to combine together succussfully.  
    While Parts are kept in classes, they should be functions only: no state information should be kept.  If 
    different parts from different classes having the same name are combined into one class, that class must 
    specify which one it wants, or an error will be raised at class creation time.  If __magic_methods__ are part 
    of the Parts, their names must be specified in the part classes __magic_parts__ list attribute; like-wise, 
    if Parts have required attributes that must be supplied by the composed class/other Parts, their names must 
    be in the __required_parts__ list attribute; finally, if the part in the base class is the desired one, it's
    name must be in __base_parts__.

Name resolution order:
    Least - Base class
            Composite
    Most -  Current (composed) class
    
Composite sources (aka Parts) are a bunch of methods and attributes with the following properties:

   1. the methods/attributes in a Part belong logically together
   2. if a Part enhances a class, then all subclasses are enhanced too
   3. if a Part has methods in common with the class, then the methods defined in the class have precedence
   4. the Parts order is not important, i.e. enhancing a class first with Part P1 and then with Part P2 or viceversa is the same
   5. if parts P1 and P2 have names in common, enhancing a class with P1 and P2 raises an error
          because the final class has final say, conflicts can be resolved there (by hand)
   6. if a Part has methods in common with the base class, then the Part methods have precedence
   7. a class can be seen both as a composition of Parts and as an homogeneous entity
"""

import sys
from collections import defaultdict

__version__ = "0.03.000"

__all__ = ['Composite']

class Composite(type):
    def __init__(yo, *args, **kwargs):
        super().__init__(*args)
    def __new__(metacls, cls_name, cls_bases, cls_dict, parts=tuple()):
        if len(cls_bases) > 1:
            raise TypeError("multiple bases not allowed with Composite")
        result_class = type.__new__(metacls, cls_name, cls_bases, cls_dict)
        found_conflict = False
        errors = []
        __base_parts__ = getattr(result_class, '__base_parts__', tuple())
        base_class = cls_bases[0]

        for part in result_class.__part_conflicts__:
            if part not in __base_parts__:
                bc_part = getattr(base_class, part, None)         # get the part from the base class if it exists
                rc_part = getattr(result_class, part, None)       # get the part from the result class if it exists
                if rc_part is None or rc_part is bc_part:         # conflict not resolved by result class?
                    found_conflict = True
                    if bc_part:
                        result_class.__part_conflicts__[part].insert(0, base_class)
                    errors.append("           conflict:  <%s> is in %s" % (part, result_class.__part_conflicts__[part]))
        delattr(result_class, '__part_conflicts__')

        required_missing = False
        for part in result_class.__required_parts__:
            if getattr(result_class, part, None) is None:
                required_missing = True
                errors.append("missing requirement:  %s needs <%s>" % (result_class.__required_parts__[part][0], part))
        delattr(result_class, '__required_parts__')

        if found_conflict or required_missing:
            error = ('','conflicts','missing requirements','conflicts and missing requirements')[found_conflict*1 + required_missing*2]
            error = "%s in %s" % (error, cls_name)
            error = error + "\n\n" + '\n'.join(errors)
            raise TypeError(error)

        return result_class

    @classmethod
    def __prepare__(metacls, name, bases, parts=tuple()):
        """inserts the requested parts into the class dictionary
        if there are conflicting parts, they will be inserted into a __part_conflicts__
        attribute, and must be sorted out in the class definition itself or a TypeError
        will be raised."""
        if not parts:
            raise TypeError("no parts specified... what's the point?")
        elif type(parts) != tuple:
            parts = (parts, )
        class_dict = _Dict()
        parts_dict = defaultdict(list)
        for name, obj in (
                ('parts', _Parts()), 
                ('__part_conflicts__', defaultdict(list)),
                ('__magic_parts__', set()),
                ('__required_parts__', defaultdict(list)) ):
            class_dict[name] = obj
            setattr(class_dict, name, obj)
        for bundle in parts:
            class_dict.parts.add(bundle)
            metacls.integrate_parts(class_dict, parts_dict, bundle)
        metacls.check_conflicts(class_dict, parts_dict)
        return class_dict

    @staticmethod
    def check_conflicts(class_dict, parts_dict):
        """does the actual checking for conflicts"""
        for part, cls_list in parts_dict.items():
            if len(cls_list) == 1:
                class_dict[part] = getattr(cls_list[0], part)
            else:
                first_part = getattr(cls_list[0], part)
                for next_class in cls_list[1:]:
                    next_part = getattr(next_class, part)
                    if first_part is not next_part:
                        class_dict.__part_conflicts__[part] = cls_list
                        break
                    else:
                        class_dict[part] = first_part

    @staticmethod
    def integrate_parts(class_dict, parts_dict, bundle):
        required = getattr(bundle, '__required_parts__', tuple())
        magic_parts = getattr(bundle, '__magic_parts__', tuple())
        for part in required:
            class_dict.__required_parts__[part].append(bundle) 
        for part in magic_parts:
            class_dict.__magic_parts__.add(part)
            parts_dict[part].append(bundle) 
        for part in [p for p in dir(bundle) if not (p[:2] == p[-2:] == '__')]:
            parts_dict[part].append(bundle) 


class _Dict(dict):
    "Normal dict with parts attribute, will be the class dictionary"
    pass

class _Parts:
    "container for part bundles"
    def __init__(yo):
        yo.bundles = set()
    def __contains__(yo, part):
        "True if part is in *any* bundle"
        for bundle in yo.bundles:
            if part is getattr(bundle, str(part), None):
                return True
        return False
    def __repr__(yo):
        return "(%s)" % ", ".join([str(getattr(yo, bundle)) for bundle in dir(yo) if not bundle[:2] == bundle[-2:] == '__'])
    def __str__(yo):
        result = []
        for bundle in yo.bundles:
            bundle_name = "%s:  " % bundle
            bundle_str = []
            bundle_str.append('normal=' + str(["%s" % part for part in dir(bundle) if not part[:2] == part[-2:] == '__']))
            for parts, title in (('__magic_parts__','magic='), ('__required_parts__','required='), ):
                parts = getattr(bundle, parts, None)
                if parts:
                    bundle_str.append(title + str(["%s" % req for req in parts]))
            result.append(bundle_name + ', '.join(bundle_str))
        return '\n'.join(result)
    def add(yo, bundle):
        if bundle in yo.bundles:
            raise ValueError("bundle %s already added" % bundle)
        yo.bundles.add(bundle)
        setattr(yo, str(bundle), bundle)

