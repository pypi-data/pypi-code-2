"""
Base class for all models and unknown models.
"""
import traceback
import uuid
from collections import defaultdict
from meta import SubscribableModelMeta, ClassRegistry
from instancereg import InstanceRegistry

########################################################
# reference model
class SubscribableModel(object):
    """
    Base model supporting event notifications about changes.
    All models inherit from this class.

    Note you declare properties for the model using the properties
    from metamodel.properties in the class declaration.
    """
    __metaclass__ = SubscribableModelMeta
    _instances = []

    def __init__(self, instance_uuid=None, datasource=None, **kwargs):
        self._datasource = datasource
        self._evhs = []
        self._children = []
        self._references = defaultdict(list)
        self._referencedby = defaultdict(list)
        self._callbacks = defaultdict(list)
        self._props = {}
        self._parents = []
        self.__class__._instances.append(self)
        # set property values
        myclass = self.__class__
        kwargs = dict(kwargs)
        for propname, value in kwargs.iteritems():
            if propname in self.properties:
                setattr(self, propname, value)
            else:
                self._props[propname] = value
        # set uuid
        if instance_uuid:
            self.uuid = instance_uuid
        else:
            self.uuid = uuid.uuid1()

    def __str__(self):
        return "Model:"+str(self.name)+" ("+self.__class__.__name__+")"

    def trait(self, name):
        """
        Return the trait class for a given property.
        """
        return getattr(self.__class__, name)

    def _get_uuid(self):
        """
        Getter function for the uuid property.
        """
        return self._uuid

    def _set_uuid(self, value):
        """
        Setter function for the uuid property.

        The instance gets 'published' on the InstanceRegistry as
        soon as this is called.
        """
        if not value.__class__ == uuid.UUID:
            raise ValueError,"uuid %s is not an uuid.UUID!!"%value.__class__.__name__
        self._uuid = value
        self.on_uuid_set()
        InstanceRegistry.post(self)

    def on_uuid_set(self):
        """
        Convenience function which gets called after setting uuid, but
        before posting on the InstanceRegistry.
        """
        pass

    uuid = property(_get_uuid, _set_uuid)

    def new(self, clsname, instance_uuid=None, *args, **kwargs):
        """
        Create a new model from a classname or klass, 
        optional uuid, args and kwargs.
        """
        if self._datasource:
            inst = self._datasource.new(clsname,
                                        instance_uuid,
                                        *args,
                                        **kwargs)
        else:
            if isinstance(clsname, str):
                klass = ClassRegistry[clsname]
            else:
                klass = clsname
            inst = klass(instance_uuid,
                         self._datasource,
                         *args,
                         **kwargs)
        return inst

    def isDefault(self, propname):
        """
        Check whether an instance is default.
        """
        prop_obj = getattr(self.__class__, propname)
        return prop_obj._default == getattr(self, propname)

    def subscribe(self, *args):
        """
        Subscribe to this model changes.
        """
        if len(args) == 1:
            evh = args[0]
            if evh not in self._evhs:
                self._evhs.append(evh)
        elif len(args) == 2:
            signal = args[0]
            callback = args[1]
            self._callbacks[signal].append(callback)

    def unsubscribe(self, *args):
        """
        Unsubscribe from this model changes.
        """
        if len(args) == 1:
            evh = args[0]
            if evh in self._evhs:
                self._evhs.remove(evh)
        elif len(args) == 2:
            signal = args[0]
            callback = args[1]
            if signal in self._callbacks and callback in self._callbacks[signal]:
                self._callbacks[signal].remove(callback)

    def _post_evh(self, name, *args):
        """
        Post a message. Only for internal use.
        """
        for evh in reversed(self._evhs):
            if hasattr(evh, name):
                try:
                    getattr(evh, name)(*args)
                except:
                    print self
                    traceback.print_exc()

    def _post_signal(self, name, *args):
        """
        Send a signal. Only for internal use.
        """
        for callback in self._callbacks[name]:
            callback(*args)

    def post(self, name, *args):
        """
        Send a signal and post to general event handlers.
        """
        self._post_evh(name, *args)
        self._post_signal(name, *args)

    def setProperty(self, name, value):
        """
        Set a property to some value. Only for internal use.
        """
        self._props[name] = value
        self._post_evh("propertychange", name, value)
        self._post_signal(name, value)

    def getProperty(self, name):
        """
        Get a property value. Only for internal use.
        """
        return self._props[name]

    def getProperties(self):
        """
        Get all properties supported by this instance.
        """
        return self._props.keys()

    def delProperty(self, name):
        """
        Delete a property from this instance.
        """
        if name in self._props:
            del self._props[name]
        self.post("delproperty", name)

    def addChild(self, child):
        """
        Add a child.
        """
        self._children.append(child)
        child._parents.append(self)
        self.post("addchild", child)

    def delChild(self, child):
        """
        Delete a child.
        """
        self.post("delchild", child)
        child._parents.remove(self)
        self._children.remove(child)
        self.post("childdeleted", child)

    def getParents(self):
        """
        Return the node parents.
        """
        return self._parents

    def getChildren(self):
        """
        Get all children.
        """
        return self._children
    
    def getChildrenToPersist(self):
        """
        Method for datasources to return children that should be persisted.
        """
        return self.getChildren()

    def getSelfToPersist(self):
        """
        Method bad inherited classes have to inherit to return a different
        self to persist.
        """
        return self

    def getFromUrl(self, url):
        """
        Get a model from a relative path in the following form:
           /child1name/child2name/ -> child2
        """
        return self._getFromSplitUrl(url.split('/'))

    def _getFromSplitUrl(self, url):
        """
        Get a model from url tokens.
        """
        url = filter(lambda s: s, url)
        next = self
        for child in self.getChildren():
            next = child
            for url_tok in url:
                if url_tok:
                    next_test = next.findChild(url_tok)
                    if not next_test:
                        #print url_tok,map(lambda s: s.name, next.getChildren())
                        raise ValueError, "cannot resolve url:"+str(url)
                    next = next_test
            if next:
                return next

    def findChildren(self, name=None, ctype=None, uuid=None, recursive=False, stack=None):
        """
        Find children with a certain name or type.
        """
        children = self.getAllReferences()
        if not name == None:
            children = filter(lambda s: s.name == name, children)
        if not ctype == None:
            children = filter(lambda s: isinstance(s, ctype), children)
        if not uuid == None:
            # XXX actually it doesnt make sense to look for uuid in get
            # children, since there can be at most one, but saves some
            # code atm :P
            children = filter(lambda s: s.uuid == uuid, children)
            if children:
                return children
        if recursive:
            if stack == None:
                stack = set([self])
            for child in self.getAllReferences():
                if child in stack:
                    continue
                stack.add(child)
                children += child.findChildren(name, ctype, uuid, recursive, stack)
        return children

    def findChild(self, name=None, ctype=None, uuid=None, recursive=False):
        """
        Find the first child with a certain name or type.
        """
        children = self.findChildren(name, ctype, uuid, recursive)
        if children:
            return children[0]
        else:
            return None

    def findParents(self, name=None, ctype=None, recursive=False, stack=None, **kwargs):
        """
        Find parents with a certain name or type.
        """
        parents = self._parents
        if not name == None:
            parents = filter(lambda s: s.name == name, parents)
        if not ctype == None:
            parents = filter(lambda s: isinstance(s, ctype), parents)

        for key, value in kwargs.iteritems():
            parents = filter(lambda s: getattr(s, key) == value, parents)

        if recursive:
            if stack == None:
                stack = set([self])
            for parent in self._parents:
                if parent in stack:
                    continue
                stack.add(parent)
                parents += parent.findParents(name, ctype, recursive, stack, **kwargs)

            print "stack =", stack, "parents=", parents

        return parents

    def findParent(self, name=None, ctype=None, recursive=False, **kwargs):
        """
        Find the first parent with a certain name or type.
        """
        parents = self.findParents(name, ctype, recursive, **kwargs)
        if parents:
            return parents[0]
        else:
            return None

    def purgeChildren(self):
        """
        Unlink all children.
        """
        children = list(self.getChildren())
        children.reverse()
        for child in children:
            self.delChild(child)

    def getAllReferences(self):
        """
        A get all children and models referenced through properties
        (childs go last).
        """
        allref = []
        for refsection in self._references.values():
            allref += refsection
        allref += self.getChildren()
        return allref

    def getReferences(self):
        """
        Get all models referenced through properties.
        """
        allref = []
        for refsection in self._references.values():
            allref += refsection
        return allref

    #def _setReference(self, name, val):
    #    if val:
    #        self._references[name] = [val]
    #    else:
    #        self._references[name] = []

    def invalidate(self, force=False):
        """
        Invalidate this node.
        """
        if self._datasource and not force:
            self._datasource.invalidate(self)
            return
        for child in list(self._children):
            if len(child._parents) == 1:
                child.invalidate()
            else:
                # hiddenly remove the parenting info from the child.
                child._parents.remove(self)
        for parent in list(self._parents):
            parent.delChild(self)
        # unref references
        for refcls in self._references:
            setattr(self, refcls, None)
        for refcls in self._referencedby.keys():
            for ref in list(self._referencedby[refcls]):
                # remove self from people referencing us.
                setattr(ref, refcls, None)
        try:
            self.__class__._instances.remove(self)
        except ValueError:
            pass # XXX already removed. probably needs more thought.
        else:
            self.post("invalidate")

    def clone(self):
        """
        Clone this node and link the children.
        """
        newobj = self.new(self.__class__, **self._props)
        for child in self.getChildren():
            newobj.addChild(child)
        return newobj

    def deepclone(self, stack=None):
        """
        Deep clone this object branch.
        """
        if stack == None:
            stack = {}
        if self in stack:
            newobj = stack[self]
        else:
            newobj = self.new(self.__class__, **self._props)
            stack[self] = newobj
            for child in self.getChildren():
                newobj.addChild(child.deepclone(stack))
        return newobj

    def updateWith(self, aSubscribableModel, doReferences=True):
        """
        Update all properties of this model using the values of the
        given model.
        """
        for propname in aSubscribableModel.properties:
            # Ignore the uuid field since it should not be changed
            if propname == "uuid":
                continue

            if (not doReferences) and aSubscribableModel.trait(propname)._reference:
                continue

            old = getattr(self, propname)
            new = getattr(aSubscribableModel, propname)
            if old != new:
                setattr(self, propname, new)

    def _get_name(self):
        """name getter"""
        return self.__class__.__name__

    name = property(_get_name)

    builds = []
    builtby = []

class UnknownModel(SubscribableModel):
    """
    Class for models of a yet unknown model class.
    """
    # dont publish uuid
    def _get_uuid(self):
        """uuid getter"""
        return self._uuid

    def _set_uuid(self, val):
        """uuid setter"""
        self._uuid = val

    uuid = property(_get_uuid, _set_uuid)

