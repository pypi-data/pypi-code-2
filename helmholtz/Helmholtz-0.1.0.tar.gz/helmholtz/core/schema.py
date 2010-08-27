#encoding:utf-8
from django.utils.datastructures import SortedDict
from helmholtz.core.shortcuts import get_subclasses

def get_parents_recursively(entity):
    """Return parent classes defining a hierarchy of subclass."""
    result = list()
    for parent in entity._meta.parents :
        result.append(parent)
        result.extend(get_parents_recursively(parent))
    return result

def create_subclass_lookup(entity):
    chain = get_parents_recursively(entity)[0:-1]
    chain.reverse()
    chain.append(entity)
    lookup = '__'.join([k.__name__.lower() for k in chain])
    return lookup

def regular_fields(entity, inheritance=False):
    """Return regular fields of the specified Model."""
    choices = ['ForeignKey', 'OneToOneField']
    fields = [k.name for k in entity._meta.fields if not (k.__class__.__name__ in choices)] 
    return fields 

def is_regular_field(entity, field):
    """Return a boolean telling if a field is a regular field."""
    fields = regular_fields(entity)
    return (field in fields)

def subclasses(entity, proxies=False):
    """Return all direct subclasses of the specified Model."""
    classes = SortedDict()
    for subclass in get_subclasses(entity, proxies) :
        classes[subclass.__name__.lower()] = subclass
    return classes

def get_subclasses_recursively(entity, strict=True, proxies=False):
    """Return all subclasses of a Model in a recursive manner."""
    subclasses = list()
    for subclass in get_subclasses(entity, proxies) :
        subclasses.append(subclass)
        subclasses.extend(get_subclasses_recursively(subclass))
    if not strict :
        subclasses.insert(0, entity)    
    return subclasses

def get_base_class(entity):
    """Return the root base class of a Model."""
    parents = get_parents_recursively(entity) 
    return parents[-1]

def cast_queryset(queryset, key):
    """Return a QuerySet filtered by actual object type."""
    subclasses = get_subclasses_recursively(queryset.model)
    if isinstance(key, str) :
        names = [k.__name__ for k in subclasses]
        index = names.index(key)
    else :
        index = subclasses.index(key)
    selection = subclasses[index]
    lookup = create_subclass_lookup(selection)
    dct = {'%s__isnull' % lookup:False}
    pks = [k.id for k in queryset.filter(**dct).distinct()]
    objects = selection.objects.filter(pk__in=pks)
    return objects

def get_parent_chain(obj, field):
    """Return all node of a hierarchy defined by a self referencing Model.""" 
    result = list()
    parent = getattr(obj, field)
    if parent :
        result.append(parent)
        result.extend(get_parent_chain(parent, field))
    return result
        
def get_root_node(obj, field):
    """Return the root node of a hierarchy defined by a self referencing Model."""
    parent = getattr(obj, field)
    if parent :
        return get_root_node(parent, field)
    else :
        return obj

def get_all_children(obj, field, children=None, recursive=False, starting_point=True, as_queryset=False):
    """Return children of the specified object in a recursive manner."""
    if starting_point :
        children = list()
    manager = getattr(obj, field)
    new_children = [k for k in manager.all()]
    for child in new_children :
        if not (child in children) :
            children.append(child)
        if recursive : 
            get_all_children(child, field, children, recursive, False)
    if starting_point :
        if not as_queryset :
            return children
        else :
            pks = [k.pk for k in children]
            queryset = obj.__class__.objects.filter(pk__in=pks)
            return queryset

def subclasses_tree(entity):
    """Return subclasses of the specified Model in a recursive manner."""
    classes = SortedDict()
    for subclass in entity.__subclasses__() :
        class_name = subclass.__name__.lower()
        classes[class_name] = SortedDict()
        classes[class_name]['class'] = subclass
        classes[class_name]['field'] = subclass._meta.pk.name
    return classes

def foreign_keys(entity, display_ptr=True):
    """Return ForeignKeys of a of Model."""
    choices = ['ForeignKey', 'OneToOneField']
    fks = SortedDict()
    entities = get_parents_recursively(entity)
    entities.reverse()
    entities.append(entity)
    for entity in entities :
        for field in entity._meta.fields :
            if (field.__class__.__name__ in choices) :
                strict = (entity.__class__.__name__ != field.rel.to.__class__.__name__) 
                is_strict_subclass = (display_ptr and issubclass(entity, field.rel.to) and strict)
                if (not is_strict_subclass) : 
                    fks[field.name] = SortedDict()
                    fks[field.name]['class'] = field.rel.to
                    fks[field.name]['field'] = field.rel.field_name  
                    fks[field.name]['is_required'] = not field.null
                    fks[field.name]['type'] = 'fk' 
                    fks[field.name]['is_o2o'] = True if (field.__class__.__name__ != 'ForeignKey') else False
    return fks 

