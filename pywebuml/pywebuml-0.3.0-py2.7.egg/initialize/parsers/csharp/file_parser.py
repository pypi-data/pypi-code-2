# -*- coding: utf-8 -*-
'''
File C# parser.

@author: tzulberti
'''
from logging import getLogger

from pywebuml.initialize.parsers.base_typed.file_parser import AbstractStaticTypeFileParser
from pywebuml.initialize.parsers.csharp.class_parser import CSharpClassParser
from pywebuml.initialize.parsers.constants import (
                    PREPROCESSOR_DIRECTIVES,
                    SIMPLE_PREPROCESSOR_DIRECTIVES,
                    CLASS_KEYWORDS,
                    )

LOGGER = getLogger(__name__)



class CSharpFileParser(AbstractStaticTypeFileParser):
    ''' Given a C# file it will parse it's content an return
    a list of the parsed classes.
    '''

    def get_class_parser(self):
        return CSharpClassParser()


    def clean_content(self, content):
        ''' Removes all the decoratos and the code that won't
        be compiled taking into account the preprocessor directives.

        :see:
            `AbstractStaticTypeFileParser.clean_content`
        '''
        if self.has_preprocessor_directive(content):
            # take only into account the true conditions.
            content = self.remove_preprocessor_code(content)

        content = filter(lambda l : not l.startswith('['), content)
        return content


    def get_current_namespace(self, content):
        ''' Return the global namespace.
        If there is a namespace definition, then it will be updated
        in the ``should_ignore_line` method.

        :see:
            `AbstractStaticTypeFileParser.get_current_namespace`
        '''
        return 'global'


    def should_ignore_line(self, current_line, content):
        ''' Wil ignore the line if it is:
        - an import (using)
        - defines a namespace. In this case, it will update the
          current_namespace value.

        :see:
            `AbstractStaticTypeFileParser.should_ignore_line`
        '''
        if self.has_any_keyword(current_line, ['using']):
            self.index += 1
            return True
        elif self.has_any_keyword(current_line, ['namespace']):
            current_line = self.remove_keywords(current_line, ['namespace'])
            if '{' in current_line:
                current_line = current_line[:current_line.index('{')]
            else:
                # if the "{" isn't in the next line, then
                # it will be in the following..
                self.index += 1
            self.current_namespace = current_line.strip()
            self.index += 1
            return True
        elif '}' in current_line and not self.has_any_keyword(current_line, CLASS_KEYWORDS):
            # it is closing the current namespace
            self.current_namespace = 'global'
            self.index += 1
            return True
        else:
            return False


    def has_preprocessor_directive(self, content):
        ''' Identifies if the content of the file has a preprocesor directive.

        :parameters:
            content: list(str)
                the lines of the file.

        :returns:
            True if the file has a preprocesor directive.
        '''
        for line in content:
            if self.has_any_keyword(line, PREPROCESSOR_DIRECTIVES):
                return True

        return False

    def remove_preprocessor_code(self, content):
        ''' Removes the part of the content of the file
        that are code that won't be compiled taking into account the
        content of the file.

        For example in the following file::

            #define foo
            #if foo
                public class Bar {}
            #endif

        the class Bar will be returned. By if the definition of `foo` is
        commented or isn't found then an empty file might be returned.


        :parameters:
            content: list(str)
                the content read of the file. It must have a precompiler
                directive.

        :returns:
            the content of the file without any precompiler directive,
            and the actual code taking into account the definitions, if any.
        '''
        res = []
        # the names of the defined symbols
        defined = []

        # is true if any #if, #elif was true. It is used to take
        # into account that only one #if, #elif, #else can be true
        block_was_true = []


        index = 0
        while index < len(content):
            line = content[index]
            if not self.has_any_keyword(line, PREPROCESSOR_DIRECTIVES):
                # if there is no condition defined, then this line should
                # be added.
                res.append(line)
            else:
                # check that the preprocessor condition is one that changes
                # the code of the file.
                if not self.has_any_keyword(line, SIMPLE_PREPROCESSOR_DIRECTIVES):
                    is_current_block_valid = False

                    if not (line.startswith('#else') or line.startswith('#endif')):
                        # all the other lines have some symbol, so I should get it
                        symbol = line[line.index(' '):]

                    if line.startswith('#if'):
                        is_current_block_valid = symbol in defined
                        block_was_true.append(is_current_block_valid)

                    elif line.startswith('#define'):
                        defined.append(symbol)
                    elif line.startswith('#undef'):
                        defined.remove(symbol)
                    elif line.startswith('#endif'):
                        block_was_true.pop()
                    elif line.startswith('#else'):
                        if not block_was_true[len(block_was_true) -1]:
                            # the #else condition will be true if all the #if, #elif
                            # were false.
                            block_was_true.pop()
                            block_was_true.append(True)
                            is_current_block_valid = True

                    else:
                        # the line starts with 'elif'
                        # the elif will only be used if the condition was false
                        if not block_was_true[len(block_was_true) -1]:
                            block_was_true.pop()
                            is_current_block_valid = symbol in defined
                            block_was_true.append(is_current_block_valid)

                    # will remove the lines of the blocks that aren't true
                    if self.has_any_keyword(line, ['#if', '#elif', '#else']) \
                            and not is_current_block_valid:
                        nested_index = index
                        unused_opened_ifs = 0
                        while nested_index < len(content):
                            nested_index += 1
                            nested_line = content[nested_index]
                            if self.has_any_keyword(nested_line, ['#if']):
                                unused_opened_ifs += 1
                            elif self.has_any_keyword(nested_line, ['#endif']) \
                                    and unused_opened_ifs > 0:
                                unused_opened_ifs -= 1
                            elif self.has_any_keyword(nested_line, ['#elif', '#else', '#endif']) \
                                    and unused_opened_ifs == 0:
                                # in this case a new block begins so, it should
                                # be taken into account
                                break
                        index = nested_index - 1


            index += 1

        return res


