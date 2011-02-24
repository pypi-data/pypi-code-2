from jinja2 import PackageLoader, Environment
from lxml import etree
import sys, os
import string
import getopt
import re
import xmltopy
from decimal import Decimal

def get_type_info(type_name, nsmap):
    ns = nsmap[None]

    if ':' in type_name:
        prefix, type_name = type_name.split(':')
        ns = nsmap[prefix]    
    
    return ns, type_name

def resolve_type(element):
    target_namespace = element.xpath('/x:schema', namespaces={'x': 'http://www.w3.org/2001/XMLSchema'})[0].get('targetNamespace')
    test_assignment = None
    
    ns, type_name = get_type_info(element.get('type'), element.nsmap)

    if ns == target_namespace:
        e = element.xpath('/x:schema/x:simpleType[@name="%s"]' % type_name, namespaces={'x': 'http://www.w3.org/2001/XMLSchema'})
        if e:
            if e[0].xpath('x:restriction/x:enumeration', namespaces={'x': 'http://www.w3.org/2001/XMLSchema'}):
                test_assignment = '%s.' % type_name
            ns, type_name = get_type_info(e[0].xpath('.//x:restriction', namespaces={'x': 'http://www.w3.org/2001/XMLSchema'})[0].get('base'), element.nsmap)
        else:    
            return type_name, '%s()' % type_name
    
    if ns == 'http://www.w3.org/2001/XMLSchema':
        if type_name == 'string': return 'str', test_assignment or '\'string value\''
        if type_name == 'dateTime': return 'datetime', 'datetime(1999, 12, 31, 23, 59, tzinfo=pytz.utc)'
        if type_name == 'integer': return 'int', '7'
        if type_name == 'int': return 'int', '7'
        if type_name == 'boolean': return 'bool', 'True'
        if type_name == 'long': return 'long', '5000000000L'
        if type_name == 'float': return 'float', '7.77'
        if type_name == 'date': return 'date', 'date(1999, 12, 31)'
        if type_name == 'decimal': return 'Decimal', '7.77'
        if type_name == 'nonNegativeInteger': return 'int', '7'
        raise Exception, 'type %s is not supported!' % type_name
    
    if ns in dependencies:
        ref = dependencies[ns]
        return '%s.%s' % (ref, type_name), 'None # TODO: set an appripriate test value: %s.%s()' % (ref, type_name)
    
    raise Exception('Unresolved namespace %s' % ns)

def pick_enum_for_doctest(test_assignment, constant_classes):
    if test_assignment.endswith('.'):
        for c in constant_classes:
            if c['name'] == test_assignment[:-1]:
                test_assignment = '%s.%s' % (c['name'], c['members'][0].replace(' ', '_').replace('-', '_'))
                break
    return test_assignment    

def depth(classes, class_name, i=0):
    if class_name == 'object':
        return i
    
    for x in classes:
        if x['name'] == class_name:
            return depth(classes, x['base'], i+1)
    
    return i+1    

