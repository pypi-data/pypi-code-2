# -*- coding: utf-8 -*-

'''
Defines de model classes and the connection to them
'''

from main import db



CLASS_TYPES = (
    'inner',
    'normal',
    'enum',
    'interface'
)

# the visibility of a method or attribute of a class.
VISIBILITY_VALUES = (
    'public',
    'protected',
    'private'
)

PROGRAMMING_LANGUAGES = (
    "C#",
    "Java",
    "Python",
)

class Class(db.Model):
    ''' Represents the Java/C#/Python class.

    The values are:

    - discriminator: indicates if the class is normal or inner.
    - package: the complete path of the class. In the case of C#
    it will be the namespace and the name of the class. For java
    it will be the package and the name of the class.
    - name: the name of the class without taking into account the
    namespace/package.
    - documentation: the documentation of the class.
    - is_interface: inidcates if the class is an interface or not.
    - file_path: the filesystem path where the file of the class is located.
    In java it will be the same as the package without the class name. In C#
    it will be the path where the file was found. It is relative to where
    the command was executed.
    - programming_language: indicates the programming language of the class.
    The programming language will be used later on the web to remove
    the getter/setters of the class.
    '''

    __tablename__ = 'classes'	

    discriminator = db.Column('type', db.String(50))
    package = db.Column(db.String(1024), primary_key = True)
    name = db.Column(db.String(255))
    documentation = db.Column(db.String(3000))
    is_interface = db.Column(db.Boolean, nullable = False)
    filepath = db.Column(db.String(1024), nullable = False)
    programming_language = db.Column(db.String(20), nullable = False)

    __mapper_args__ = {'polymorphic_on': discriminator,
					   'polymorphic_identity': 'normal'}

    def __init__(self, package, name, documentation, is_interface,
                 filepath , programming_language):
        self.package = package
        self.name = name
        self.documentation = documentation
        self.is_interface = is_interface		
        self.filepath = filepath
        self.programming_language = programming_language

    def __eq__(self, other):
        return self.package == other.package

    def __hash__(self):
        return hash(self.package)

    def __repr__(self):
        return '<Class("%s", "%s", %s)>' % (self.package, self.name, self.is_interface)

    def no_getter_and_setters(self):
        ''' Returns the attributes that aren't getter or setters.

        :returns:
            a list of `pywebuml.models.Attributes` that aren't used as
            getter and setters.
        '''
        # TODO ver si a esto lo vamos a hacer al momento del parseo
        res = []
        used_names = []

        for attr in self.attributes:
            if attr.visibility == 'public':
                res.append(attr)
                used_names.append(attr.name)

        for attr in self.attributes:
            if attr.visibility in ('private', 'protected'):
                name = attr.name
                if name.startswith('m'):
                    name = name[1:]
                if name.istitle():
                    name = name[0].lower() + name[1:]
                if name not in used_names:
                    res.append(attr)
                    used_names.append(name)

        return res




class InnerClass(Class):
    ''' These classes are the same as ``pywebuml.model.Class``
    but are created when one class is defined iniside another.

    This is used for example in this case:

    public class Foo {

        private int j = 3;

        public class Bar {

            private int i = 4;
        }
    }


    In this case, the owner will be the class *Foo*
    '''

    __tablename__ = 'inner_classes'
    __mapper_args__ = {'polymorphic_identity': 'inner'}

    owner_package_name = db.Column(db.String(1024), db.ForeignKey('classes.package'), primary_key = True)
    owner = db.relationship(Class, backref=db.backref('inner_classes'))

    def __init__(self, owner, package, name, documentation, is_interface,
                        filepath, programming_language):
        super(InnerClass, self).__init__(package, name, documentation, is_interface,
                        filepath, programming_language)
        self.owner = owner


