#encoding:utf-8
from copy import deepcopy
from django.conf import settings
from django.utils.datastructures import SortedDict
from django.core.management.base import NoArgsCommand
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from helmholtz.core import loggers
from helmholtz.core.schema import foreign_keys, many_to_many_fields, reverse_one_to_one_keys, reverse_foreign_keys, reverse_many_to_many_fields, generic_foreign_keys, generic_relations, subclasses
from helmholtz.core.modules import get_application_classes
from helmholtz.access_control.lifecycle import create_group_permission
  
logging = loggers.create_mixed_logger('helmholtz.core.populate', 'a') if settings.DEBUG else loggers.create_console()
keywords = ['__cleanup__']#force and __target_class__ are reserved

class Column(object):
    """A way to represent a hierachical structure 
    and provide the dot notation on each of its node."""
    def __init__(self, entry_point, recursive=True):
        self.__dict__['_sorted_dict'] = SortedDict()
        self.__dict__['entry_point'] = deepcopy(entry_point)
        self.objectify()
        self.__dict__.pop('entry_point')

    def __getattr__(self, name): 
        return self._sorted_dict[name]
    
    def __setattr__(self, name, value):
        self._sorted_dict[name] = value
    
    def __delattr__(self, name):
        if name in self._sorted_dict :
            del self._sorted_dict[name]
        else :
            super(Column, self).__delattr__(self, name)

    def __deepcopy__(self, memo):
        new = self.__class__(deepcopy(self._sorted_dict), True)
        return new  
        
    def objectify(self, recursive=True):
        """Generate the object tree from a dictionary."""
        for field in self.entry_point :
            entry_point = self.entry_point[field]
            if isinstance(entry_point, dict) and (len(entry_point) > 0) :
                new_object = Column(entry_point, recursive) 
                self._sorted_dict[field] = new_object
            else :
                self._sorted_dict[field] = entry_point 
                if (isinstance(entry_point, list) or isinstance(entry_point, set)) and (len(entry_point) > 0) :
                    index = 0
                    for item in entry_point :
                        assert item.__class__.__name__ in ['dict', 'int', 'float', 'bool', 'str', 'unicode', 'Column'], 'not implemented case'
                        if isinstance(item, dict) :
                            new_object = Column(item, recursive) 
                            entry_point[index] = new_object    
                        index += 1 
    
    def list_or_set_recursion(self, entry_point, objects, cleanup, recursive):
        """Enable the recursion even for node containing list or set."""
        index = 0
        to_clean = []
        for item in objects :
            if isinstance(item, Column) :
                sub_cleanup = cleanup if not hasattr(item, '__cleanup__') else item.__cleanup__
                new_item = item.dictionarize(sub_cleanup, recursive, False)
                entry_point.append(new_item)
                if not new_item :
                    to_clean.append(index)
            elif recursive and (isinstance(item, list) or isinstance(item, set)) and (len(item) > 0) :
                new_item = self.list_or_set_recursion(entry_point[index], item, cleanup, recursive)
                entry_point.append(new_item)
                if not new_item :
                    to_clean.append(index)
            elif item.__class__.__name__ == 'NoneType' :
                entry_point.append(item)
                if not item :
                    to_clean.append(index)
            else :
                entry_point.append(item)        
            index += 1
        if cleanup :
            for index in to_clean :
                entry_point.pop(index)
    
    def dictionarize(self, cleanup=False, recursive=True, starting_point=True):
        """Return a dictionary from the object structure."""
        dct = SortedDict()
        to_clean = []
        for attr in self._sorted_dict :
            #to avoid recursion caused by a dictionary
            #force a dictionary to be a node of the object
            obj = self._sorted_dict[attr] 
            
            if isinstance(obj, dict) and recursive :
                self._sorted_dict[attr] = Column(obj)
                obj = self._sorted_dict[attr] 
            if isinstance(obj, Column) and recursive :
                sub_cleanup = cleanup if not hasattr(obj, '__cleanup__') else obj.__cleanup__
                dct[attr] = obj.dictionarize(sub_cleanup, recursive, False)
                if not dct[attr] :
                    to_clean.append(attr)
            elif (isinstance(obj, list) or isinstance(obj, set)) :
                dct[attr] = obj.__class__()
                if len(obj) > 0 : 
                    if recursive :  
                        self.list_or_set_recursion(dct[attr], obj, cleanup, recursive)    
                else :
                    to_clean.append(attr)
            elif (not obj) and not isinstance(obj, bool) :
                dct[attr] = None
                to_clean.append(attr)
            elif not (attr in keywords) :
                dct[attr] = obj
                
        #cleanup nodes that are empty dictionaries
        if cleanup :
            for attr in to_clean :
                dct.pop(attr)    
        return dct            