def go(schema_path, module_name, dependencies, additional_imports, generate_base_classes=False, generate_subclass_stubs=False):
    classes = []
    constant_classes = []
    primitive_classes = []

    x = etree.fromstring(open(schema_path).read())
    target_namespace = x.xpath('/x:schema', namespaces={'x': 'http://www.w3.org/2001/XMLSchema'})[0].get('targetNamespace')
    
    simpletypes = x.xpath('/x:schema/x:simpleType[x:restriction]', namespaces={'x': 'http://www.w3.org/2001/XMLSchema'})
    for y in simpletypes:
        restriction = y.xpath('x:restriction', namespaces={'x': 'http://www.w3.org/2001/XMLSchema'})
        base_ns, base_type_name = get_type_info(restriction[0].attrib['base'], restriction[0].nsmap)

        if y.xpath('x:restriction/x:enumeration', namespaces={'x': 'http://www.w3.org/2001/XMLSchema'}):
            # only generate these classes when the base type is 'string'
            # this prevents generating a class where members names are not valid in Python (such as ints, longs, etc) 
            if base_type_name == 'string':        
                class_data = {}
                constant_classes.append(class_data)
                class_data['name'] = y.get('name')
                class_data['members'] = []
                # ignore empty enumeration values, example: <xsd:enumeration value=""/>
                for e in y.xpath('x:restriction/x:enumeration[@value!=""]', namespaces={'x': 'http://www.w3.org/2001/XMLSchema'}):
                    class_data['members'].append(e.get('value'))
        else: # simpletype with restriction, but not an enumeration            
            if base_type_name == 'string':
                class_data = {}
                primitive_classes.append(class_data)
                class_data['base'] = 'str'
                class_data['name'] = y.get('name')
                class_data['members'] = []
                
    for y in x.xpath('/x:schema/x:complexType', namespaces={'x': 'http://www.w3.org/2001/XMLSchema'}):
        class_data = {}
        classes.append(class_data)
        class_data['name'] = y.get('name')
        class_data['xml_namespace'] = target_namespace
        class_data['base'] = 'object'
    
        if y.xpath('.//x:extension', namespaces={'x': 'http://www.w3.org/2001/XMLSchema'}):
            class_data['base'] = y.xpath('.//x:extension', namespaces={'x': 'http://www.w3.org/2001/XMLSchema'})[0].get('base').split(':')[1]
    
        class_data['members'] = []
        class_data['types'] = []
        class_data['elements'] = []
        
        elements = []
        elements += y.xpath('.//x:sequence/x:element | .//x:choice/x:element', namespaces={'x': 'http://www.w3.org/2001/XMLSchema'}) 
        
        for e in elements:
            type_name, test_assignment = resolve_type(e)
            test_assignment = pick_enum_for_doctest(test_assignment, constant_classes)
            if 'maxOccurs' in e.attrib:
                maxOccurs = e.attrib['maxOccurs']
                if maxOccurs == 'unbounded' or int(maxOccurs) > 1:
                    test_assignment = '[%s, %s]' % (test_assignment, test_assignment)
                    type_name = '[%s]' % type_name
            class_data['types'].append({'name': e.get('name'), 'type': type_name, 'test_assignment': test_assignment})
            class_data['members'].append(e.get('name'))
            class_data['elements'].append(e.get('name'))
            
        class_data['attributes'] = []
        for e in y.xpath('.//x:attribute', namespaces={'x': 'http://www.w3.org/2001/XMLSchema'}):
            type_name, test_assignment = resolve_type(e)
            test_assignment = pick_enum_for_doctest(test_assignment, constant_classes)
            class_data['types'].append({'name': e.get('name'), 'type': type_name, 'test_assignment': test_assignment})
            class_data['members'].append(e.get('name'))
            class_data['attributes'].append(e.get('name'))            
            
    for y in x.xpath('/x:schema/x:element[x:complexType]', namespaces={'x': 'http://www.w3.org/2001/XMLSchema'}):
        class_data = {}
        classes.append(class_data)
        class_data['name'] = y.get('name')
        class_data['xml_namespace'] = target_namespace
        class_data['base'] = 'object'
    
        if y.xpath('.//x:extension', namespaces={'x': 'http://www.w3.org/2001/XMLSchema'}):
            class_data['base'] = y.xpath('.//x:extension', namespaces={'x': 'http://www.w3.org/2001/XMLSchema'})[0].get('base').split(':')[1]
    
        class_data['members'] = []
        class_data['types'] = []
        class_data['elements'] = []
        
        elements = []
        elements += y.xpath('.//x:sequence/x:element', namespaces={'x': 'http://www.w3.org/2001/XMLSchema'})
        elements += y.xpath('.//x:sequence/x:choice/x:element', namespaces={'x': 'http://www.w3.org/2001/XMLSchema'})
                
        for e in elements:
            type_name, test_assignment = resolve_type(e)
            test_assignment = pick_enum_for_doctest(test_assignment, constant_classes)      
            if 'maxOccurs' in e.attrib:
                maxOccurs = e.attrib['maxOccurs']
                if maxOccurs == 'unbounded' or int(maxOccurs) > 1:
                    test_assignment = '[%s, %s]' % (test_assignment, test_assignment)
                    type_name = '[%s]' % type_name  
            class_data['types'].append({'name': e.get('name'), 'type': type_name, 'test_assignment': test_assignment})
            class_data['members'].append(e.get('name'))
            class_data['elements'].append(e.get('name'))
            
        class_data['attributes'] = []
        for e in y.xpath('.//x:attribute', namespaces={'x': 'http://www.w3.org/2001/XMLSchema'}):
            type_name, test_assignment = resolve_type(e)
            test_assignment = pick_enum_for_doctest(test_assignment, constant_classes)          
            class_data['types'].append({'name': e.get('name'), 'type': type_name, 'test_assignment': test_assignment})
            class_data['members'].append(e.get('name'))
            class_data['attributes'].append(e.get('name'))
    
    for c in classes:
        c['depth'] = depth(classes, c['name'])
        if c['base'] != 'object':
            for b in primitive_classes:
                if b['name'] == c['base']:
                    c['base'] = b['base']
            for b in classes:
                if b['name'] == c['base']:
                    c['elements'] = b['elements'] + c['elements']
                    c['types'] = b['types'] + c['types']
                    if 'attributes' in b and 'attributes' in c:
                        c['attributes'] = b['attributes'] + c['attributes']
                    elif 'attributes' in b:
                        c['attributes'] = b['attributes']
    
    classes.sort(lambda x, y: cmp(x['depth'], y['depth']))
    
    from datetime import datetime

    env = Environment(loader=PackageLoader('xmltopy', 'templates'), trim_blocks=True)
    base_class_template = env.get_template('xsdtopy.txt')
    subclass_template = env.get_template('subclass_stub.txt')
    
    module_file_name = '%s.py' % module_name
    
    if generate_subclass_stubs:
        module = open(module_file_name, 'w')
        module.write(subclass_template.render(version=xmltopy.__version__,
                                              constant_classes=constant_classes,
                                              classes=classes,
                                              base_classes_module = module_name,
                                              dependencies=dependencies.values(),
                                              timestamp = str(datetime.now()),
                                              target_namespace = target_namespace,
                                              schema_file = os.path.basename(schema_path)))
        module.close()

    if generate_base_classes or generate_subclass_stubs:
        module_file_name = '%s_base.py' % module_name
    
    module = open(module_file_name, 'w')
    module.write(base_class_template.render(version=xmltopy.__version__,
                                            constant_classes=constant_classes,
                                            classes=classes,
                                            primitive_classes=primitive_classes,
                                            dependencies=dependencies.values(),
                                            additional_imports = additional_imports,
                                            timestamp = str(datetime.now()),
                                            target_namespace = target_namespace,
                                            schema_file = os.path.basename(schema_path)))
    module.close()

if __name__ == '__main__':
    opts, args = getopt.getopt(sys.argv[1:], 'f:d:bsn:i:')
    dependencies = {}
    additional_imports = []
    
    generate_base_classes=False
    generate_subclass_stubs=False
    module_name = None
    
    for o, a in opts:
        if o == '-f':
            schema_path = a
        elif o == '-d':
            for item in a.split(','):
                module, ns = item.split(':', 1)
                dependencies[ns] = module
        elif o == '-b':
            generate_base_classes = True
        elif o == '-s':
            generate_subclass_stubs = True
        elif o == '-n':
            module_name = a
        elif o == '-i':
            for item in a.split(','):
                subitems = item.split('.')
                additional_imports.append("from %s import %s" % (subitems[0], subitems[1]))

    if module_name is None:
        filename = os.path.splitext(os.path.basename(schema_path))[0]
        module_name = re.sub(r'(.)([A-Z])', r'\1_\2', filename).lower()
        
    go(schema_path, module_name, dependencies, additional_imports, generate_base_classes, generate_subclass_stubs)