class ClassInheritence(db.Model):
    ''' Represent the inheritence relationshipt between two classes.

    For example, if class A extends class B and C, then in the database
    there will the following rows:
        A   B
        A   C

    In some languages (Java) a class can only extend one class, but in
    other languages (Python) there is no such limitation.
    '''

    __tablename__ = 'class_inheritence'

    class_package = db.Column(db.String(1024), db.ForeignKey('classes.package'), primary_key = True)
    base_class_package = db.Column(db.String(1024), primary_key = True)

    class_model = db.relationship(Class, backref=db.backref('base_classes'))

    def __init__(self, class_model, base_class_package):
        self.class_model = class_model
        self.base_class_package = base_class_package



class ClassImplements(db.Model):
    ''' Relates a class with the interfaces it implements.

    For example if class A implements D and E, then in the database there
    will be the folling rows:
        A   D
        A   E

    There are some clases that doesn't have interface (Python), so there
    won't be no rows in this table.

    The values are:
        class_package: the package of the class that implements the interfaces.
        interface_class_package: the package of the interface.
    '''

    __tablename__ = 'class_implementations'

    class_package = db.Column(db.String(1024), db.ForeignKey('classes.package'), primary_key = True)
    interface_class_package = db.Column(db.String(1024), primary_key = True)

    class_model = db.relationship(Class, backref=db.backref('interfaces'))

    def __init__(self, class_model, interface_class_package):
        self.class_model = class_model
        self.interface_class_package = interface_class_package





class Attribute(db.Model):
    ''' Represents each of the attributes of the class.

    It has the following fields:
    - The name is the name of the attribute,
    - the class_id is the class to which the attribute belongs,
    - the visibility indicates if it is private/protected/public
    - the type indicates the type of the attribute. It could be some
    basic system attribute (float, int, string, etc..) or a reference
    to another class. If it is a refernece, then the referenced_class_id
    will have the id of the ``Class``
    - is_final indicates if the value is const/final/etc..
    - is_static indicates if the attribute is static.
    '''

    __tablename__ = 'attributes'

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(255))
    type = db.Column(db.String(255))
    class_package = db.Column(db.String(1024), db.ForeignKey('classes.package'))
    visibility = db.Column(db.String(50))
    referenced_class_package = db.Column(db.Integer)
    documentation = db.Column(db.String(1000))
    is_final = db.Column(db.Boolean)
    is_static = db.Column(db.Boolean)

    class_model = db.relationship(Class, backref=db.backref('attributes'))

    def __init__(self, name, type, class_model, visibility,
                 documentation, is_static, is_final, referenced_class_package = None):
        self.name = name
        self.type = type
        self.class_model = class_model
        self.visibility = visibility
        self.documentation = documentation
        self.is_final = is_final
        self.is_static = is_static
        self.referenced_class_package = referenced_class_package

    def __repr__(self):
        return self.name


class Method(db.Model):
    ''' Represents a model of the class.

    It has the followin fields:
    - name: the name of the method
    - singature: the parameters and return class of the method. For example:
        sum(long a, long c) -> long
    - visibility: indicates if it is private/protected/etc...
    - short_documentation: has the documentation of the method without the
      documentation of the parameters.
    - long_documentation: the whole documentation of the method.
    - is_static: indicate if the method is static.
    - is_abstract: indicate if the method is abstract. If the class is
      an interface, then the method will be abstract
    '''

    __tablename__ = 'methods'

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(255))
    class_package = db.Column(db.String(1024), db.ForeignKey('classes.package'))
    signature = db.Column(db.String(1024))
    visibility = db.Column(db.String(50))
    short_documentation = db.Column(db.String(1000))
    long_documentation = db.Column(db.String(3000))
    is_static = db.Column(db.Boolean)
    is_abstract = db.Column(db.Boolean)

    class_model = db.relationship(Class, backref=db.backref('methods'))


    def __init__(self, name, class_model, signature, visibility,
                short_documentation, long_documentation, is_static):
        self.name = name
        self.class_model = class_model
        self.signature = signature
        self.visibility = visibility
        self.short_documentation = short_documentation
        self.long_documentation = long_documentation
        self.is_static = is_static

    def __repr__(self):
        return '<Method("%s")>' % self.signature