class Populate(object):
    
    def __init__(self):
        self.all_classes = get_application_classes()
    
    def cleanup_database(self, excluded_tables=[], excluded_apps=[]):
        """Cleanup all database tables excepting those where name appears in the exclude parameter and not included in applications."""
        if len(excluded_apps) < 1 :
            model_classes = [k for k in self.all_classes if not (k.__name__ in excluded_tables)]
        else :
            model_classes = [k for k in self.all_classes if (not (k.__name__ in excluded_tables)) and (not (k.__module__.split('.')[-1] in excluded_apps))]
        for cls in model_classes :
            cls.objects.all().delete()
    
    def list_or_set_recursion(self, entry_point, cleanup, recursive):
        index = 0
        to_clean = []
        for item in entry_point :
            if isinstance(item, Column) :
                entry_point[index] = item.dictionarize(cleanup, recursive, False)
                if not entry_point[index] :
                    to_clean.append(index)
            elif recursive and isinstance(item, dict) :
                entry_point[index] = self.dictionarize(item, cleanup, recursive, False)
                if not entry_point[index] :
                    to_clean.append(index)  
            elif item.__class__.__name__ == 'NoneType' :
                to_clean.append(index)  
            index += 1
            
        if cleanup :
            for index in to_clean :
                entry_point.pop(index)
    
    def dictionarize(self, props, cleanup=False, recursive=True, starting_point=True):
        """Generate a dictionary from the object structure."""
        dct = props
        to_clean = []
        for attr in dct :
            if isinstance(dct[attr], Column) and recursive :
                dct[attr] = dct[attr].dictionarize(cleanup, recursive, False)
                if not dct[attr] :
                    to_clean.append(attr)
            elif isinstance(dct[attr], dict) and recursive :
                dct[attr] = self.dictionarize(dct[attr], cleanup, recursive, False)
                if not dct[attr] :
                    to_clean.append(attr)
            elif (isinstance(dct[attr], list) or isinstance(dct[attr], set)) :
                if (len(dct[attr]) > 0) :
                    if recursive : 
                        self.list_or_set_recursion(dct[attr], cleanup, recursive)
                else :
                    to_clean.append(attr)  
            elif (not dct[attr]) and not isinstance(dct[attr], bool) :
                dct[attr] = None
                to_clean.append(attr)
        if cleanup :
            for attr in to_clean :
                dct.pop(attr)       
        return dct
    
    def transform(self, props, fks, generic_fks, entity):
        """Replaces field values by their corresponding objects."""
        global all_classes
        cache = props.copy()
        for property in cache :
            if (cache[property].__class__.__class__.__name__ != "ModelBase") : 
                pk_db = entity._meta.pk.name
