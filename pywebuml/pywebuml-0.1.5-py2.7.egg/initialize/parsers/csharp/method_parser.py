# -*- coding: utf-8 -*-

'''
Created on 05/02/2011

@author: tzulberti
'''
from logging import getLogger
from xml.dom.minidom import parseString

from pywebuml.models import Method                    

from pywebuml.initialize.parsers.exceptions import (                    
                    MissingClosingParenthesis,
                    MissingClosingMethod,                                        
                    )

from pywebuml.initialize.parsers.constants import ABSTRACT_KEYWORDS
from pywebuml.initialize.parsers.csharp.base import BaseCSharpParser




LOGGER = getLogger(__name__)


class CSharpMethodParser(BaseCSharpParser):
    ''' Parser for CSharp methods.
    
    Given the content of the file and the current class, it
    will have the responsability of parsing the method of the class.
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
        - MissingClosingParenthesis: if it cant find the closing ) of 
                                         the method signature
            
        '''        
        current_position = index        
        current_line = content[index]        
        
        visibility = self.check_visibility(current_line)
        is_static = self.has_any_keyword(current_line, ['static'])
        is_abstract = self.has_any_keyword(current_line, ABSTRACT_KEYWORDS) or class_model.is_interface

        current_line = self.remove_keywords(current_line, [visibility])        
        current_line = self.remove_modifiers(current_line)

        signature = current_line.strip()
        if not ')' in current_line:
            # in this case the signature of the method is in only one
            # line. For example:
            #   public void Foo(int a, int b, int c,
            #                   int d)
            current_position += 1
            while True:

                if current_position >= len(content):
                    raise MissingClosingParenthesis(index)

                signature += content[current_position].strip()
                if ')' in content[current_position]:
                    break
                current_position += 1



        if not is_abstract:
            # now move the index to the end of the method code
            # the abstract method only have thier definitions, so this
            # isn't necessary

            # take into account that the definition of the method can
            # only be of one line.
            if '{' in content[current_position] and \
                    (content[current_position].count('{') ==
                            content[current_position].count('}')):
                current_position += 1
            else:
                opened_keys = 0
                if '{' in content[current_position]:
                    opened_keys = 1

                started_method = False
                current_position += 1
                while True:
                    if current_position == len(content):
                        raise MissingClosingMethod(index)

                    line = content[current_position]
                    if self.is_comment(line):
                        # remove all lines inside the comment to take into
                        # account that comented lines could have "}" or "{"                        
                        current_position = self.move_to_documentation_end(content, current_position)                                                
                        continue

                    started_method = started_method or opened_keys > 0
                    opened_keys = opened_keys + line.count('{') - line.count('}')
                    current_position += 1
                    # take into account that the next line of the method definition
                    # could be another thing that isn't the openin. For example:
                    #   public Foo()
                    #       : base(1)
                    #   {
                    #       // do something
                    #   }
                    if opened_keys == 0 and started_method:
                        break
        else:
            current_position += 1

        # remove all the code of the signature
        if '{' in signature:
            signature = signature[:signature.index('{')].strip()

        if 'where' in signature and ':' in signature and signature.index('where') > signature.index(')'):
            # take into account methods that uses templates with conditionals.
            signature = signature[:signature.index('where')].strip()
        elif ':' in signature:
            # take into account that it cant be an inline constructor.
            # for example:
            #   public MyClass(): this("foo") {}
            signature = signature[:signature.index(':')].strip()


        
        tmp = signature[:signature.index('(')].strip()
        # take into account if the method definitions is an operator
        # definition.
        if self.has_any_keyword(tmp, ['operator']):
            return (current_position, None)
        
        # remove the parameters of the signature
        if len(tmp.split(' ')) == 1:
            # the the method is a constructor, and the name
            # is the value
            name = tmp
            return_type = 'void'
        else:
            return_type, name = self.get_type_and_name(tmp, index)
            

        long_documentation = self.get_documentation_string(content, index)

        # the c_sharp documentation is basically an xml.
        try:
            dom = parseString("<xml>%s</xml>" % long_documentation)
            short_documentation = dom.getElementsByTagName("summary")[0].childNodes[0].data
        except:
            # to take into account that the documentation isn't an xml, becuase
            # it was worng
            short_documentation = long_documentation

        
        LOGGER.debug("Found method: %s", name)        
        return (current_position,
                Method(name, class_model, signature, visibility,
                          short_documentation, long_documentation, is_static),
                )
        
    
        