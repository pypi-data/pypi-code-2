#encoding:utf-8
from copy import copy, deepcopy
from datetime import datetime
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils.datastructures import SortedDict
from helmholtz.core.modules import application_classes,get_application_classes, get_model_class
from helmholtz.core.schema import subclasses_tree, regular_fields, foreign_keys, generic_relations, many_to_many_fields, reverse_many_to_many_fields, reverse_one_to_one_keys, reverse_foreign_keys, get_subclasses_recursively, get_parents_recursively
from helmholtz.access_control.dependencies import get_dependencies
from helmholtz.core.shortcuts import cast_object_to_leaf_class
from helmholtz.access_control.conditions import is_under_access_control
from helmholtz.access_control.filters import get_accessible_by

node_template = {'index':None,
                 'old_index':None, #useful for AdminWidget.map_old_state function
                 'class':None,
                 'id':None,
                 'db_object':None,
                 'parent':{'id':None,
                           'class':None,
                           'index':None},
                 'can_create':[],
                 'can_be_deleted':False,
                 'can_be_updated':False,
                 'title':{'human_readable':None,
                          'original':None},
                 'value':None,
                 'type':None,
                 'state':None,
                 'table':None,
                 'node':None,
                 'object':None,
                }

constraints_template = {'excluded_fields':[],
                        'actions':[],
                        'properties':[],
                        'links':{},
                        'table':{},
                        'form':None,
                        'queryset':{},
                        'order_by':[],
                        'ordering':None,
                        'shunt':None,
                        'limit_to_one_subclass':False,
                        'display_base_class_only':False,
                        'display_base_class':False,
                        'excluded_subclasses':list()
                        #'expansion':[]
                       }

def compress_hierarchy(hierarchy, compression=None, path=None, starting_point=True):
    if starting_point :
        compression = SortedDict()
        
    for item in hierarchy :
        if starting_point :
            new_path = item
        else :
            new_path = '%s.%s' % (path, item)
        if isinstance(hierarchy[item], dict) and (not hierarchy[item].has_key('classes')) and (len(hierarchy[item]) < 2) :
            compress_hierarchy(hierarchy[item], compression, new_path, False)
        else :
            compression[new_path] = copy(hierarchy[item])
    
    if starting_point :
        return compression

def get_class_hierarchy(project_name=settings.PROJECT_NAME, modules_filter=None, foreign_models=True, classes_filter=None, shunt_models=True, order_filter=None, compress=False, extra_content=False, user=None):
    """Hierarchical organisation of modules and their relative classes."""
    hierarchy = SortedDict()
    classes = get_application_classes(project_name, modules_filter, classes_filter)
    if order_filter :
        order_key = lambda x:[k[1] for k in order_filter if (k[0] == (x.__module__ + '.' + x.__name__))][0]
        ord = order_key(classes[0])
        classes.sort(key=order_key)
    for cls in classes :
        splitted_modules = cls.__module__.split('.')
        node = hierarchy
        for item in splitted_modules :
            if shunt_models and (item != 'models') :
                if not node.has_key(item) :
                    node[item] = SortedDict()
                node = node[item]
        #find constraints useful to know what to display
        if order_filter :
            for index in xrange(0, len(order_filter)) :
                if order_filter[index][0] == cls.__module__ + '.' + cls.__name__ :
                    break
                else :
                    continue
            constraints = order_filter[index][2]
        else :
            constraints = None
        if not node.has_key('classes') :
            node['classes'] = SortedDict()
        node['classes'][cls.__name__] = dict()
        node['classes'][cls.__name__] = {'class':cls, 'constraints':constraints}
        if constraints :
            node['classes'][cls.__name__]['objects'] = HierarchicView(cls.__name__, cls.__module__, select_foreign_models=True, constraints={cls.__name__:{'constraints':constraints}}, extra_content=extra_content, user=user)
            node['classes'][cls.__name__]['dependent_classes'] = node['classes'][cls.__name__]['objects'].hierarchy['dependent_classes']
    
    if compress :
        hierarchy = compress_hierarchy(hierarchy)
    return hierarchy 

def get_menu_hierarchy(sections, project_name=settings.PROJECT_NAME, modules_filter=None, foreign_models=True, classes_filter=None, order_filter=None, extra_content=False, user=None):
    """Hierarchical organisation of modules and their relative classes."""
    hierarchy = SortedDict()
    classes = get_application_classes(project_name, modules_filter, classes_filter)
    if order_filter :
        order_key = lambda x:[k[1] for k in order_filter if (k[0] == (x.__module__ + '.' + x.__name__))][0]
        ord = order_key(classes[0])
        classes.sort(key=order_key)
    
    for cls in classes :
        transform = [(k[2], k[3], k[4]) for k in order_filter if (k[0] == cls.__module__ + '.' + cls.__name__)][0]
        #find constraints useful to know what to display
        if order_filter :
            constraints = transform[0] #[k for k in order_filter if (k[0] == cls.__module__ + '.' + cls.__name__)][0][2]
        else :
            constraints = None
        is_class = transform[2]
        if not is_class :
            section = transform[1]
            splitted_sections = section.split('.')
            node = hierarchy
            for item in splitted_sections :
                if not node.has_key(item) :
                    node[item] = SortedDict()
                    node[item]['modules'] = SortedDict()
                class_container = node[item]
                node = node[item]['modules']

            if not class_container.has_key('classes') :
                class_container['classes'] = SortedDict()
                
            class_container['classes'][cls.__name__] = dict()
            class_container['classes'][cls.__name__] = {'class':cls, 'constraints':constraints}
            if constraints :
                class_container['classes'][cls.__name__]['objects'] = HierarchicView(cls.__name__, cls.__module__, select_foreign_models=True, constraints={cls.__name__:{'constraints':constraints}}, extra_content=extra_content, user=user)
                class_container['classes'][cls.__name__]['dependent_classes'] = class_container['classes'][cls.__name__]['objects'].hierarchy['dependent_classes']
        else :
            hierarchy[cls.__name__] = {'class':cls, 'constraints':constraints}
            if constraints :
                hierarchy[cls.__name__]['objects'] = HierarchicView(cls.__name__, cls.__module__, select_foreign_models=True, constraints={cls.__name__:{'constraints':constraints}}, extra_content=extra_content, user=user)
                hierarchy[cls.__name__]['dependent_classes'] = hierarchy[cls.__name__]['objects'].hierarchy['dependent_classes']
    return hierarchy 

