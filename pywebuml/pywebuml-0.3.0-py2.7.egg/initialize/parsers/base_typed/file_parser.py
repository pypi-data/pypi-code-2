# -*- coding: utf-8 -*-
'''
File parser for static type languages.

@author: tzulberti
'''
from logging import getLogger

from pywebuml.initialize.parsers.base import BaseParser
from pywebuml.initialize.parsers.base_typed.base import BaseStaticTypeParser
from pywebuml.initialize.parsers.constants import CLASS_KEYWORDS


LOGGER = getLogger(__name__)


class AbstractStaticTypeFileParser(BaseParser, BaseStaticTypeParser):
    ''' Given the content of a file that is a static typed language,
    it will parse it's content and return a list of parsed classes.


    It has the following abstract methods:

    - clean_content: removes the decoratos and any other file content
      that shouldn't be parsed.

    - get_current_namespace: takes the responsability of of
      returning the namespace of the class.

    - should_ignore_line: indicates that the current line
      shouldn't be parsed.

    - get_class_parser: return the instance of `pywebuml.parsers.ClassParser`
      that will be used to parse the content of the file
    '''

    def __init__(self):
        self.current_namespace = ''
        self.class_parser = self.get_class_parser()
        self.index = 0

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
        res = []

        content = self.remove_comments(content)
        content = self.clean_content(content)
        current_line = None

        self.current_namespace = self.get_current_namespace(content)
        while True:
            current_line = content[self.index]

            if self.should_ignore_line(current_line, content):
                pass
            elif self.has_any_keyword(current_line, CLASS_KEYWORDS):
                # To take into account that some methods or enums, could
                # be defined before the class.
                self.index = self.parse_class_definition(filepath, content, self.index,
                                                    self.current_namespace, res)
            else:
                # iterate the method or enum that is outside the class
                opened = current_line.count('{') - current_line.count('}')
                current_position = self.index
                opened_keys = 0
                while True:
                    line = content[current_position]
                    opened_keys = opened_keys + line.count('{') - line.count('}')
                    current_position += 1

                    if opened_keys == 0:
                        break
                self.index = current_position


            if self.index >= len(content):
                break

        return res


    def remove_comments(self, content):
        ''' Remove all the comments of the code.

        :parameters:
            content: list(str)
                the content of the file

        :returns:
            the content of the file without any comment.
        '''
        position = 0
        res = []
        while position < len(content):
            line = content[position]
            if self.is_comment(line):
                position = self.move_to_documentation_end(content, position)
                continue

            if '//' in line:
                line = line[: line.index('//')].strip()

            if '/*' in line and '*/' in line:
                line = line[0: line.index('/*')].strip() + line[line.index('*/') + 2:].strip()
            elif '/*' in line:
                #TODO solve this problem
                raise Exception("Estoy jodido...")
            position += 1
            res.append(line)
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
        index, found_classes = self.class_parser.parse(filepath, content, index, current_namespace)
        res.extend(found_classes)
        return index

    def clean_content(self, content):
        ''' Returns the content of the file that should be parsed.
        It should be used to remove big blocks of code, it aid the method
        `should_line_be_ignored`.

        It should remove the file decorators, and the preprocessor directives
        (if any)

        :parameters:
            content: list(str)
                the whole content of the file.

        :returns:
            the new content (list(str)) that will be parsed.
        '''
        raise NotImplementedError('clean_content')


    def get_class_parser(self):
        ''' Returns the instance of the `pywebuml.parsers.ClassParsers`
        that will be used to parse the class code.

        :returns:
            an instance of `pywebuml.parsers.ClassParsers` that will
            get parse the file.
        '''
        raise NotImplementedError('get_class_parser')


    def get_current_namespace(self, content):
        ''' Returns the current package of the class.
        It C# is the namespace in which the class if found, and in java
        is the defined package.

        :returns:
            the package of the class that will be concatenated with the
            class name
        '''
        raise NotImplementedError('get_current_namespace')


    def should_line_be_ignored(self, current_line, content):
        ''' Indicates if the line should be parsed or ignored.
        It must update the `index` value. That value is used to get the line
        that will be parsed.

        :parameters:
            current_line: str
                the current line that is iterating.
            content: list(str)
                the cleaned content of the file.

        :return:
            True if the line should be ignored, else False.
        '''
        raise NotImplementedError('should_line_be_ignored')