def many_to_many_fields(entity):
    """Return local ManyToManyFields of a Model."""
    mks = SortedDict()
    entities = get_parents_recursively(entity)
    entities.reverse()
    entities.append(entity)
    for entity in entities :
        for field in entity._meta.local_many_to_many :
            if field.__class__.__name__ != 'GenericRelation' :
                mks[field.name] = SortedDict()
                mks[field.name]['class'] = field.rel.to
                mks[field.name]['field'] = None    
                mks[field.name]['type'] = 'm2m'
                mks[field.name]['is_required'] = False#not field.null or not field.blank
    return mks

def reverse_one_to_one_keys(entity):
    """Return reverse one to one fields of a Model."""
    fks = foreign_keys(entity)
    reverse_oks = SortedDict()
    choices = ['ReverseSingleRelatedObjectDescriptor', 'SingleRelatedObjectDescriptor']
    internal = entity.__dict__
    for field in internal :
        attribute = internal[field]
        class_name = attribute.__class__.__name__
        if (not (field in fks)) and (class_name in choices) :
            subcls = entity.__subclasses__()
            if (class_name == choices[0]) and not (attribute.field.rel.to in subcls) :
                reverse_oks[field] = SortedDict()
                reverse_oks[field]['class'] = attribute.field.rel.to
                reverse_oks[field]['field'] = attribute.field.rel.field_name
                f = getattr(attribute.field.rel.to, attribute.field.rel.field_name)
                reverse_oks[field]['is_required'] = not f.null
                reverse_oks[field]['type'] = 'reverse_o2o'
            elif class_name == choices[1] and not (attribute.related.model in subcls) :
                reverse_oks[field] = SortedDict() 
                reverse_oks[field]['class'] = attribute.related.model
                reverse_oks[field]['field'] = attribute.related.field.name
                reverse_oks[field]['is_required'] = not attribute.related.field.null
                reverse_oks[field]['type'] = 'reverse_o2o'
    return reverse_oks

def reverse_foreign_keys(entity):
    """Return reverse reverse foreign keys of a Model."""
    fks = foreign_keys(entity)
    reverse_fks = SortedDict()
    choices = ['ForeignRelatedObjectsDescriptor']
    all_classes = list(entity._meta.get_parent_list())
    all_classes.append(entity)
    for cls in all_classes :
        internal = cls.__dict__
        for field in internal :
            attribute = internal[field]
            class_name = attribute.__class__.__name__
            if (not (field in fks)) and (class_name in choices) and not (class_name in reverse_fks) :
                if class_name == choices[0] : 
                    reverse_fks[field] = SortedDict()
                    reverse_fks[field]['class'] = attribute.related.model
                    reverse_fks[field]['field'] = attribute.related.field.name
                    reverse_fks[field]['is_required'] = not attribute.related.field.null
                    reverse_fks[field]['type'] = 'reverse_fk'
    return reverse_fks

def reverse_many_to_many_fields(entity):
    """Return reverse many to many fields of a Model."""
    mks = many_to_many_fields(entity)
    reverse_mks = SortedDict()
    internal = entity.__dict__
    for field in internal :
        attribute = internal[field]
        class_name = attribute.__class__.__name__
        if (not (field in mks)) and (class_name == "ManyRelatedObjectsDescriptor") :
            reverse_mks[field] = SortedDict()
            reverse_mks[field]['class'] = attribute.related.model
            reverse_mks[field]['field'] = attribute.related.field.name
            reverse_mks[field]['is_required'] = False
            reverse_mks[field]['type'] = 'reverse_m2m'
    return reverse_mks

def generic_foreign_keys(entity):
    """Return local GenericForeignKeys of a Model."""
    gfks = SortedDict()
    for attr in entity._meta.virtual_fields :
        if attr.__class__.__name__ == 'GenericForeignKey' :
            gfks[attr.name] = SortedDict()
            gfks[attr.name]['ct_field'] = attr.ct_field
            gfks[attr.name]['fk_field'] = attr.fk_field  
            gfks[attr.name]['type'] = 'generic_fk' 
            ct_field = [k for k in entity._meta.fields if k.name == attr.ct_field][0]
            fk_field = [k for k in entity._meta.fields if k.name == attr.fk_field][0]
            assert ct_field.null == fk_field.null, "ct_field.null and fk_field.null must be equal"
            gfks[attr.name]['is_required'] = not (ct_field.null and fk_field.null)
    return gfks

def generic_relations(entity):
    """Return local GenericRelations of a Model."""
    grs = SortedDict()
    entities = get_parents_recursively(entity)
    entities.reverse()
    entities.append(entity)
    for entity in entities :
        for field in entity._meta.local_many_to_many :
            if field.__class__.__name__ == 'GenericRelation' :
                gfk = [k.name for k in field.rel.to._meta.virtual_fields if (k.__class__.__name__ == 'GenericForeignKey') and (k.ct_field == field.content_type_field_name) and (k.fk_field == field.object_id_field_name)]
                assert len(gfk) == 1, "problem with GenericRelation key of model %s" % (entity)
                grs[field.name] = SortedDict()
                grs[field.name]['class'] = field.rel.to
                grs[field.name]['verbose'] = field.verbose_name
                grs[field.name]['field'] = gfk[0] 
                grs[field.name]['type'] = 'generic_rel' 
                grs[field.name]['is_required'] = False
    return grs