class HierarchicView(object):
    
    def __init__(self, cls, package, foreign_apps=None, select_foreign_models=True, constraints=None, recursive=True, extra_content=False, complete_constraints=True, user=None, hierarchy=None):
        self.class_cache = application_classes#see later if a cache is necessary to improve performances
        self.cls = get_model_class(package, cls)
        self.user = user
        self.application = [k for k in settings.INSTALLED_APPS if k in self.cls.__module__][0]
        self.foreign_apps = foreign_apps
        self.select_foreign_models = select_foreign_models
        self.extra_content = extra_content
        assert (not constraints) or ((len(constraints) == 1) and constraints.has_key(self.cls.__name__)), "constraints defined like {'Entity_Name':{...}}"
        self.constraints = constraints
        if complete_constraints :
            self.complete_constraints()
            self.complete_subclasses()
        self.skeleton = self.create_skeleton(self.cls, constraints)
        self.recursive = recursive
        if not hierarchy :
            self.hierarchy = self.create_hierarchy(recursive=False)
        else :
            self.hierarchy = hierarchy
    
    def complete_constraints(self, constraints=None, starting_point=True, subcls=None):
        """Put dummy links, excluded_fields, properties and order fields..."""
        if starting_point :
            constraints = self.constraints

        for constraint in constraints :
            if not constraints[constraint].has_key('module') :
                constraints[constraint]['module'] = None    
            delegate = constraints[constraint]['constraints']
            if not delegate.has_key('display_base_class') :
                delegate['display_base_class'] = False
            if not delegate.has_key('display_base_class_only') :
                delegate['display_base_class_only'] = False
            if not delegate.has_key('limit_to_one_subclass') :
                delegate['limit_to_one_subclass'] = False
            if not delegate.has_key('form') :
                delegate['form'] = None
            if not delegate.has_key('shunt') :
                delegate['shunt'] = None
            if not delegate.has_key('actions') :
                delegate['actions'] = []
            if not delegate.has_key('links') :
                delegate['links'] = {}
            if not delegate.has_key('queryset') :
                delegate['queryset'] = {}
            else :
                if not delegate['queryset'].has_key('hierarchy') :
                    delegate['queryset']['hierarchy'] = False
                if not delegate['queryset'].has_key('querydict') :
                    delegate['queryset']['querydict'] = {}     
            if not delegate.has_key('excluded_subclasses') :
                delegate['excluded_subclasses'] = list()
            if not delegate.has_key('excluded_fields') :
                delegate['excluded_fields'] = [] 
            if not delegate.has_key('order_by') :
                delegate['order_by'] = None
            if not delegate.has_key('ordering') :
                delegate['ordering'] = None
            if not delegate.has_key('properties') :
                delegate['properties'] = []
            if not delegate.has_key('table') : 
                delegate['table'] = {} 
            else :
                if not delegate['table'].has_key('expansion') :
                    delegate['table']['expansion'] = []
                if not delegate['table'].has_key('pagination') :
                    delegate['table']['pagination'] = 50
                if not delegate['table'].has_key('fields') :
                    delegate['table']['fields'] = []
                if not delegate['table'].has_key('length') :
                    delegate['table']['length'] = None
                if not delegate['table'].has_key('width') :
                    delegate['table']['width'] = None
            #complete constraints with subclasses  
            cls = self.cls if starting_point else self.get_class(constraint, constraints)
            subclasses = [k for k in get_subclasses_recursively(cls, strict=True)]# if not k.__name__ in delegate['excluded_subclasses']]
            for subclass in subclasses :
                if not subclass.__name__ in delegate['links'] :
                    delegate['links'][subclass.__name__] = dict()
                    delegate['links'][subclass.__name__]['constraints'] = dict()
            #copy in subclasses constraints constraint of the main node
            if delegate['links'] :
                self.complete_constraints(delegate['links'], False)
#            for subclass in subclasses :
#                source = delegate
#                destination = deepcopy(delegate['links'][subclass.__name__]['constraints'])
#                self.extend_with_parent_constraints(cls,subclass,source,destination)
#                delegate['links'][subclass.__name__]['constraints'] = deepcopy(destination)
        if starting_point :
            return
    
    def complete_subclasses(self, constraints=None, starting_point=True):
        if starting_point :
            constraints = self.constraints

        for constraint in constraints :  
            delegate = constraints[constraint]['constraints']
            #complete constraints with subclasses        
            cls = self.cls if starting_point else self.get_class(constraint, constraints)
            subclasses = [k for k in get_subclasses_recursively(cls, strict=True)]# if not k.__name__ in delegate['excluded_subclasses']]
            for subclass in subclasses :
                source = delegate
                destination = deepcopy(delegate['links'][subclass.__name__]['constraints'])
                self.extend_with_parent_constraints(cls, subclass, source, destination)
                delegate['links'][subclass.__name__]['constraints'] = deepcopy(destination)
            if delegate['links'] :
                self.complete_subclasses(delegate['links'], False)
                 
        if starting_point :
            return
    
    def get_class(self, class_name, constraints):
        if (self.cls.__name__ == class_name) :
            candidate = self.cls
        else :
            candidates = [k for k in self.class_cache if (k.__name__ == class_name)]
            assert candidates, "cannot find any candidate classes"
            if len(candidates) > 1 :
                if not constraints[class_name].has_key('module') :
                    raise Exception('please specify the module of the class %s' % (class_name))
                else :
                    module = constraints[class_name]['module']
                    candidates = [k for k in candidates if (k.__module__ == module)]
                    assert candidates, "cannot find class %s in module %s" % (class_name, module)
                    candidate = candidates[0]
            else :
                candidate = candidates[0]
        return candidate
    
    def complete_skeleton_with_subclasses(self, subclasses, skeleton, path, starting_point=True):
        #extend default skeleton with subclasses  
        if subclasses :
            for subclass in subclasses :
                subclass_path = copy(path)
                subclass_path.append(subclass)
                self.complete_skeleton_with_subclasses(subclass.__subclasses__(), skeleton, subclass_path, False)
        else :
            skeleton.append(path)
    
    def create_skeleton(self, cls, constraints, skeleton=None, path=None, starting_point=True):
        #init skeleton
        if starting_point :
            skeleton = list()
            path = [cls]
        
        #create each path of the skeleton
        for class_name in constraints :
            delegate_constraints = constraints[class_name]['constraints']
            if starting_point :
                new_path = path
                delegate_class = cls
            else :
                new_path = copy(path)
                delegate_class = self.get_class(class_name, constraints)  
                new_path.append(delegate_class)   
            if delegate_constraints['links'] :
                self.create_skeleton(delegate_class, delegate_constraints['links'], skeleton, new_path, False)
            else :
                skeleton.append(new_path) 
            #subclasses = delegate_class.__subclasses__()
            #self.complete_skeleton_with_subclasses(subclasses,skeleton,path)                           

        if starting_point :
            return skeleton
    
    def is_local_field(self, parent, child):
        local = [k.name for k in parent._meta.fields if hasattr(k.rel, 'to') and (k.rel.to == child)]
        many_to_many = [k.name for k in parent._meta.local_many_to_many if hasattr(k.rel, 'to') and (k.rel.to == child)]
        return bool(local) or bool(many_to_many)
    
    def is_in_skeleton(self, path):
        """Tell if a path is a sub part of the skeleton.""" 
        #candidates = [k for k in self.skeleton if set(path).issubset(set(k)) and (len(path) == len(k))] 
        candidates = [k for k in self.skeleton if set(path).issubset(set(k))] 
        return (not bool(self.skeleton)) or (len(candidates) > 0)
    
    def extend_with_parent_properties(self, source, destination):
        """When an inheritance relation is discovered, store the parent properties into the child."""
        for field in ['dependent_classes', 'foreign_keys', 'many_to_many_fields', 'generic_relations', 'reverse_foreign_keys', 'reverse_one_to_one_keys', 'reverse_many_to_many_fields'] :
            if source.has_key(field):
                if not field in destination :
                    destination[field] = SortedDict()
                for attr in source[field] :
                    if not (attr in destination[field]) :
                        destination[field][attr] = deepcopy(source[field][attr])
    
    def extend_with_parent_constraints(self, cls, subclass, source, destination):
