"""
Dynamic class and instance synchronization against the ontology model.

Maintains a set of python classes accessible through 
metamodel.RegistryView.<ClassName>.
"""

from basemodel import SubscribableModel
from metamodel import MetaProperty, MetaModel, Namespace
from properties import Property, Vector3, Vector2, Color, Color4
from meta import SubscribableModelMeta, ClassRegistry
from yamlserializer import LoadModel
from baseview import ViewObjectBase, ModelViewBase

class PropertyGuardian(ViewObjectBase):
    """
    Guards a property for a specific class.

    Synchronizes changes in the model into the python classes and instances.
    """
    def __init__(self, view, parent, model):
        ViewObjectBase.__init__(self, view, parent, model)
        self.create_property(model)
        # backup some values in case they change...
        self._name = model.name
        self._type = model.type
        self._default = model.default

    def create_property(self, model):
        """
        Create some property in the guarded python class.
        """
        klass = ClassRegistry[self._parents[0].classname] # XXX _parents use
        if model.name in klass.properties:
            return
        propclass = Property
        propmap = {"Vector3": Vector3, "Vector2": Vector2, "Color4": Color4,
                   "Color": Color}
        if model.type in propmap:
            propclass = propmap[model.type]
            default = eval(model.default)
        else:
            try:
                proptype = eval(model.type)
                try:
                    if proptype == bool:
                        if model.default in ["False", "false", "no", "0"]:
                            default = False
                        else:
                            default = True
                    elif proptype == list:
                        default = eval(model.default)
                    else:
                        default = proptype(model.default)
                except:
                    default = None
            except:
                proptype = ClassRegistry[model.type]
                default = None
        if propclass == Property:
            prop = Property(proptype, default)
        else:
            prop = propclass()
        prop.name = model.name
        klass.properties.append(model.name)
        setattr(klass, model.name, prop)
        for inst in klass.get_instances():
            if prop.name in inst._props:
                value = inst._props[prop.name]
            else:
                value = default
            if not value == None:
                inst._post_evh("propertychange", prop.name, value)
                inst._post_signal(prop.name, value)
            #    inst.properties.append(model.name)
        #if not default == None:
            #    for inst in klass.get_instances():
                #    setattr(inst, model.name, default)

    def invalidate(self):
        """
        Invalidate callback
        """
        klass = ClassRegistry[self._parents[0].classname] # XXX _parents use
        for inst in klass.get_instances():
            inst.delProperty(self._model.name)
        # destroy in class
        delattr(klass, self._model.name)

    def change_name(self, value):
        """
        the property changed name
        """
        if value == self._name:
            return
        klass = ClassRegistry[self._parents[0].classname] # XXX _parents use
        klass.properties.remove(self._name)
        prop = Property(eval(self._model.type), self._model.default)
        prop.name = value
        # create the new property in the class
        setattr(klass, value, prop)
        # recreate properties at instances
        for inst in klass._instances:
            oldval = getattr(inst, self._name)
            # create new property
            setattr(inst, value, oldval)
            inst.delProperty(self._name)
        # remove old property
        delattr(klass, self._name)
        # set some extra info
        klass.properties.append(value)
        self._name = value

    def change_default(self, value):
        """
        the property changed default

        adapt defaults.
        """
        klass = ClassRegistry[self._parents[0].classname] # XXX parents use
        prop = getattr(klass, self._name)
        for inst in klass._instances:
            oldval = getattr(inst, self._name)
            if oldval == self._default:
                # reset XXX not sure this is best..
                setattr(inst, self._name, value)
        prop.default = value
        self._default = value

    def change_type(self, value):
        """
        the property changed type

        adapt values in instances, adapt default.
        """
        k = ClassRegistry[self._parents[0].classname] # XXX parents use
        prop = getattr(k, self._name)
        # change type
        prop.type = eval(value)
        # correct default
        try:
            # try to convert
            newdefault = prop.type(self._default)
        except:
            # else default to empty constructor for declared type
            newdefault = prop.type()
        # set default
        self._model.default = newdefault
        # pass
        for inst in k._instances:
            oldval = getattr(inst, self._name)
            #print "apply change type:",oldval
            try:
                newval = prop.type(oldval)
            except ValueError:
                newval = prop.default
            setattr(inst, self._name, newval)
        self._type = value

    # properties reacting to the model's properties.
    type = property(None, change_type)
    default = property(None, change_default)
    name = property(None, change_name)


