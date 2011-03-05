# -*- coding: utf-8 -*-

'''
Created on 05/02/2011

@author: tzulberti
'''

from logging import getLogger

from pywebuml.main import db
from pywebuml.models import Class, InnerClass, ClassInheritence, ClassImplements
from pywebuml.initialize.parsers.csharp.attribute_parser import CSharpAttributeParser
from pywebuml.initialize.parsers.csharp.base import BaseCSharpParser
from pywebuml.initialize.parsers.csharp.method_parser import CSharpMethodParser
from pywebuml.initialize.parsers.constants import CLASS_KEYWORDS
from pywebuml.initialize.parsers.exceptions import (
            MissingClosingClassDefinition,
            MissingOpeningClassDefinition
            )

LOGGER = getLogger(__name__)

class CSharpClassParser(BaseCSharpParser):
    ''' Given a content it parses it content and returns the class
    representation.
    '''


    def parse(self, filepath, content, index, current_namespace, owner = None):
        ''' Parse the content of the class.

        The index must be setted in the first line of the class definition.

        The result will be a list with more than one element if there is an
        inner class. If there is more than one class definition in the file,
        then this method should be used more than once.

        :parameters:
            filepath: str
                the folder and name of the file. For example:
                    ./examples/mycode.c_sharp
            content: list(str)
                the content of the file.
            current_namespace: str
                the namespace of the class.
            owner: pywebuml.model.Class
                the owner of this class. This will only be used if the class
                as inner.

        :return:
            a tuple with the index and the list of class representation. I
        '''
        res = []
        started_definition = index
        index, current_class = self.parse_class_signature(filepath, content, index, current_namespace, owner)
        res.append(current_class)
        position = index - 1

        current_line = content[position]
        if '{' in current_line and '}' in current_line and \
            self.has_any_keyword(current_line, CLASS_KEYWORDS):
            # then the class definition is of 1 line
            # For example:
            #   public class Foo { }
            return (index, res)

        while True:
            if index == len(content):
                raise MissingClosingClassDefinition(started_definition)


            current_line = content[index]
            if self.is_comment(current_line):
                index = self.move_to_documentation_end(content, index)
                continue

            if current_line in  ('}', '};'):
                # the closing key of the class definition
                # must comprare to equals because the current line could be a
                # one line method, attr or inner class definition
                index += 1
                break

            if '//' in current_line:
                current_line = current_line[:current_line.index('//')]

            if self.has_any_keyword(current_line, CLASS_KEYWORDS):
                index, inner_res = self.parse(filepath, content, index, current_class.package, current_class)
                res.extend(inner_res)
            elif self.is_method(current_line) or self.has_any_keyword(current_line, ['operator']):
                index = self.parse_method(content, index, current_class)
            else:
                index = self.parse_attribute(content, index, current_class)

        return (index, res)



    def parse_attribute(self, content, index, current_class):
        ''' Parse the atttibute.

        :parameters:
            content: list(str)
                the content of the file.
            index: int
                the current line of the content
            current_class: pywebuml.models.Class
                where the attribute belongs.

        :returns:
            the index where the attribute definition ends.
        '''
        attr_parser = CSharpAttributeParser()
        index, attr = attr_parser.parse(current_class, content, index)
        return index


    def parse_method(self, content, index, current_class):
        ''' The same as parse_attribute but this time with a method.
        '''
        method_parser = CSharpMethodParser()
        index, method = method_parser.parse(current_class, content, index)
        return index


    def parse_class_signature(self, filepath, content, index, current_namespace, owner = None):
        ''' Returns the `pywebuml.models.Class`  object without any attribute
        or method, but with its implementations and extensions.

        :parameters:
            content: list(str)
                the content of the file
            index: int
                from which position of the content start getting the info.
            current_namespace: str
                the namespace to which this class belongs.
                The defaut will be global, but it can be defined
                in the file.
            owner: `pywebuml.models.Class`
                if the class is an inner class, then this is the
                parent class.

        :returns:
            a ``pywebuml.models.Class`` taking into account the
            content of the file.
        '''
        current_line = content[index]

        is_interface = self.has_any_keyword(current_line, ['interface'])
        is_partial = self.has_any_keyword(current_line, ['partial'])

        class_data = self.remove_keywords(current_line, CLASS_KEYWORDS)
        class_data = self.remove_modifiers(class_data)


        visibility = self.check_visibility(class_data)
        class_data = self.remove_keywords(class_data, [visibility])


        # if the class definition doesn't end in that line then
        # it might have some other base_classes in the following lines
        # for example:
        #   public class Foo : A, B, C
        #                      D, E, F
        #                      G {
        finish = False
        current_line = class_data
        class_definition = ''
        current_position = index

        while True:
            current_position += 1
            class_definition += current_line

            # found the end of the class definition
            if '{' in current_line:
                break

            if current_position == len(content):
                raise MissingOpeningClassDefinition()

            current_line = content[current_position].strip()


        # TODO get the documentation of the class and check if it is an interface
        documentation = ''

        # remove the {
        # Don't take into account that there might be some code on that
        # line.
        base_classes = []
        implements = []

        # saco todo lo que esta a la derecha del { becuase
        # that belongs to the class implementation
        class_definition = class_definition[:class_definition.index('{')]


        # TODO get the documentation of the class
        documentation = ''

        if ':' in class_definition:
            class_name = class_definition[:class_definition.index(':')]
            are_template_constrains = False

            # check if the class is a singlton, and
            # the template might have some constrains.
            if '<' in class_name:
                # in this case is a template that has some constrains
                if self.has_any_keyword(class_name, ['where']):
                    #TODO keyword bug....
                    class_name = class_name[:class_name.index('where')].strip()
                    are_template_constrains = True

            if not are_template_constrains:
                class_extensions = class_definition[class_definition.index(':') + 1 :].strip()
                for extension in class_extensions.split(','):
                    extension = extension.strip()
                    if extension.startswith('I'):
                        # TODO falta checkear que la segunda palabra tambien sea
                        # una mayuscula
                        implements.append(extension)
                    else:
                        base_classes.append(extension)
        else:
            class_name = class_definition

        class_name = class_name.strip()
        index = current_position
        LOGGER.debug("Found class: %s", class_name)
        package = '%s.%s' % (current_namespace, class_name)

        if is_partial:
            klass = self.find_partial_class(package)
            if not klass:
                klass = Class(package, class_name, documentation, is_interface,
                                    filepath, 'C#')
        elif owner:
            klass = InnerClass(owner, package, class_name, documentation,
                                    is_interface, filepath, 'C#')
        else:
            klass = Class(package, class_name, documentation, is_interface,
                                    filepath, 'C#')

        for base_name in base_classes:
            base_name = 'global.%s' % base_name
            ClassInheritence(klass, base_name)

        for interface in implements:
            interface = 'global.%s' % interface
            ClassImplements(klass, interface)

        return (index, klass)


    def find_partial_class(self, package):
        ''' Find the definition of the class it the class already exists.
        If it doesn't exists then it will return None.

        :parameter:
            package: str
                the package of the partial class found. For example:
                    global.Foo.

        :returns:
            the database class if found else None.
        '''
        # Can't use Class.query because isn't inside a request.
        # see: http://flask.pocoo.org/mailinglist/archive/2010/10/14/flask-sqlalchemy-query-property
        query = db.session.query(Class)
        query = query.filter_by(package = package)
        return query.first()

    def is_method(self, current_line):
        ''' Identifies if the current line is a method
        or an attribute.

        :parameters:
            content: list(str)
                the content of the file

        :returns:
            True if the current line is a method definition
            else False.
        '''
        if '//' in current_line:
            # take into account lines that have comments. For example:
            #   private void myMethod(int foo, int bar) // this is to...
            current_line = current_line[:current_line.index('//')]


        if self.has_any_keyword(current_line, ['operator']):
            # Take into account if the line is an operator definition.
            #   public static bool operator !=(Foo lhs, Foo rhs)
            return True

        if not '(' in current_line:
            # it is an attribute (or the properties) because all methods must
            # have a () in the definition.
            return False

        if '=' in current_line and '{' not in current_line:
            # it is an attribute:
            #   private int b = 3;
            return False

        # check if it is a method defined in one line
        # or the properties (rare which has a method that uses (
        # of the attribute. For example:
        #    public OnDemand() { b = 3; }
        #    public int attr { get { Debug.Log("Foo"); value; } }
        if self.has_any_keyword(current_line, ['get', 'set']):
            return False
        elif '(' in current_line and '=' in current_line and (
                current_line.find('(') > current_line.find('=')
                ):
            # in this case the value is something like:
            #   private Foo[] bar = new Foo[] { new Foo(1,2) };
            return False
        else:
            return True