##        copy links of the super class
##        and remove fields that corresponding to subclasses
#        destination['links'].update(source['links'])
#        subclasses = cls.__subclasses__() #get_subclasses_recursively(cls)
#        for subcls in subclasses :
#            if destination['links'].has_key(subcls.__name__) :
#                tmp = destination['links'].pop(subcls.__name__)
#                if subcls == subclass :
#                    destination['table'] = tmp['constraints']['table']  
#        #remove classes not hierarchically specified
#        for subcls in get_subclasses_recursively(cls):
#            if not (subcls in subclasses) and destination['links'].has_key(subcls.__name__) :
#                destination['links'].pop(subcls.__name__)
        base_class = get_parents_recursively(subclass)[-1]
        subclasses = get_subclasses_recursively(subclass)
        subclass_names = [k.__name__ for k in subclasses]
        base_subclass_names = [k.__name__ for k in get_subclasses_recursively(base_class)]
        #complete with node that are not subclasses of the base class
        for link in source['links'] :
            in_base_subclasses = (link in base_subclass_names)
            if (not in_base_subclasses) :
                destination['links'][link] = source['links'][link]
        for link in source['links'] :
            in_subclasses = (link in subclass_names)
            if in_subclasses :
                destination['links'][link] = source['links'][link]
#                new_source = destination
#                new_destination = destination['links'][link]['constraints']
#                new_subclass = [k for k in subclasses if k.__name__ == link][0] 
#                self.extend_with_parent_constraints(subclass,new_subclass,new_source,new_destination)
        
        #copy other fields
        fields = ['excluded_fields', 'properties', 'actions']
        for field in fields :
            filtered = [k for k in source[field] if k not in destination[field]]
            destination[field].extend(filtered) 
        destination['display_base_class_only'] = source['display_base_class_only']
        if destination['order_by'] is None :
            destination['order_by'] = source['order_by']
        if destination['ordering'] is None :
            destination['ordering'] = source['ordering']
        if destination['shunt'] is None :
            destination['shunt'] = source['shunt']
        if destination['form'] is None :
            destination['form'] = source['form']
        #copy table description
        if source['table'] :
            if not destination['table'].has_key('pagination') :
                destination['table']['pagination'] = source['table']['pagination'] 
            if not destination['table'].has_key('width') :
                destination['table']['width'] = source['table']['width'] 
            if not destination['table'].has_key('length') :
                destination['table']['length'] = source['table']['length']
            if not destination['table'].has_key('pagination') :
                destination['table']['pagination'] = source['table']['pagination'] 
            if destination['table'].has_key('fields') :
                filtered = [k for k in source['table']['fields'] if k not in destination['table']['fields']]
                destination['table']['fields'].extend(filtered)
            else :
                filtered = [k for k in source['table']['fields']]
                destination['table']['fields'] = filtered
            if destination['table'].has_key('expansion') :
                filtered = [k for k in source['table']['expansion'] if k not in destination['table']['expansion']]
                destination['table']['expansion'].extend(filtered)
            else :
                filtered = [k for k in source['table']['expansion']]
                destination['table']['expansion'] = filtered
                   
    def _get_keys(self, cls, function, key_name, entry_point, path, starting_point=True, recursive=True, constraints=None):
        keys = function(cls)
        tmp = SortedDict()
        excluded_fields = constraints['excluded_fields'] 
        links = constraints['links']
        properties = constraints['properties']
        
        for attr in keys : 
            if (not excluded_fields) or not (attr in excluded_fields) : 
                new_cls = keys[attr]['class']
                subclass_condition = (new_cls != cls) and issubclass(new_cls, cls)   
                is_in_installed_apps = len([k for k in settings.INSTALLED_APPS if (new_cls.__module__.startswith(k))]) > 0
                parent_condition = (new_cls == cls) and (path.count(cls) < 2)
                in_path_condition = not (new_cls in path)
                key_names = ['foreign_keys', 'many_to_many_fields']
                if (in_path_condition or subclass_condition or parent_condition or (key_name in ['many_to_many_fields'])) and recursive and is_in_installed_apps :  
                    new_path = copy(path)
                    new_path.append(new_cls)
                    in_skeleton = self.is_in_skeleton(new_path) 
                    if in_skeleton or (not in_skeleton and parent_condition) or (not in_skeleton and subclass_condition) or (not in_skeleton and (key_name in key_names)) :
                        #avoid the recursion into other applications, 
                        #in fact it goes into the application but it limits 
                        #the recursion to the first reached class to know 
                        #about the foreign class representation
                        
                        force_recursion = True
                        select_all_foreign_models = self.select_foreign_models and not bool(self.foreign_apps)
                        select_specified_foreign_modules = bool(self.foreign_apps) and (len([k for k in self.foreign_apps if (new_cls.__module__.startswith(k))]) > 0)  
                        is_in_module = new_cls.__module__.startswith(self.application)
                        if not (select_all_foreign_models or select_specified_foreign_modules or is_in_module) or parent_condition or ((not in_skeleton) and (key_name in key_names) and not new_cls.__subclasses__()) : #
                            force_recursion = False
                        new_entry_point = SortedDict()
                        #keep the base class properties
#                        if (function == subclasses_tree) and in_skeleton and subclass_condition :
#                            self.extend_with_parent_properties(entry_point,new_entry_point)   
                        if not subclass_condition :
                            new_constraints = dict()
                            if parent_condition :
                                if new_cls.__name__ in constraints['links'] :
                                    new_constraints = constraints['links'][new_cls.__name__]['constraints']
                                else :
                                    new_constraints = constraints
                            elif links and links.has_key(new_cls.__name__) :
                                new_constraints = deepcopy(links[new_cls.__name__]['constraints'])
                            else :
                                new_constraints = deepcopy(constraints_template)      
                        else :
                            if in_skeleton :    
                                if not new_cls.__name__ in links :
                                    new_constraints = deepcopy(constraints_template)
                                    self.extend_with_parent_constraints(cls, new_cls, constraints, new_constraints)
                                else :
                                    new_constraints = constraints['links'][new_cls.__name__]['constraints']          
                            else :
                                new_constraints = constraints
                            
                        self.create_hierarchy(new_cls, new_entry_point, new_path, False, force_recursion, new_constraints)#new_excluded_fields,new_links,new_properties)
                        if new_entry_point :
                            keys[attr].update(new_entry_point) 
                            tmp[attr] = keys[attr]
        if tmp :
            #update with base class properties
            if entry_point.has_key(key_name) :
                entry_point[key_name].update(tmp)
            else :
                entry_point[key_name] = tmp
    
    def create_hierarchy(self, cls=None, entry_point=None, path=None, starting_point=True, recursive=True, constraints=None):
        if starting_point :
            cls = self.cls
            path = [self.cls]
            entry_point = SortedDict()
            recursive = self.recursive
            constraints = self.constraints[self.cls.__name__]['constraints']
        excluded_fields = constraints['excluded_fields'] 
        properties = constraints['properties']
