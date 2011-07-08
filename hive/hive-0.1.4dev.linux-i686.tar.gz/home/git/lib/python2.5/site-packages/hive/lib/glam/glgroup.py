#!/usr/bin/python2

''' Representing a group
'''

import re

class GLGroup:
    ''' Representing a group '''
    def __init__(self, name, member_list):
        '''
        name: the group name('@' prefix)
        member_list: a list of the member_list
        '''
        self.name = name
        self.member_list = member_list
        self.expanded_member_list = []
        self.deleted = False
        self.check_parameters()

    def check_parameters(self):
        ''' Checks if parameters are valid '''
        if not (isinstance(self.name, (str, unicode)) and
                isinstance(self.member_list, list)):
            raise TypeError('Parameters type invalid.')
        if not self.name.startswith('@'):
            raise ValueError('Group name should starts with "@".')

    def get_id(self):
        ''' ID '''
        return '@' + self.name[self.name.find('_')+1:]

    @staticmethod
    def parse_id(group_id):
        ''' Returns repo name and group name'''
        return group_id[1:group_id.find('_')], '@' + group_id[group_id.find('_')+1:]

    @staticmethod
    def expand(member_list, group_list):
        ''' Expands a list of members '''
        result = []
        for member in member_list:
            if not member.startswith('@') and not member in result:
                result.append(member)
            else:
                # Member is a group
                for group in group_list:
                    if group.name == member:
                        # Avoid repeat expanding group
                        group_list.remove(group)
                        tmp = GLGroup.expand(group.member_list, group_list)
                        for item in tmp:
                            if not item in result:
                                result.append(item)
                        break
        return result

    def dumps(self):
        ''' Returns a string representing the group '''
        if not self.deleted:
            return '%s = %s\n' % (self.name, ' '.join(self.member_list))
        else:
            return ''

    def delete(self):
        ''' Delete this group '''
        self.deleted = True
        return True

    def join(self, element):
        ''' element is a group or user '''
        assert isinstance(element, (str, unicode))
        assert re.match('@?\w+', element) != None
        if not element in self.member_list:
            self.member_list.append(element)

    def leave(self, element):
        ''' element is a group or user '''
        assert isinstance(element, (str, unicode))
        assert re.match('@?\w+', element) != None
        if element in self.member_list:
            self.member_list.remove(element)

    def to_dict(self):
        ''' Convert to dict '''
        return dict(name=self.name,
                    member_list=self.member_list)
