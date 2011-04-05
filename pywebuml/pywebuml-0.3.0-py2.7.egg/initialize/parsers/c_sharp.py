# -*- coding: utf-8 -*-

"""
Parse for C# files.
"""
from logging import getLogger
from xml.dom.minidom import parseString

from pywebuml.initialize.parsers.base import BaseParser
from pywebuml.main import db
from pywebuml.models import Class, ClassInheritence, ClassImplements, \
                            Attribute, Method, VISIBILITY_VALUES, InnerClass

from pywebuml.initialize.parsers.exceptions import (
                    MissingOpeningClassDefinition,
                    MissingClosingClassDefinition,
                    MissingClosingParenthesis,
                    MissingClosingMethod,                    
                    MissingClosingKeyAttributeDefinition,
                    )

from pywemuml.initializer.parsers.constants import (
                    MODIFIERS,
                    ABSTRACT_KEYWORDS,
                    CLASS_KEYWORDS,
                    CONST_KEYWORDS,
                    COMPILER_DIRECTIVES
                    ) 


LOGGER = getLogger(__name__)



class CSharpParser(BaseParser):

    def __init__(self):
        self.index = 0
        self.res = []

    def parse_content(self, content):
        """ Parse the content of the file. The file should have the
        following structure:

        /// ==================================
        /// License
        /// =================================
        /// Class documentation
        /// =================================
        /// Other documentation (not used, not a must)

        public class Foo : Bar
        {
            private int a;

            public ToString()
            {
                return "Foo"
            }
        }


        NOTE:
        - The empty lines aren't important
        - where the "{" and "}" isn't important

        """
        

    def parse_class(self, content, current_namespace = 'global', owner=None):
        


    def _is_comment(self, current_line):
        """ Identifies if the current line is a comment.

        :parameters:
            current_line: str
                the line that will be parsed if it isn't a comment.

        :returns:
            True if it is a comment.
        """
        return (current_line.startswith('//') or
                current_line.startswith('///') or
                current_line.startswith('/*') or
                current_line.startswith('*') or
                current_line.startswith('*/')
                )


    

    



    


      




    




    

    def _find_partial_class(self, package_name):
        """ Used to search the other part of the definiton of the class.
        This happens when the definition is partial, so all the parts
        should be joined.

        :parameters:
            package_name: str
                the name of the class to find.

        :returns:
            the `pywebuml.models.Class` that that class had. Returns None
            if the class hasn't been defined.
        """
        # Can't use Class.query because isn't inside a request.
        # see: http://flask.pocoo.org/mailinglist/archive/2010/10/14/flask-sqlalchemy-query-property
        query = db.session.query(Class)
        query = query.filter_by(package = package_name)
        return query.first()



    