#            
        #regular fields
        entry_point['fields'] = regular_fields(cls, True)  
        #pop fields that are in excluded fields   
        if excluded_fields :  
            for field in excluded_fields :
                if field in entry_point['fields'] :
                    index = entry_point['fields'].index(field)
                    entry_point['fields'].pop(index)
        if properties :
            if not entry_point.has_key('properties') :
                entry_point['properties'] = properties    
            else :
                for prop in properties :
                    if not prop in entry_point['properties'] :
                        entry_point['properties'][prop] = deepcopy(properties[prop])
        
        #necessary to memorize dependencies between classes
        #without skeleton limitation
        entry_point['dependent_classes'] = get_dependencies(cls)
        #foreign keys
        self._get_keys(cls, foreign_keys, 'foreign_keys', entry_point, path, False, recursive, constraints)
        #many to many fields
        self._get_keys(cls, many_to_many_fields, 'many_to_many_fields', entry_point, path, False, recursive, constraints)
        #reverse keys
        self._get_keys(cls, generic_relations, 'generic_relations', entry_point, path, False, recursive, constraints)
        self._get_keys(cls, reverse_foreign_keys, 'reverse_foreign_keys', entry_point, path, False, recursive, constraints)
        self._get_keys(cls, reverse_one_to_one_keys, 'reverse_one_to_one_keys', entry_point, path, False, recursive, constraints)
        self._get_keys(cls, reverse_many_to_many_fields, 'reverse_many_to_many_fields', entry_point, path, False, recursive, constraints)
        #subclasses
        self._get_keys(cls, subclasses_tree, 'subclasses', entry_point, path, False, recursive, constraints)
                
        if starting_point :
            return entry_point
    
    def _format_subclasses(self, node, dct=None, starting_point=True, base_class=True, excluded_subclasses=None):
        """Create a dictionary where keys are subclasses names.""" 
        if starting_point :
            dct = SortedDict()
        for subcls in node['subclasses'] :
            #do not considered subclasses stored in excluded_subclasses
            if not excluded_subclasses or not (subcls in excluded_subclasses) :
                dct[subcls] = {'content':list()}
            if node['subclasses'][subcls].has_key('subclasses') :
                self._format_subclasses(node['subclasses'][subcls], dct, False, excluded_subclasses=excluded_subclasses)
        if starting_point :
            if base_class :
                dct.update({node['class'].__name__.lower():{'content':list()}})
            return dct
    
    def _replace_values(self, obj, hierarchy, node):
        result = SortedDict()
        for field in hierarchy[node] :
            value = getattr(obj, field)
            result[field] = {'content':value}
            if self.extra_content :
                extra = deepcopy(node_template)
                extra['parent']['id'] = obj.pk
                extra['parent']['class'] = obj.__class__.__name__
                extra['title']['human_readable'] = obj._meta.get_field_by_name(field)[0].verbose_name.lower()
                extra['title']['original'] = field
                if (not value) or (value is None) :
                    extra['value'] = 'N.D' if not type(value) in [int, float, long] else 0
                elif isinstance(value, datetime) :
                    extra['value'] = value.__str__().split('.')[0]  
                else :
                    extra['value'] = value if not hasattr(obj, 'get_%s_display' % field) else getattr(obj, 'get_%s_display' % field)()
                extra['type'] = 'leaf'
                extra['object'] = 'value'
                extra['state'] = 'closed'
                if value.__class__.__name__ == 'ImageFieldFile' :
                    extra['class'] = 'ImageFieldFile'
                result[field]['extra_content'] = extra
        return result
    
    def _replace_properties(self, obj, hierarchy, node):
        result = SortedDict()
        for field in hierarchy[node] :
            assert isinstance(field, tuple)
            splitted_property = field[0].split('.')
            if len(splitted_property) < 2 :
                try :
                    obj_attr = getattr(obj, field[0])    
                except :
                    obj_attr = None
            else :
                try :
                    obj_attr = getattr(obj, splitted_property[0])
                    for property in splitted_property[1:] :
                        if callable(obj_attr) :
                            obj_attr = obj_attr()
                        if not (obj_attr is None) : 
                            try : 
                                obj_attr = getattr(obj_attr, property)
                            except :
                                obj_attr = None
                        else :
                            break
                except :
                    obj_attr = None
            
            if callable(obj_attr) :
                value = obj_attr()
            else :
                value = obj_attr  

            result[field] = {'content':value}

            if self.extra_content :
                extra = deepcopy(node_template)
                extra['parent']['id'] = obj.pk
                extra['parent']['class'] = obj.__class__.__name__
                extra['title']['human_readable'] = field[1]
                extra['title']['original'] = field[0]
                if (not value) or (value is None) :
                    extra['value'] = 'N.D' if not type(value) in [int, float, long] else 0
                else :
                    extra['value'] = value
                extra['type'] = 'leaf'
                extra['object'] = 'property'
                extra['state'] = 'closed'
                result[field]['extra_content'] = extra
        return result
    
    def _replace_single_links(self, obj, hierarchy, node, path, constraints=None):
        #for a link to another object
        result = SortedDict()
        for field in hierarchy[node] :
            child_obj = getattr(obj, field)
            cast = cast_object_to_leaf_class(child_obj)
            if child_obj.__class__.__name__ in constraints['links'] :
                parent_constraints = constraints['links'][child_obj.__class__.__name__]['constraints']
                if cast.__class__.__name__ in parent_constraints['links'] : 
                    force_shunt = parent_constraints['links'][cast.__class__.__name__]['constraints']['shunt']
                else :
                    force_shunt = parent_constraints['shunt']       
            else :
                force_shunt = False
            if force_shunt :
                result[field] = {'content':cast}
            elif child_obj :
                result[field] = dict()
                result[field]['content'] = self.hierarchic_representation(child_obj, hierarchy[node][field], path, False, constraints=constraints)
            else :
                result[field] = {'content':None}   
            if self.extra_content :
                extra = deepcopy(node_template)
                #extra['db_object'] = child_obj
                extra['parent']['id'] = obj.pk
                extra['parent']['class'] = obj.__class__.__name__
                extra['state'] = 'closed'
                #human readable title is defined in the verbose_name parameter of the object class field for foreign keys
                #but for reverse one to one fields it is stored in the Meta of the class 
                if 'foreign_keys' in node :
                    extra['object'] = 'fkey' 
                    extra['title']['human_readable'] = obj._meta.get_field_by_name(field)[0].verbose_name.lower()
                else :
                    extra['object'] = 'link'
                    extra['title']['human_readable'] = hierarchy[node][field]['class']._meta.verbose_name.lower()
                extra['title']['original'] = field
                if child_obj :
                    cls = cast.__class__
                    extra['class'] = cls.__name__
                    extra['db_object'] = cast
                    extra['can_be_deleted'] = True
                    extra['can_be_updated'] = True
                    extra['id'] = child_obj.pk
                    extra['can_create'] = [k.__name__ for k in get_subclasses_recursively(child_obj.__class__, strict=False)] 
                    has_subclasses = (len(extra['can_create']) > 1)
                    if force_shunt :
                        extra['type'] = 'leaf'
                        extra['value'] = cast.__unicode__() 
                    elif not isinstance(result[field]['content'], dict) :
                        extra['type'] = 'leaf'
                        extra['value'] = result[field]['content'].__unicode__() 
                    else :
                        extra['type'] = 'group'
                        extra['value'] = cast.__unicode__()
                else :
                    cls = hierarchy[node][field]['class']
                    extra['class'] = cls.__name__
                    extra['can_be_deleted'] = False
                    extra['can_be_updated'] = False
                    extra['id'] = None
                    extra['type'] = 'leaf'
                    extra['value'] = 'N.D'   
                    extra['db_object'] = cls 
                    extra['can_create'] = [k.__name__ for k in get_subclasses_recursively(cls, strict=False)]                         
                if constraints and constraints.has_key('links') and (extra['class'] in constraints['links']) :
                    extra['node'] = constraints['links'][extra['class']]
                    extra['node']['dependent_classes'] = hierarchy[node][field]['dependent_classes']
                    extra['node']['class'] = cls
                else :
                    extra['node'] = SortedDict()
                    extra['node']['class'] = cls
                    extra['node']['constraints'] = deepcopy(constraints_template)
                    extra['node']['dependent_classes'] = hierarchy[node][field]['dependent_classes']
                #extra['node']['objects'] = HierarchicView(extra['class'],extra['node']['class'].__module__,select_foreign_models=True,constraints={cls.__name__:{'constraints':extra['node']['constraints']}},extra_content=True,complete_constraints=False,user=self.user)     
                result[field]['extra_content'] = extra
        return result
    
    def _replace_reverse_single_links(self, obj, hierarchy, node, path, constraints=None):
        #for a reverse link to another object
        result = SortedDict()
        for field in hierarchy[node] :
            try :
                child_obj = getattr(obj, field)
                cast = cast_object_to_leaf_class(child_obj)
                if child_obj.__class__.__name__ in constraints['links'] :
                    parent_constraints = constraints['links'][child_obj.__class__.__name__]['constraints']
                    if cast.__class__.__name__ in parent_constraints['links'] : 
                        force_shunt = parent_constraints['links'][cast.__class__.__name__]['constraints']['shunt']
                    else :
                        force_shunt = parent_constraints['shunt']       
                else :
                    force_shunt = False
                if force_shunt :
                    result[field] = {'content':cast}
                else :
                    result[field] = dict()
                    result[field]['content'] = self.hierarchic_representation(child_obj, hierarchy[node][field], path, False, constraints=constraints)
            except ObjectDoesNotExist, e:
                child_obj = None
                result[field] = {'content':None}    
            if self.extra_content :
                extra = deepcopy(node_template)
                #extra['db_object'] = child_obj
                extra['parent']['id'] = obj.pk
                extra['parent']['class'] = obj.__class__.__name__
                extra['state'] = 'closed'
                #human readable title is defined in the verbose_name parameter of the object class field for foreign keys
                #but for reverse one to one fields it is stored in the Meta of the class 
                if 'foreign_keys' in node :
                    extra['object'] = 'fkey'
                    extra['title']['human_readable'] = obj._meta.get_field_by_name(field)[0].verbose_name.lower()
                else :
                    extra['object'] = 'link'
                    #extra['title']['human_readable'] = hierarchy[node][field]['class']._meta.verbose_name.lower()
                    extra['title']['human_readable'] = obj._meta.get_field_by_name(field)[0].field.rel.related_name
                extra['title']['original'] = field
                
                if child_obj :
                    cls = cast.__class__
                    extra['class'] = cls.__name__
                    extra['db_object'] = cast
                    extra['can_be_deleted'] = True
                    extra['can_be_updated'] = True
                    extra['id'] = child_obj.pk
                    extra['can_create'] = [k.__name__ for k in get_subclasses_recursively(child_obj.__class__, strict=False)] 
                    has_subclasses = (len(extra['can_create']) > 1)
                    if force_shunt :
                        extra['type'] = 'leaf'
                        extra['value'] = cast.__unicode__() 
                    elif not isinstance(result[field]['content'], dict) :
                        extra['type'] = 'leaf'
                        extra['value'] = result[field]['content'].__unicode__() 
                    else :
                        extra['type'] = 'group'
                        extra['value'] = cast.__unicode__()
                else :
                    cls = hierarchy[node][field]['class']
                    extra['class'] = cls.__name__
                    extra['can_be_deleted'] = False
                    extra['can_be_updated'] = False
                    extra['id'] = None
                    extra['type'] = 'leaf'
                    extra['value'] = 'N.D'   
                    extra['db_object'] = cls 
                    extra['can_create'] = [k.__name__ for k in get_subclasses_recursively(cls, strict=False)]                     
                      
                if constraints and constraints.has_key('links') and (extra['class'] in constraints['links']) :
                    extra['node'] = constraints['links'][extra['class']]
                    extra['node']['dependent_classes'] = hierarchy[node][field]['dependent_classes']
                    extra['node']['class'] = cls
                else :
                    extra['node'] = SortedDict()
                    extra['node']['class'] = cls
                    extra['node']['constraints'] = deepcopy(constraints_template)
                    extra['node']['dependent_classes'] = hierarchy[node][field]['dependent_classes']
                #extra['node']['objects'] = HierarchicView(extra['class'],extra['node']['class'].__module__,select_foreign_models=True,constraints={cls.__name__:{'constraints':extra['node']['constraints']}},extra_content=True,complete_constraints=False,user=self.user)          
                result[field]['extra_content'] = extra
        return result
    
    def _replace_with_objects(self, obj, obj_set, hierarchy, node, field, path, constraints=None, table=None):
        result = SortedDict()
        tmp_lst = list()
        #objects = obj_set.get_accessible_objects(self.user) if (settings.ACCESS_CONTROL and isinstance(obj_set,AccessControlManager)) else obj_set.all()
        display_base_class_only = constraints['links'][obj_set.model.__name__]['constraints']['display_base_class_only'] if obj_set.model.__name__ in constraints['links'] else False
        force_shunt = constraints['links'][obj_set.model.__name__]['constraints']['shunt'] if obj_set.model.__name__ in constraints['links'] else False
        for child_obj in obj_set :
            if force_shunt :
                content = {'content':child_obj} 
                new_constraints = deepcopy(constraints_template)
            else :
                #a field that is a link to the object class itself is a special case
                #i.e. all the hierarchy has to be browsed the same way as the parent node
                is_link_to_itself = (child_obj.__class__.__name__ == obj.__class__.__name__) 
                if not is_link_to_itself :
                    new_constraints = constraints['links'][child_obj.__class__.__name__]['constraints'] if child_obj.__class__.__name__ in constraints['links'] else deepcopy(constraints_template)
                    tmp = self.hierarchic_representation(child_obj, hierarchy[node][field], path, False, constraints=new_constraints)
                else :
                    delegate = deepcopy(hierarchy)
                    delegate['class'] = child_obj.__class__
                    new_constraints = constraints
                    tmp = self.hierarchic_representation(child_obj, delegate, path, False, is_link_to_itself, constraints=new_constraints)         
                content = {'content':tmp if tmp else child_obj}      
            if self.extra_content :
                extra = deepcopy(node_template)
                if force_shunt :
                    extra['type'] = 'leaf' 
                    extra['object'] = 'link' 
                elif tmp and isinstance(tmp, dict) :
                    extra['type'] = 'group'
                    extra['object'] = 'link'
                else :
                    extra['type'] = 'leaf' 
                    extra['object'] = 'link'  
                extra['class'] = obj_set.model.__name__
                extra['id'] = child_obj.pk
                extra['db_object'] = child_obj if not display_base_class_only else cast_object_to_leaf_class(child_obj)
                extra['parent']['id'] = None#obj.pk
                extra['parent']['class'] = obj_set.model.__name__#obj.__class__.__name__ 
                extra['can_be_deleted'] = True
                extra['can_be_updated'] = True
                extra['title']['human_readable'] = extra['db_object'].__unicode__()
                extra['title']['original'] = extra['db_object'].__unicode__()
                #extra['object'] = 'link'
                extra['state'] = 'closed'
                extra['node'] = dict()
                extra['node']['constraints'] = new_constraints
                extra['node']['dependent_classes'] = hierarchy[node][field]['dependent_classes']
                #extra['table'] = extra['node']['constraints']['table']
                content['extra_content'] = extra#content[child_obj.__unicode__()]['extra_content'] = extra
            tmp_lst.append(content)   
        
        result[field] = {'content':tmp_lst} if tmp_lst else {'content':None} 
        return result
        
    def get_value(self, obj, order):
        splitted = order.split('__')
        attr = splitted[0]
        value = getattr(obj, attr)
        if len(splitted) > 1 :
            for attr in splitted[1:] :
                value = getattr(value, attr)
                if not value or value.__class__.__class__.__name__ == 'ModelBase' :
                    break
            raise Exception('test')
            return value
        else :
            return value
            
    def _restore_default_order(self, dct, subcls):
        content = dct[subcls]['content']
        extra_content = dct[subcls]['extra_content']
        default_order = extra_content['node']['class']._meta.ordering
        if default_order.startswith('-') :
            default_order = default_order[1:]
            ascending = False
        else :
            ascending = True
        content.sort(key=lambda x:self.getvalue(x['db_object'], default_order))
        if not ascending :
            content.reverse() 
    
    def _get_constraints(self, model, subclass, constraints):
        if not model.__name__ in constraints['links'] :
            parent_constraints = deepcopy(constraints_template)
        else :
            parent_constraints = constraints['links'][model.__name__]['constraints']
        links = parent_constraints['links']
        if (model.__name__ != subclass.__name__) :
            if subclass.__name__ in links :
                new_constraints = links[subclass.__name__]['constraints']                                   
            else :
                new_constraints = deepcopy(constraints_template)
            self.extend_with_parent_constraints(model, subclass, parent_constraints, new_constraints)  
        else :
            new_constraints = parent_constraints
        return new_constraints
    
    def _put_objects_in_relative_subclass(self, obj, obj_set, hierarchy, node, field, path, constraints=None, table=None):
        result = SortedDict() 
        base_class = False if not obj_set.model.__name__ in constraints['links'] else constraints['links'][obj_set.model.__name__]['constraints']['display_base_class']
        excluded_subclasses = constraints['links'][obj_set.model.__name__]['constraints']['excluded_subclasses']
        tmp_dct = self._format_subclasses(hierarchy[node][field], base_class=base_class, excluded_subclasses=[k.lower() for k in excluded_subclasses])
        #__subclasses__ represents only strict subclasses and not the class itself