class ClassGuardian(ViewObjectBase):
    """
    Guards a class.

    Synchronizes changes in the model into a python class.
    """
    def __init__(self, view, parent, model):
        ViewObjectBase.__init__(self, view, parent, model)
        if not model.classname in ClassRegistry:
            self._instance = self.createClass(model)
        else:
            # XXX should check consistency?
            self._instance = ClassRegistry[model.classname]

    def createClass(self, model):
        """
        fill in class dictionary and parents information
        """
        dct = {}
        parents = ()
        for parent in model.inheritfrom:
            parents += (ClassRegistry[parent],)
        if not parents:
            parents = (SubscribableModel,)
        dct["builds"] = model.builds_list
        dct["builtby"] = model.builtby_list
        klass = SubscribableModelMeta.__new__(SubscribableModelMeta,
                                                   model.classname,
                                                   parents,
                                                   dct,
                                                   model)
        klass._model = model # XXX just for the test :P
        ClassRegistry[model.name] = klass
        namespaces = self.findClassNamespaces()
        for ns in namespaces:
            ClassRegistry[ns+"."+model.name] = klass
        return klass

    def findClassNamespaces(self):
        namespaces = []
        parents = []
        model = self._model
        parent_nss = filter(lambda s: isinstance(s, Namespace), model.getParents())
        for parent_ns in parent_nss:
            parents = self._findParentNS([parent_ns], [])
            for parent in parents:
                parent_names = map(lambda s: s.name, parent)
                namespaces.append(".".join(parent_names))
        return namespaces

    def _findParentNS(self, path, stack):
        all_parents = []
        ns = path[0]
        parent_nss = filter(lambda s: isinstance(s, Namespace), ns.getParents())
        if parent_nss:
            for parent_ns in parent_nss:
                parent_path = [parent_ns] + path
                parents = self._findParentNS(parent_path, [])
                all_parents += parents
        else:
            all_parents = [path]
        return all_parents

    def invalidate(self):
        """
        Invalidate callback.
        """
        print "ClassGuardian::invalidate not implemented!"


class NamespaceGuardian(ViewObjectBase):
    """
    Guards an ontology.

    Listens for ontology top level additions or removals.
    """
    pass


class InstanceRegistryModel(SubscribableModel):
    """
    Main model to hold all ontologies.
    """
    builds = ["Namespace"]


class InstanceRegistry(ModelViewBase):
    """
    A registry that syndicates loaded ontology models.

    Can load a number of ontologies from disk.
    """
    _model2view = {
        "Namespace" : [NamespaceGuardian],
        "MetaModel" : [ClassGuardian],
        "MetaProperty" : [PropertyGuardian],
    }

    def __init__(self, model):
        ModelViewBase.__init__(self, model)
        self._internalNamespace = self._model.new(Namespace, name="internal")
        self._model.addChild(self._internalNamespace)

    def createClassModel(self, cls):
        """
        Create a (meta)model for a class directly declared from python.
        """
        bases = []
        for base in cls.__bases__:
            if issubclass(base, SubscribableModel) and not base == cls:
                bases.append(base.__name__)
        class_meta = self._model.new(MetaModel, classname=cls.__name__, 
                               name=cls.__name__, 
                               inherit_from=bases, 
                               builtby_list=list(cls.builtby), 
                               builds_list=list(cls.builds))
        for propname in dir(cls):
            try:
                prop_obj = getattr(cls, propname)
            except AttributeError:
                continue
            if isinstance(prop_obj, Property):
                metaprop = self._model.new(MetaProperty, name=prop_obj.name,
                                       type = prop_obj.type.__name__,
                                       ro = prop_obj.ro)
                if not prop_obj._default == None:
                    metaprop.default = str(prop_obj._default)
                class_meta.addChild(metaprop)
        namespacename = cls.__module__
        ont = self.createNamespaces(namespacename)
        ont.addChild(class_meta)
        return class_meta

    def createNamespaces(self, namespacename):
        splitname = namespacename.split('.')
        currparent = self._model
        while splitname:
            ont = currparent.findChild(splitname[0])
            if not ont:
                ont = currparent.new(Namespace, name=splitname[0])
                currparent.addChild(ont)
            currparent = ont
            splitname.pop(0)
        return ont

    def __getattr__(self, name):
        """
        Implements attribute access for instanced classes.
        """
        return ClassRegistry[name]

    def load_file(self, filename):
        """
        load a file with ontology data
        """
        afile = open(filename)
        data = afile.read()
        afile.close()
        ontologies = LoadModel(data,"Namespace")
        for ontology in ontologies:
            self._model.addChild(ontology)


# the class instance registry
Registry = InstanceRegistryModel()
RegistryView = InstanceRegistry(Registry)