#                if (property in fks) and (property != pk_db) :
                if (property in fks) and ((property != pk_db) or not issubclass(entity, entity._meta.pk.rel.to)) :
                    #get or create object corresponding to a foreign key that is not a super class pointer (*_ptr)
                    
                    tmp = cache[property]
                    if tmp :
                        attributes = [tmp]
                        entity = fks[property]['class'] 
                        #replace nested objects 
                        new_object = self.store(entity, attributes)[0]
                        cache[property] = new_object
                elif (property in generic_fks) :
                    #get or create object corresponding to a generic foreign key
                    tmp = cache[property]
                    if tmp :
                        try :
                            entity = tmp.pop('__target_class__')
                            entity = [k for k in self.all_classes if k.__name__ == entity][0]  
                        except :
                            raise Exception('as %s is a GenericForeignKey please specify the target type in the class field' % (property))  
                        attributes = [tmp] 
                        #replace nested objects 
                        new_object = self.store(entity, attributes)[0]
                        cache[property] = new_object
        return cache
    
    def reorder_from_sorteddict(self, dct1, dct2):
        pass
     
    def store(self, entity, objects, starting_point=True, connect_to_base=True):
        """Stores objects into the database."""
        pk_id = [k for k in entity._meta.fields if k.primary_key][0].name
        #some model properties
        fks = foreign_keys(entity)
        m2m = many_to_many_fields(entity)
        reverse_o2o = reverse_one_to_one_keys(entity)
        reverse_fks = reverse_foreign_keys(entity)
        reverse_m2m = reverse_many_to_many_fields(entity)
        generic_fks = generic_foreign_keys(entity)
        generic_rels = generic_relations(entity)
        subcls = subclasses(entity)
        tmp_aggregate = SortedDict()
        tmp_aggregate.update(m2m)
        tmp_aggregate.update(reverse_o2o)
        tmp_aggregate.update(reverse_fks)
        tmp_aggregate.update(reverse_m2m)
        tmp_aggregate.update(generic_rels)
        #store data contained in objects list
        created_objects = []
        for props in objects :
            class_name = props.__class__.__class__.__name__
            assert isinstance(props, dict) or (props.__class__.__name__ == 'Column') or (class_name == "ModelBase"), "objects must be a list of dictionaries or Column or ModelBase objects or ids."
            if class_name != "ModelBase" :
                if starting_point :
                    if (props.__class__.__name__ == 'Column') :
                        cleanup = True if not hasattr(props, '__cleanup__') else props.__cleanup__
                        tmp = props.dictionarize(cleanup=cleanup)
                    elif isinstance(props, dict) :
                        cleanup = True if not props.has_key('__cleanup__') else props['__cleanup__']
                        tmp = self.dictionarize(props, cleanup=cleanup)
                else :
                    tmp = props
                
                #reorder aggregate respecting props field order
                aggregate = SortedDict()
                for field in tmp :
                    if tmp_aggregate.has_key(field) :
                        aggregate[field] = tmp_aggregate[field]
                
                to_create = SortedDict()
                for field in aggregate :
                    if tmp.has_key(field) :
                        to_create[field] = tmp.pop(field)
                
                delegate = {}
                for field in subcls :
                    if tmp.has_key(field) :
                        delegate[field] = tmp.pop(field)
                assert len(delegate) < 2, "cannot derivate twice"
                
                #replace value of field corresponding to foreign keys by its relative object
                tmp = self.transform(tmp, fks, generic_fks, entity)
                logging.debug("Storing %s with properties %s" % (entity.__name__, props))
                if len(delegate) :
                    #delegate the creation to a subclass of entity
                    field, item = delegate.items()[0]
                    item.update(tmp)
                    child_entity = subcls[field]
                    new_object = self.store(child_entity, [item], starting_point=False)[0] 
                elif pk_id in tmp :
                    #the pk is specified in the dictionary i.e. get_or_create cannot be used
                    if tmp.has_key('force') :
                        force = tmp.pop('force')
                    else :
                        force = False
                    pk_val = tmp[pk_id]
                    obj_list = entity.objects.filter(pk=pk_val) 
                    if obj_list.count() :
                        if len(tmp) : 
                            new_object = obj_list.update(**tmp)
                        new_object = obj_list[0]
                    else :
                        new_object = entity.objects.create(**tmp)  
                else : 
                    if tmp.has_key('force') :
                        force = tmp.pop('force')
                    else :
                        force = False
                    #User is a special case because an encrypted password has to be specified
                    if (entity.__name__ == 'User') :
                        pwd_condition = tmp.has_key('password')
                        password = tmp.pop('password') if pwd_condition else None
                        created = True
                    if not len(generic_fks) :
                        if not force :
                            try :
                                new_object, created = entity.objects.get_or_create(**tmp)
                            except :
                                #get returns more than one instance
                                #i.e. an indetermination arises 
                                #because fields that are useful to 
                                #identify an object are not stored in tmp 
                                logging.header("impossible to identify the good object with %s = %s" % (entity.__name__, tmp))
                                new_object = entity.objects.create(**tmp)
                        else :
                            new_object = entity.objects.create(**tmp)
                    else :
                        new_dct = tmp.copy()
                        for gfk in generic_fks :
                            gfk_obj = new_dct.pop(gfk)
                            ct_field = generic_fks[gfk]['ct_field']
                            fk_field = generic_fks[gfk]['fk_field']
                            new_dct[ct_field] = ContentType.objects.get_for_model(gfk_obj)
                            new_dct[fk_field] = gfk_obj.pk
                        if not force :
                            objects = entity.objects.filter(**new_dct)
                            if objects.count() == 0 :
                                new_object = entity.objects.create(**new_dct)
                            elif objects.count() > 1 :
                                logging.header("impossible to identify the good object with %s = %s" % (entity.__name__, new_dct))
                                new_object = entity.objects.create(**new_dct)
                            elif objects.count() == 1 :
                                new_object = objects[0]
                        else :
                            new_object = entity.objects.create(**new_dct)
                    if (entity.__name__ == 'User') and created :
                        assert password, 'password must be specified for a User object'
                        new_object.set_password(password)
                        new_object.save()
                #attach link to the created object
                for field in aggregate :
                    if to_create.has_key(field) and to_create[field]:
                        if aggregate[field]['type'] == 'm2m' :
                            m2m_entity = aggregate[field]['class']
                            new_objects = self.store(m2m_entity, to_create[field], starting_point=False) 
                            getattr(new_object, field).add(*new_objects)
                        elif aggregate[field]['type'] == 'reverse_o2o' :
                            reverse_entity = aggregate[field]['class']
                            to_create[field].update({aggregate[field]['field']:new_object})
                            new_objects = self.store(reverse_entity, [to_create[field]], starting_point=False)
                        elif aggregate[field]['type'] == 'reverse_fk' :
                            reverse_entity = aggregate[field]['class']
                            for item in to_create[field] :
                                item.update({aggregate[field]['field']:new_object})
                            new_objects = self.store(reverse_entity, to_create[field], starting_point=False)
                        elif aggregate[field]['type'] == 'reverse_m2m' :
                            reverse_entity = aggregate[field]['class']
                            new_objects = self.store(reverse_entity, to_create[field], starting_point=False)
                            for obj in new_objects :
                                getattr(obj, aggregate[field]['field']).add(new_object)
                        elif aggregate[field]['type'] == 'generic_rel' :
                            reverse_entity = aggregate[field]['class']
                            for item in to_create[field] :
                                reverse_field = aggregate[field]['field']
                                if connect_to_base :
                                    link = entity.__name__
                                else :
                                    link = new_object.__class__.__name__
                                item.update({reverse_field:{'__target_class__':link, 'pk':new_object.pk}})
                            new_objects = self.store(reverse_entity, to_create[field], starting_point=False)      
            else :
                new_object = props           
            created_objects.append(new_object)
        return created_objects

class PopulateCommand(NoArgsCommand):
    """Base class that manages database population"""
    def __init__(self):
        super(PopulateCommand, self).__init__()
        self.populate = Populate()
    
    def handle_noargs(self, **options):
        logging.header('start %s' % self.help)
        for item in self.data :
            name = item['class']._meta.verbose_name_plural.lower()
            logging.header('start %s storage' % name)
            objects = self.populate.store(item['class'], item['objects'])
            if item.get('create_default_access_control') :
                for obj in objects : 
                    group = Group.objects.get(name="admin")
                    kwargs = {
                        'can_view':True,
                        'can_modify':True,
                        'can_delete':True,
                        'can_download':True,
                        'can_modify_permission':True
                    }
                    create_group_permission(obj, group, **kwargs)
            logging.header("%s stored in database" % name)
        logging.header('%s finished' % self.help)