#        subclasses = [k for k in obj_set.model.__subclasses__()]
        subclasses = [k for k in get_subclasses_recursively(obj_set.model, strict=True) if not (k.__name__ in excluded_subclasses)]
        if base_class :
            subclasses.append(obj_set.model) 
        pks = [k.pk for k in obj_set] 
        for subcls in subclasses :
            manager = subcls.objects
            children = manager.filter(pk__in=pks)
            if is_under_access_control(manager.model) :
                children = get_accessible_by(children, self.user)    
            if children :
                new_constraints = self._get_constraints(obj_set.model, subcls, constraints)
                for sub_obj in children :
                    if sub_obj.__class__ != obj_set.model :
                        entry_point = hierarchy[node][field]['subclasses']
                        parent_list = list(sub_obj._meta.get_base_chain(obj_set.model))
                        parent_list.reverse()
                        parent_list = parent_list[parent_list.index(obj_set.model):]
                        if parent_list and (sub_obj.__class__.__name__ != parent_list[0].__name__) :
                            for parent in  parent_list[1:] :
                                parent_name = parent.__name__.lower()
                                #the skeleton may not contain 'subclasses' field
                                entry_point = entry_point[parent_name]['subclasses']
                            new_entry_point = entry_point[sub_obj.__class__.__name__.lower()]
                        else :
                            new_entry_point = hierarchy[node][field]  
                    else :
                        new_entry_point = hierarchy[node][field]
                    force_shunt = new_constraints['shunt']
                    if force_shunt :
                        content = {'content':sub_obj}
                    else :
                        tmp = self.hierarchic_representation(sub_obj, new_entry_point, path, False, constraints=new_constraints)
                        content = {'content':tmp if tmp else sub_obj}
                    if self.extra_content :
                        extra = deepcopy(node_template)
                        if force_shunt :
                            extra['type'] = 'leaf'
                        elif not isinstance(tmp, dict) :
                            extra['type'] = 'leaf'
                        else :
                            extra['type'] = 'group'
                        extra['class'] = sub_obj.__class__.__name__
                        extra['id'] = sub_obj.pk
                        extra['db_object'] = sub_obj
                        extra['parent']['id'] = obj.pk
                        extra['parent']['class'] = obj.__class__.__name__ 
                        extra['can_be_deleted'] = True
                        extra['can_be_updated'] = True
                        extra['title']['human_readable'] = sub_obj.__unicode__()
                        extra['title']['original'] = sub_obj.__unicode__()
                        extra['object'] = 'link'
                        extra['state'] = 'closed'
                        extra['node'] = dict()
                        extra['node']['constraints'] = new_constraints
                        extra['node']['dependent_classes'] = hierarchy[node][field]['dependent_classes']
                        content['extra_content'] = extra#content[sub_obj.__unicode__()]['extra_content'] = extra    
                        tmp_dct[sub_obj.__class__.__name__.lower()]['content'].append(content)
        
        #extra content
        if self.extra_content :
            limit_choice = False if not obj_set.model.__name__ in constraints['links'] else constraints['links'][obj_set.model.__name__]['constraints']['limit_to_one_subclass']
            if limit_choice :
                all_subclasses = get_subclasses_recursively(obj_set.model, strict=False)
                selected_classes = list()
                for s in all_subclasses :
                    count = s.objects.filter(pk__in=pks).count()
                    if count :
                        selected_classes.append(s)
                selected_subclass = selected_classes[-1] if selected_classes else None
