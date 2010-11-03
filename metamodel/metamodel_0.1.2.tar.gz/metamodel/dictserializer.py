"""
Generic methods to serialize models to and from python dicts.
"""

import uuid

from meta import ClassRegistry
from basemodel import SubscribableModel, UnknownModel
from instancereg import ChildWaiter, PropWaiter

def find_uuid(obj_uuid):
    """
    Find the object with a certain uuid.
    """
    for klass in ClassRegistry.values():
        # check _instances because we want only the
        # instances for this class.
        for inst in klass._instances:
            try:
                if inst.uuid == obj_uuid:
                    return inst
            except AttributeError:
                pass

def wait_for_class(clsname, objid, obj, reqclsname, datasource):
    """
    Wait for the given class to appear.
    """
    def wait(_):
        LoadModel({objid:obj}, reqclsname, datasource)
    ClassRegistry.subscribe(wait, clsname)

def check_unref_properties(tounref, objects):
    """
    Check for properties which can be unrefed to this object.
    """
    # unref properties
    for newobj2, prop, val in tounref:
        try:
            val = objects[val]
        except KeyError:
            obj = find_uuid(uuid.UUID(val))
            if obj:
                objects[val] = obj
                val = obj
            else:
                PropWaiter(uuid.UUID(val), newobj2, prop)
                val = UnknownModel()
        setattr(newobj2, prop, val)
        
def check_unref_children(unrefchilds, objects):
    """
    Check for objects which have to be connected to this one.
    """
    # unref children
    for newobj, children in unrefchilds:
        for child in children:
            try:
                newobj.addChild(objects[child])
            except KeyError:
                obj = find_uuid(uuid.UUID(child))
                if obj:
                    objects[child] = obj
                    newobj.addChild(obj)
                else:
                    ChildWaiter(uuid.UUID(child), newobj)

def LoadModel(objs, reqclsname=None, datasource=None):
    """
    Convert given dict model into metamodel classes.
    """
    retobj = []
    objects = {}
    tounref = []
    unrefchilds = []
    # load objects
    for objid, obj in objs.iteritems():
        clsname, objuuid = objid.split("#")
        if not clsname in ClassRegistry:
            wait_for_class(clsname, objid, dict(obj), reqclsname, datasource)
            continue
        cls = ClassRegistry[clsname]
        objunref = []
        kwargs = {}
        children = obj.pop("children")
        for prop, value in obj.iteritems():
            if isinstance(value, str) and value.startswith("uuid:"):
                try:
                    value = objects[value[5:]]
                    kwargs[prop] = value
                except KeyError:
                    objunref.append([prop, value[5:]])
            else:
                kwargs[prop] = value
        if datasource:
            newobj = datasource.new(cls, uuid.UUID(objuuid), **kwargs)
        else:
            newobj = cls(uuid.UUID(objuuid), **kwargs)
        # append the references needing unrefing
        for prop, val in objunref:
            tounref.append([newobj, prop, val])
        # check if its in the class requested
        if reqclsname and clsname == reqclsname:
            retobj.append(newobj)
        objects[objuuid] = newobj
        # add the childs for unrefing
        if len(children):
            unrefchilds.append([newobj, children])
    # unref or produce waiters
    check_unref_properties(tounref, objects)
    check_unref_children(unrefchilds, objects)
    return retobj

def SaveModel(model):
    """
    Convert given model into a dict.
    """
    # prepare struct
    props = { "children" : map(lambda s: str(s.uuid),
                                           model.getChildrenToPersist()) }
    obj = {str(model.__class__.__name__)+"#"+str(model.uuid): props}
    # dereference properties, the ones in the internal dictionary are
    # the ones assumed to be set.
    for prop, value in model._props.iteritems():
        if isinstance(value, SubscribableModel):
            props[prop] = "uuid:"+str(value.uuid)
        else:
            props[prop] = value
    return obj

