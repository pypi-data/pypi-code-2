# -*- coding: utf-8 -*-
'''
File C# parser.

@author: tzulberti
'''
from logging import getLogger

from pywebuml.initialize.parsers.base import BaseParser
from pywebuml.initialize.parsers.csharp.base import BaseCSharpParser
from pywebuml.initialize.parsers.csharp.class_parser import CSharpClassParser
from pywebuml.initialize.parsers.constants import (
                    COMPILER_DIRECTIVES,
                    CLASS_KEYWORDS
                    )

LOGGER = getLogger(__name__)



class CSharpFileParser(BaseParser, BaseCSharpParser):
    ''' Given a C# file it will parse it's content an return
    a list of the parsed classes.
    '''

    def parse_content(self, filepath, content):
        ''' It will parse the content of the file.

        If the file has a compiler directive, then it will be ignore
        it by returning an empty list, because it is very difficult
        to take into account the changes that affect the compiler.


        :parameters:
            filepath: str
                the path and name of the file. The path will
                be realive to where the command was executed.
            content: list(str)
                the content of the file already modified
                by the base parser.

        :returns:
            a list of pywebuml.models.Class with it's
            methods and attributes.
        '''
        index = 0
        res = []
        if self._has_compiler_directive(content):
            # if there is a compiler directive, then ignore
            # the file because there could be problems when parsing
            # the data
            return []

        # remove all decorators.
        final_content = []
        for line in content:
            if not line.strip().startswith('['):
                final_content.append(line)

        content = final_content

        # use this kind of condition to take into account
        # that I might be necesary to go upper in the content
        # of the file
        current_line = None

        # remove all the decorators of the file.
        current_namespace = 'global'
        content = filter(lambda l : not l.startswith('['), content)
        while True:
            current_line = content[index]

            if self.is_comment(current_line):
                index = self.move_to_documentation_end(content, index)
            elif self.has_any_keyword(current_line, ['using']):
                index += 1
            elif self.has_any_keyword(current_line, ['namespace']):
                current_line = self.remove_keywords(current_line, ['namespace'])
                if '{' in current_line:
                    current_line = current_line[:current_line.index('{')]
                else:
                    # if the "{" isn't in the next line, then
                    # it will be in the following..
                    index += 1
                current_namespace = current_line.strip()
                index += 1
            elif current_line in ('}', '};'):
                # closing namepsace definition
                index += 1
                current_namespace = 'global'

            elif self.has_any_keyword(current_line, CLASS_KEYWORDS):
                # To take into account that some methods or enums, could
                # be defined before the class.
                index = self.parse_class_definition(filepath, content, index,
                                                    current_namespace, res)
            else:
                # iterate the method or enum that is outside the enum
                opened = current_line.count('{') - current_line.count('}')
                current_position = index
                opened_keys = 0
                while True:
                    line = content[current_position]
                    if self.is_comment(line):
                        current_position = self.move_to_documentation_end(content, current_position)
                        continue

                    opened_keys = opened_keys + line.count('{') - line.count('}')
                    current_position += 1

                    if opened_keys == 0:
                        break
                index = current_position


            if index >= len(content):
                break

        return res

    def parse_class_definition(self, filepath, content, index, current_namespace, res):
        ''' Parse the class, added it to res, and return the nwe index.

        :parameters:
            filepath: str
                the path of the current file.
            contennt: list(str)
                the content of the file
            index: int
                the current position where the class definition starts.
            current_namespace: str
                the current namespace where the class belongs.
            res: list(`pywebuml.models.Class`)
                the current classes found in the file, and where to add the
                result of parsing the file.

        :return:
            the index where the class definition ends. It is important to take
            into account that the index could not belong to the file, it the }
            clossing class was the last line of the file.
        '''
        class_parser = CSharpClassParser()
        index, found_classes = class_parser.parse(filepath, content, index, current_namespace)
        res.extend(found_classes)
        return index



    def _has_compiler_directive(self, content):
        ''' Identifies if the content of the file has a compiler directive.

        :parameters:
            content: list(str)
                the lines of the file.

        :returns:
            True if the file has a compiler directive.
        '''
        for line in content:
            if self.has_any_keyword(line, COMPILER_DIRECTIVES):
                return True

        return False