#                raise Exception('test')
                if selected_subclass :
                    cls_name = selected_subclass.__name__.lower()
                    old_dct = tmp_dct
                    tmp_dct = SortedDict()
                    tmp_dct[cls_name] = old_dct[cls_name]
            for cls in tmp_dct :
                extra = deepcopy(node_template)
                extra['type'] = 'group' if tmp_dct[cls]['content'] else 'leaf' 
                cls_obj = [k for k in get_subclasses_recursively(obj_set.model) if (k.__name__.lower() == cls)]
                if cls_obj :
                    cls_obj = cls_obj[0]
                else :
                    cls_obj = obj_set.model
                
                new_constraints = self._get_constraints(obj_set.model, cls_obj, constraints)
                extra['node'] = dict()
                extra['node']['constraints'] = new_constraints 
                extra['table'] = extra['node']['constraints']['table']
                extra['class'] = cls_obj.__name__
                extra['db_object'] = cls_obj
                extra['parent']['class'] = obj_set.model.__name__
                extra['can_create'] = [cls_obj.__name__]
                extra['title']['human_readable'] = cls_obj._meta.verbose_name_plural.lower()
                extra['title']['original'] = cls_obj.__name__.lower()
                extra['object'] = 'link_list'
                if limit_choice :
                    extra['state'] = 'opened'
                    extra['type'] = 'leaf'
                else :
                    extra['state'] = 'closed'
                extra['node']['class'] = cls_obj
                
                tmp = {extra['class']:{'constraints':new_constraints}}
                h = hierarchy[node][field]['subclasses']
                if not (cls in h) :
                    parents = get_parents_recursively(cls_obj)
                    parents.reverse()
                    #[cls_obj.__name__.lower()]
                    for parent in parents[1:] :
                        h = h[parent.__name__.lower()]['subclasses']    
                h = h[cls]
                extra['node']['objects'] = HierarchicView(extra['class'], extra['node']['class'].__module__, select_foreign_models=True, constraints=tmp, extra_content=True, complete_constraints=False, user=self.user, hierarchy=h)     
                extra['node']['dependent_classes'] = hierarchy[node][field]['dependent_classes'] 
                tmp_dct[cls]['extra_content'] = extra
        #cleanup before adding data to the tree
        #reorder objects because obj_set default order doesn't match with subclass one
        count_none = 0
        if tmp_dct :
            for subcls in tmp_dct :
                if not tmp_dct[subcls]['content'] :
                    tmp_dct[subcls]['content'] = None
                    tmp_dct[subcls]['extra_content']['value'] = 'None'
                    count_none += 1
            if count_none != len(tmp_dct) :
                result[field] = {'content':tmp_dct}
            else :
                result[field] = {'content':tmp_dct}
        else :
            result[field] = {'content':None}
        return result
        
    def _replace_multiple_links(self, obj, hierarchy, node, path, constraints=None):  
        #for a list of objects      
        result = SortedDict()
        for field in hierarchy[node] :
            manager = getattr(obj, field)
            #reorder list respecting constraints
            if constraints['links'].has_key(manager.model.__name__) :
                order_by = constraints['links'][manager.model.__name__]['constraints']['order_by']
                if order_by :
                    obj_set = manager.order_by(*order_by)
                else :
                    obj_set = manager.all()
            else :
                obj_set = manager.all()
            if is_under_access_control(manager.model) :
                obj_set = get_accessible_by(obj_set, self.user)
            condition = hierarchy[node][field].has_key('subclasses') and (manager.model.__name__ in constraints['links']) and not constraints['links'][manager.model.__name__]['constraints']['display_base_class_only'] 
            if not condition :
                result.update(self._replace_with_objects(obj, obj_set, hierarchy, node, field, path, constraints=constraints))   
            else :
                result.update(self._put_objects_in_relative_subclass(obj, obj_set, hierarchy, node, field, path, constraints=constraints))
            #extra content
            if self.extra_content :
                extra = deepcopy(node_template)
                extra['title']['human_readable'] = hierarchy[node][field]['class']._meta.verbose_name_plural.lower() if node != 'generic_relations' else hierarchy['generic_relations'][field]['verbose'].lower()
                extra['title']['original'] = field
                extra['type'] = 'group' if (condition or result[field]['content']) else 'leaf'
                extra['state'] = 'closed'
                extra['can_create'] = [k.__name__ for k in get_subclasses_recursively(hierarchy[node][field]['class'], strict=False)]   
                extra['class'] = hierarchy[node][field]['class'].__name__
                extra['db_object'] = hierarchy[node][field]['class']
                extra['parent']['id'] = obj.pk
                extra['parent']['class'] = obj.__class__.__name__
                if not condition :
                    extra['object'] = 'link_list' if not (node in ['many_to_many_fields', 'generic_relations']) else 'm2m' 
                else :
                    extra['object'] = 'link_list_subclass' if not (node == 'many_to_many_fields') else 'm2m_subclass'
                extra['value'] = 'None' if not (obj_set.count() or condition) else None
                #retrieve constraints relative to the node
                is_link_to_itself = (obj.__class__ == obj_set.model)
                extra['node'] = dict()
                if constraints and constraints.has_key('links') :
                    if obj_set.model.__name__ in constraints['links'] :
                        extra['node']['constraints'] = constraints['links'][obj_set.model.__name__]['constraints']
