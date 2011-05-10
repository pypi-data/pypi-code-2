# coding=utf-8
'''
Created on 17-aug-2009

@author: jm
'''

from zope.interface import implements
from ldapadapter.interfaces import ILDAPAdapter, ILDAPConnection, InvalidCredentials

dir = {'ou=users,dc=test' : [{'entry':(u'cn=André de Chimpansee,ou=users,dc=test',
                                          {'dn':[u'cn=André de Chimpansee,ou=users,dc=test'],
                                           'cn':[u'André de Chimpansee'],
                                           'sn':[u'André'],
                                           'memberOf':[u'cn=Administrators,ou=groups,dc=test'
                                                       , u'cn=Domain Users,ou=groups,dc=test']
                                           },
                                        )
                                ,'password':'dreten'
                                ,'filters':[u'(objectClass=*)'
                                            , u'(cn=André de Chimpansee)'
                                            , u'(&(dn=cn=André de Chimpansee,ou=users,dc=test)(objectClass=user))'
                                            , u'(&(objectClass=user)(memberOf=cn=Administrators,ou=groups,dc=test))'
                                            , u'(&(objectClass=user)(memberOf=cn=Domain Users,ou=groups,dc=test))']}
                              ,{'entry':(u'cn=Louis Kolibri,ou=users,dc=test',
                                      {'dn':[u'cn=Louis Kolibri,ou=users,dc=test'],
                                       'cn':[u'Louis Kolibri'],
                                       'sn':[u'Louis'],
                                       'memberOf':[u'cn=Domain Users,ou=groups,dc=test']
                                       })
                              ,'password':'louis2000'
                              ,'filters':[u'(objectClass=*)'
                                          , u'(cn=Louis Kolibri)'
                                          , u'(&(dn=cn=Louis Kolibri,ou=users,dc=test)(objectClass=user))'
                                          , u'(&(objectClass=user)(memberOf=cn=Domain Users,ou=groups,dc=test))']}]
       ,'ou=groups,dc=test':[{'entry':(u'cn=Administrators,ou=groups,dc=test',
                                      {'dn':[u'cn=Administrators,ou=groups,dc=test'],
                                       'cn':[u'Administrators'],
                                       'description':[u'Users with Administrator Rights'],
                                       'member':[u'cn=André de Chimpansee,ou=users,dc=test']
                                       })
                                ,'password':'pwd'
                                ,'filters':[u'(objectClass=*)', u'(objectClass=group)'
                                            , u'(cn=Administrators)'
                                            , u'(dn=cn=Administrators,ou=groups,dc=test)'
                                            , u'(&(member=cn=André de Chimpansee,ou=users,dc=test)(objectClass=group))']}
                               ,{'entry':(u'cn=Domain Users,ou=groups,dc=test',
                                      {'dn':[u'cn=Domain Users,ou=groups,dc=test'],
                                       'cn':[u'Domain Users'],
                                       'description':[u'Users with a domain account'],
                                       'member':[u'cn=André de Chimpansee,ou=users,dc=test'
                                                 , u'cn=Louis Kolibri,ou=users,dc=test']})
                               ,'password':'pwd'
                               ,'filters':[u'(objectClass=*)', u'(objectClass=group)'
                                           , u'(cn=Domain Users)'
                                           , u'(dn=cn=Domain Users,ou=groups,dc=test)'
                                           , u'(&(dn=cn=Domain Users,ou=groups,dc=test)(objectClass=group))'
                                           , u'(&(member=cn=Louis Kolibri,ou=users,dc=test)(objectClass=group))'
                                           , u'(&(member=cn=André de Chimpansee,ou=users,dc=test)(objectClass=group))']}
                               ]
       }


class FakeLDAPAdapter(object):
    implements(ILDAPAdapter)
    
    def connect(self, dn=None, password=None):
        if dn:
            conn=None
            for e in dir['ou=users,dc=test']:
                if e['entry'][0] == dn:
                    if password:
                        if password == e['password']:
                            conn=FakeConnection()
                        else:
                            raise InvalidCredentials()
                    else:
                        conn=FakeConnection()
            if conn is None:
                raise InvalidCredentials()
            return conn
        else:
            return FakeConnection()
    
    
class FakeConnection(object):
    def search(self, base, scope='sub', filter='(objectClass=*)',
           attrs=None):
        ret=[]
        for entry in dir[base]:
            if unicode(filter) in entry['filters']:
                ret.append(entry['entry'])
        return ret
