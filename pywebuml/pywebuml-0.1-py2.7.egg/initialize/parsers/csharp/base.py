'''
Created on 05/02/2011

@author: tzulberti
'''

from pywebuml.models import VISIBILITY_VALUES
from pywebuml.initialize.parsers.constants import (
                    COMMENTS_MARKERS,
                    MODIFIERS
                    )
from pywebuml.initialize.parsers.exceptions import (
                    EmptyNameException,
                    )



class BaseCSharpParser(object):
    ''' Has some common functionality for all the parsers.
    '''

    def is_comment(self, current_line):
        ''' Identifies if the current_line starts or is a comment.

        :parameters:
            current_line: str
                the line to identify if it is a comment.

        :return:
            True if the line is a comment, else false.
        '''
        #if  self.has_any_keyword(current_line, COMMENTS_MARKERS):
        #    return True

        for marker in COMMENTS_MARKERS:
            if current_line.startswith(marker):
                return True

        return False


    def move_to_documentation_end(self, content, index):
        ''' Returns the index in which the documentation finish.

        This should be used when there is a comment inside a class
        or method.

        For example:

        public class Foo {
            /**
            * This is some usless comment....
            */
        }

        :parameters:
            content: list(str)
                the whole content of the file.
            index: int
                from where check the content. The cotent[index] must
                be a comment.

        :returns:
            the index where the commented code finish, and continues the
            code.
        '''
        line = content[index]
        original = index
        if self.is_comment(line):
            # remove all lines inside the comment to take into
            # account that comented lines could have "}" or "{"
            index += 1
            opened_comments = 0
            if not line.startswith('//'):
                opened_comments = line.count('/*') - line.count('*/') - line.count('* /')
            if opened_comments > 0:
                while True:
                    try:
                        line = content[index]
                    except Exception, e:
                        # in this case the documents are wrong. For example:
                        # /*
                        #    /*
                        # */
                        # this will close both opened documented data
                        # TODO chech what to do in this case....
                        raise e

                    opened_comments += line.count('/*') - line.count('*/')- line.count('* /')
                    index += 1
                    if opened_comments == 0:
                        break
        return index


    def get_documentation_string(self, content, index):
        ''' Returns the string documentation from the current line.
        The documentation will be taken from the current line upwards.

        :parameters:
            content: list(str)
                the content of the file.
            index: int
                from where start getting the documentation.

        :return:
            the doc string for the current line.
        '''
        position = index -1
        res = ''
        while True:
            current_line = content[position]
            current_line = current_line.replace('* /', '*/')
            if self.has_any_keyword(current_line, COMMENTS_MARKERS):
                res = self.remove_keywords(current_line, COMMENTS_MARKERS)  + res
            else:
                break

            if position == 0:
                # get got to the start of the file.
                break

            position -= 1

        # remove all the documentations chars
        res = self.remove_keywords(res, COMMENTS_MARKERS)
        res = res.strip()
        if not res:
            # dont return an empty string
            res = None
        return res

    def has_any_keyword(self, current_line, keywords):
        ''' Search if the current_line has any of the keywords.

        :parameters:
            current_line: str
                the current line of the file
            keywords: list(str)
                the keywords to search in the line

        :returns:
            True if the current_line has any of the keywords, else False.
        '''
        # it has to be splited and can't check for each word to take
        # into account the name of the attribute or method. For example:
        #   public int myMethodclass();
        data = current_line.split(' ')
        data = map(lambda l: l.strip(), data)
        for keyword in keywords:
            if keyword in data:
                return True
        return False


    def remove_keywords(self, current_line, keywords):
        ''' Identifies which of the keywords can be in the current line and
        remove them.

        :parameters:
            current_line: str
                the current line of the file
            keywords: list(str)
                the keywords to remove of the line

        :returns:
            the line without the keywords.
        '''
        data = current_line.split(' ')
        data = map(lambda l: l.strip(), data)
        data = filter(lambda l: l.strip(), data)

        final = filter(lambda d: not d in keywords, data)
        return ' '.join(final)





    def check_visibility(self, line):
        ''' Returns the visibility of the line.

        :returns:
            one of the valid visibility for the line, that
            must be a class definition, attribute or method.
        '''
        # TODO se deberia hacer lo mismo que hace _has_keyword...
        for visibility in VISIBILITY_VALUES:
            if self.has_any_keyword(line, [visibility]):
                return visibility

        if self.has_any_keyword(line, ['internal']):
            return 'private'

        # return the default visibility for the line
        return 'protected'

    def remove_modifiers(self, line):
        ''' Removes all the modifiers from the line.

        :parameters:
            line: str
                the signature of a method, or the defintion of
                a class or attribute.

        :returns:
            the line without the modifiers.
        '''
        return self.remove_keywords(line, MODIFIERS)


    def get_type_and_name(self, current_line, index):
        ''' Return the variable type or the return class of the method.


        :parameters:
            current_line: str
                the complete definition attribute or method without any
                modifier.

        :returns:
            a (str, str) str with the type of the variable, and the name of
            the attribute.
        '''
        # can't use current_line.split(' '), becuase there can be more than
        # one space between the type and variable definition
        if ' ' not in current_line:
            raise EmptyNameException(current_line, index)

        variable_type, name = current_line.rsplit(' ', 1)
        variable_type = variable_type.strip()

        if ' ' in variable_type and not ('[]' in variable_type or '<' in variable_type):
            raise EmptyNameException(current_line, index)

        if ' ' in name or name == '':
            raise EmptyNameException(index, current_line)

        return (variable_type, name)