#                        if is_link_to_itself :
#                            extra['node']['constraints'].update(constraints)    
                    elif is_link_to_itself :
                        extra['node']['constraints'] = constraints
                    else :
                        extra['node']['constraints'] = deepcopy(constraints_template)
                        #extra['node']['constraints'] = constraints
                    extra['table'] = extra['node']['constraints']['table'] 
                extra['node']['class'] = hierarchy[node][field]['class']
                dependencies = get_dependencies(obj_set.model)
                if (constraints['links'].has_key(extra['class'])) or (field in dependencies) :
                    if not is_link_to_itself :
                        new_constraints = {extra['class']:constraints['links'][extra['class']]}
                        h = hierarchy[node][field]
                    else :
                        if obj_set.model.__name__ in constraints['links'] :
                            new_constraints = {extra['class']:{'constraints':constraints['links'][obj_set.model.__name__]['constraints']}}
                            h = None
                        else :
                            new_constraints = {extra['class']:{'constraints':constraints}}
                            h = hierarchy
                        
                    extra['node']['objects'] = HierarchicView(extra['class'], extra['node']['class'].__module__, select_foreign_models=True, constraints=new_constraints, extra_content=True, complete_constraints=False, user=self.user, hierarchy=h)     
                    extra['node']['dependent_classes'] = hierarchy[node][field]['dependent_classes']
                result[field]['extra_content'] = extra
        return result
                    
    def hierarchic_representation(self, obj, hierarchy=None, path=None, starting_point=True, is_link_to_itself=False, constraints=None):
        result = SortedDict()
        has_subclasses = obj.__class__.__subclasses__() 
        cast = cast_object_to_leaf_class(obj)
        #find new constraints
        if starting_point :
            hierarchy = self.hierarchy
            new_constraints = self.constraints[obj.__class__.__name__]['constraints']
            
        elif is_link_to_itself :
            new_constraints = constraints  
        elif not has_subclasses and constraints and constraints.has_key('links') and constraints['links'].has_key(cast.__class__.__name__) :
            new_constraints = constraints['links'][cast.__class__.__name__]['constraints']
        elif has_subclasses and (constraints['links'].has_key(obj.__class__.__name__) or constraints['links'].has_key(cast.__class__.__name__)) :    
            if (self.cls == obj.__class__):      
                hierarchy = self.hierarchy  
                new_constraints = self.constraints[cast.__class__.__name__]['constraints']
            else :
                parents = get_parents_recursively(cast.__class__)
                if (self.cls == cast.__class__) :
                    new_constraints = self.constraints[cast.__class__.__name__]['constraints']
                elif not parents :
                    if cast.__class__.__name__ in constraints['links'] :
                        new_constraints = constraints['links'][cast.__class__.__name__]['constraints']    
                    else :
                        return cast
                else :
                    if (parents[-1].__name__ == obj.__class__.__name__) and (cast.__class__.__name__ != obj.__class__.__name__) and not constraints['display_base_class_only'] :
                        parent_constraints = constraints['links'][obj.__class__.__name__]['constraints']
                        new_constraints = parent_constraints['links'][cast.__class__.__name__]['constraints']
                    else :
                        new_constraints = constraints['links'][cast.__class__.__name__]['constraints']
        else :
            new_constraints = constraints
        #detect subclassing to include missing field
        chain = list()
        if cast.__class__ != obj.__class__ :
            chain.extend(cast.__class__._meta.get_base_chain(obj.__class__)) 
        if (not has_subclasses) or (not chain) :
            delegate_hierarchy = hierarchy
            delegate_object = cast
        else :  
            #has_subclasses = bool(chain)
            chain.reverse()
            chain.append(cast.__class__)
            chain.pop(0)#pop the main class
            initial_chain = copy(chain)#memorize the current chain to extend the new path
            key = chain.pop(0).__name__.lower()#initial condition
            
            delegate_hierarchy = hierarchy['subclasses'][key]
            for item in chain :
                delegate_hierarchy = delegate_hierarchy['subclasses'][item.__name__.lower()]
            delegate_object = cast
            self.extend_with_parent_properties(hierarchy, delegate_hierarchy)    
        for node in delegate_hierarchy :
            if starting_point :
                new_path = [self.cls]
            else :
                new_path = copy(path)
                new_path.append(hierarchy['class'])
 
            if chain :
                new_path.extend(initial_chain)
            #if the new path is not in skeleton
            #then the recursion has to be stopped
            #or if it is a local field
            if has_subclasses or self.is_in_skeleton(new_path) or is_link_to_itself or (path and (self.is_local_field(path[-1], new_path[-1]) and constraints and (delegate_object.__class__.__name__ in constraints['links']))) :
                if node == 'fields' :
                    result.update(self._replace_values(delegate_object, delegate_hierarchy, node))
                elif node == 'properties' :
                    result.update(self._replace_properties(delegate_object, delegate_hierarchy, node))
                elif node == 'foreign_keys' :
                    result.update(self._replace_single_links(delegate_object, delegate_hierarchy, node, new_path, constraints=new_constraints))
                elif node == 'reverse_one_to_one_keys' : 
                    result.update(self._replace_reverse_single_links(delegate_object, delegate_hierarchy, node, new_path, constraints=new_constraints))
                elif node in ['many_to_many_fields', 'reverse_foreign_keys', 'reverse_many_to_many_fields', 'generic_relations'] :
                    result.update(self._replace_multiple_links(delegate_object, delegate_hierarchy, node, new_path, constraints=new_constraints))        
            else :
                return cast    
        return result
    
    def unordered_list_representation(self, obj, hierarchy=None, level=None, starting_point=True):
        if starting_point :
            hierarchy = self.hierarchic_representation(obj)
            level = 3
        
        st = u''
        for node in hierarchy :
            if isinstance(hierarchy[node]['content'], dict) :
                new_hierarchy = hierarchy[node]['content']
                new_st = self.unordered_list_representation(obj, new_hierarchy, level + 2, starting_point=False)
                st += u'\n%s<li>%s\n%s<ul>%s\n%s</ul>\n%s</li>' % (level * '\t', node, (level + 1) * '\t', new_st, (level + 1) * '\t', level * '\t') 
            elif isinstance(hierarchy[node]['content'], list) :
                st += u'\n%s<li>%s' % (level * '\t', node)
                for item in hierarchy[node]['content'] :
                    if isinstance(item, dict) :
                        new_hierarchy = item['content']
                        new_st = self.unordered_list_representation(obj, new_hierarchy, level + 2, starting_point=False)
                    else :
                        new_st = u'\n%s<li>%s</li>' % ((level + 2) * '\t', item['content'])
                    st += u'\n%s<ul>%s\n%s</ul>' % ((level + 1) * '\t', new_st, (level + 1) * '\t') 
                st += u'\n%s</li>' % (level * '\t')
            else :
                if not hierarchy[node]['content'] :
                    value = "Not Defined"
                else :
                    value = hierarchy[node]['content']
                st += u'\n%s<li>%s : %s</li>' % (level * '\t', node, value)
        
        if starting_point :
            return "<li>%s\n\t<ul>\n\t\t%s\n\t\t</ul>\n\t</li>" % (obj, st) 
        else :
            return st
    
    def _flat_tree_representation(self, obj, flat_tree, default_index, parent_index=None, hierarchy=None, starting_point=True):
        raise Exception('test')
        if starting_point :
            hierarchy = self.hierarchic_representation(obj, is_link_to_itself=True)
            dct = deepcopy(node_template)
            dct['index'] = "%s.%s" % (parent_index, default_index)
            
            dct['class'] = obj.__class__.__name__
            dct['id'] = obj.pk
            dct['db_object'] = obj
            dct['parent']['index'] = parent_index
            dct['can_be_deleted'] = True
            dct['can_be_updated'] = True
            dct['title']['human_readable'] = obj.__unicode__()
            dct['title']['original'] = obj.__unicode__()
            dct['type'] = 'group' if hierarchy else 'leaf'
            dct['node'] = self.hierarchy
            dct['node']['constraints'] = self.constraints[self.cls.__name__]['constraints'] 
            dct['object'] = 'object'
            dct['state'] = 'closed'
            flat_tree.append(dct) 
            parent_index = dct['index']  
        else :
            parent_index = "%s.%s" % (parent_index, default_index)

        if not ((len(obj._meta.fields) == 1) and obj._meta.fields[0].primary_key):
            i = 0
            for node in hierarchy :
                extra_content = copy(hierarchy[node]['extra_content'])
                extra_content['index'] = parent_index + '.' + str(i)
                extra_content['parent']['index'] = parent_index
                if extra_content['state'] == None :
                    extra_content['state'] = 'closed'
                flat_tree.append(extra_content)
                if isinstance(hierarchy[node]['content'], dict) :
                    new_hierarchy = hierarchy[node]['content']
                    self._flat_tree_representation(obj, flat_tree, i, parent_index=parent_index, hierarchy=new_hierarchy, starting_point=False)
                elif isinstance(hierarchy[node]['content'], list) :
                    index = extra_content['index']
                    j = 0
                    for item in hierarchy[node]['content'] :
                        extra_content = deepcopy(item['extra_content'])
                        extra_content['index'] = index + '.' + str(j)#len(flat_tree)
                        extra_content['parent']['index'] = index#parent_index
                        if extra_content['state'] == None :
                            extra_content['state'] = 'closed'
                        flat_tree.append(extra_content)
                        if isinstance(item['content'], dict) :
                            new_hierarchy = item['content']
                            self._flat_tree_representation(obj, flat_tree, j, parent_index=index, hierarchy=new_hierarchy, starting_point=False)
                        j += 1
                i += 1
        else :
            dct['type'] = 'leaf'
        if starting_point :
            return flat_tree  
        
    def flat_tree_representation(self, flat_tree=None, parent_index=None, order=None):
        if flat_tree == None :
            flat_tree = list()
        manager = self.cls.objects
        lst = manager.all()
        if is_under_access_control(manager.model) :
            lst = get_accessible_by(lst, self.user)
        if order :
            lst = lst.order_by(*order)
        for obj in lst :
            self._flat_tree_representation(obj, flat_tree, parent_index)

if __name__ == '__main__' :
    pass
