# -*- coding: utf-8 -*-
'''
Attribute parser for C#.

@author: tzulberti
'''

from logging import getLogger

from pywebuml.models import Attribute, VISIBILITY_VALUES
from pywebuml.initialize.parsers.constants import (
                    CONST_KEYWORDS, 
                    LANGUAGE_BASE_VALUES,
                    )
from pywebuml.initialize.parsers.csharp.base import BaseCSharpParser
from pywebuml.initialize.parsers.exceptions import (                                        
                    ClossingArrayException,                    
                    )

LOGGER = getLogger(__name__)


class CSharpAttributeParser(BaseCSharpParser):
    ''' Given the class and the content of the file,
    it has the responsability of parsing it into a 
    pywebuml.models.Attribute.
    '''
    
    def parse(self, class_model, content, index):
        ''' Parse the method of the class of the content.
        
        :parameters:
            class_model:  ``pywebuml.model.Class``
                the current class that is being parsed.
            content: list(str)
                the content of the file
            index: int
                from where start parsing
                
        :return:
            a tuple (pywembuml.models.Method, int) that has the parsed
            method and the index value from where it should continue reading.
            
        :raises:
        - `pywebuml.initialize.parser.exceptions.ClossingArrayException`
            if it can't find the closing } of the array definition
            
        - `pywebuml.initialize.parser.exceptions.EmptyAttributeNameException`
            if it cant get the name of the attribute.
        '''        
        current_position = index
        current_line = content[index]

        visibility = self.check_visibility(current_line)
        is_static = self.has_any_keyword(current_line, ['static'])
        is_final = self.has_any_keyword(current_line, CONST_KEYWORDS)

        current_line = self.remove_modifiers(current_line)

        
        should_iterate = False
        if '{' in current_line:
            # must check if the property definition ends in
            # this line or in some other line.
            if current_line.count("{") != current_line.count("}"):
                # if there is a property definition, then I must update the
                # index
                should_iterate = True

        elif current_position < len(content) - 1:
            # only check if the next line is a property or set the values
            # of the array, if there are more lines in the content.

            current_position += 1
            if content[current_position] == '{':
                # in this case check if the line is only a '{' to take into
                # account that the next line could be an attribute with
                # properties definition
                should_iterate = True
            elif '[]' in current_line and content[current_position].startswith('{'):
                # take into account that is an array. For example:
                #   public int[] i =
                #       { 3, ...                
                should_iterate = True
            elif content[current_position].startswith('{') and self.has_any_keyword(content[current_position], ['get', 'set']):
                # take into account some properties definitions.
                #   private int foo
                #   { get { return value; } }
                should_iterate = True
            elif content[current_position].startswith('=') or content[current_position-1].endswith('='):
                # take into account values setted in the next line.
                # private List<Foo> foos 
                #       = new ArrayList<Foo>();
                # TODO agregar un test para el caso:
                # private List<Foo> foos =
                #       new ArrayList<Foo>();
                should_iterate = True

        # iterate the property methods of the attribute.
        if should_iterate:
            opened_keys = 0
            while True:
                if current_position == len(content):
                    raise ClossingArrayException(index)

                line = content[current_position]
                if self.is_comment(line):
                    current_position = self.move_to_documentation_end(content, current_position)
                    continue

                opened_keys = opened_keys + line.count('{') - line.count('}')
                current_position += 1

                if opened_keys == 0:
                    break

        # remove the part of the property getter and setter
        if '{' in current_line:
            current_line = current_line[:current_line.index("{")]

        if '=' in current_line:
            # then the line is something of the type:
            #   private Foo bar = new Foo();
            # Have to remove the things that are at the right from
            # the "="
            current_line = current_line[:current_line.index("=")]

        current_line = current_line.replace(';', '')

        if '//' in current_line:
            # take into account if the line has a comment
            #   private int i; // this is a comment
            documentation = current_line[current_line.index('//') + 2:].strip()
            current_line = current_line[:current_line.index('//')]

        else:            
            documentation = self.get_documentation_string(content, index)


        # to take into account that some text of the line was removed
        current_line = current_line.strip()        

        
        if 'this' in current_line or 'this [' in current_line:
            # take into account that the attribute could be an indexer declaration.
            if current_position == index:
                current_position += 1
            return (current_position,  None)
                    
        # can't use current_line.split(' '), becuase there can be more than
        # one space between the type and variable definition
        variable_type, name = self.get_type_and_name(current_line, index)
        referenced_class_package = self.get_referenced_type(variable_type)

        if index == current_position:
            # in this case the variable is of 1 line...
            # private int j;
            current_position += 1
                    
        LOGGER.debug("Found attribute: %s", name)
        return (current_position, 
                Attribute(name, variable_type, class_model, visibility,
                            documentation, is_static, is_final,
                            referenced_class_package)
                 )
    
    def get_referenced_type(self, variable_type):
        ''' Get the referenced type of the variable.
        
        :parameters:
            variable_type: str
                the type as defined when defined the variable.
        
        :returns:
            the referenced class package, or None if the type is a base type.
        '''
        referenced_class_package = None
        
        if variable_type not in LANGUAGE_BASE_VALUES \
                and not '[' in variable_type and not '<' in variable_type:
            # its a common object attr. For example: Foo foo.
            referenced_class_package = variable_type                                            
            
        elif variable_type.count('<') == 1:
            # it is a dictionary or list (some kind of template). For example:
            # Map<Foo, int> or List<Foo>
            # lets get the referenced classses that are in the dictionary.
            template_values = variable_type[variable_type.index('<')+1: variable_type.index('>')].strip()
            if ',' in template_values:               
                type1, type2 = template_values.split(',')                
                type1 = type1.strip()
                type2 = type2.strip()
                if type1 not in LANGUAGE_BASE_VALUES:
                    referenced_class_package = type1
                elif type2 not in LANGUAGE_BASE_VALUES:
                    referenced_class_package = type2                    
            elif template_values not in LANGUAGE_BASE_VALUES:
                # it only has one template class...                
                referenced_class_package = template_values
            
        # TODO add some unittest for this case
        elif '<' in variable_type and variable_type.count('<') > 1:        
            # then ois a template of templates.
            # For example:
            #   Map<Foo, List<Bar>> or List< MyTemplate<Foo>>
            
            # get the type inside the template.
            variable_type = variable_type[variable_type.index('<') +1: variable_type.rindex('>')].strip()
            if ',' in variable_type:
                for type in variable_type:
                    type = type.strip()
                    res = self.get_referenced_type(variable_type)
                    if res:
                        return res
            else:                                
                return self.get_referenced_type(variable_type)                                                        
        elif '[' in variable_type:
            # it's an array type...
            array_class = variable_type[variable_type.index('[')+1: variable_type.index(']')].strip()
            if not array_class not in LANGUAGE_BASE_VALUES:
                referenced_class_package = variable_type
            
        # TODO check if a class with that name exists in the database
        # and set the namespace
        if referenced_class_package and not '.' in referenced_class_package:
            referenced_class_package = 'global.%s' % referenced_class_package
            
        return referenced_class_package
           