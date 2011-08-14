#/usr/bin/python

"""
This is a script to migrate users from LDAP to Plone internal user management.
I know this is damn ugly, but I needed to make some tweaks to bypass Zope's security policies, i.e. importing other classes
@author: Katrin Krieger <kkrieger@iws.cs.uni-magdeburg.de>
"""

import ldap
import sys
#from Products.CMFCore.utils import getToolByName
#from zLOG import LOG, INFO, ERROR
from ldap.cidict import cidict



def ldap_migration(self):    
    #REQUEST = context.REQUEST
    #RESPONSE = REQUEST.RESPONSE 
    #regtool = getToolByName(self, 'portal_registration')
    #grouptool = getToolByName(self, 'portal_groups') 
    index = 1
    imported_count = 0
    
    user_dn = None
    user_pw = None
    dump_dn = None
    
	#hatte einen Dump vom WDOK gezogen und in einen lokalen LDAP eingespielt, so dass ich ihn Ruhe rumprobieren konnte
    server = 'ldap://localhost'
    #filter = '(objectclass=*)'
    filter = 'cn=*';
    #attrs = ['*']
    attrs = None
    
    #usage="""Usage: %s user_dn dn
    
    #Log in as user_dn and dump the record for person dn.n\n """ % sys.argv[0]
    
    #if len(sys.argv) != 3:
    #    sys.stderr.write("Error: expected user_dn and dn.n\n")
    #    sys.stdout.write(usage)
    #    sys.exit(1)
    
    user_dn = "cn=Manager,dc=iws,dc=cs,dc=uni-magdeburg,dc=de"
    dump_dn = "dc=iws,dc=cs,dc=uni-magdeburg,dc=de"
    user_pw = "Asdf,." #yep i am lazy and don't want to type in the password everytime i want to start this script
	
    # Add a blank line...
    sys.stdout.write("\n")
    
    try:
        l = ldap.initialize(server)
        try:
            #l.start_tls_s()
            l.bind(user_dn, user_pw)
            result_set = []
            res = []
            timeout = 0
            raw_res = l.search( dump_dn, ldap.SCOPE_SUBTREE, filter,
                attrs )
            while 1:
                result_type, result_data = l.result(raw_res, timeout)
                if (result_data == []):
                    break
                else:
                    if result_type == ldap.RES_SEARCH_ENTRY:
                        result_set.append(result_data)
    
           
            if(raw_res):
                res = get_search_results( result_set )
            else:
                print "no raw_res"
              
            #record has attributes attrs and dn
            print res
            if res and not(res==[]):
              
                for record in res:
                    #do we have a user or a group? we handle users first
                    if ('OpenLDAPperson' in record.attrs['objectclass']):
                        # check if the desired attribute exists
                        
                        properties = {}
                        try:    
                            properties['user_name'] = record.attrs['uid']
                        except KeyError: 
                            print "No such key: uid"
                            properties['user_name'] = ""
                        try:
                            properties['fullname'] = record.attrs['cn']
                        except KeyError: 
                            print "No such key: cn"
                            properties['cn'] = ""
                        try:
                            properties['givenName']=record.attrs['givenName']
                        except KeyError: 
                            print "No such key: givenName"
                            properties['givenName'] = ""
                        try:
                            properties['email'] = record.attrs['mail']
                        except KeyError: 
                            print "No such key: mail"
                            properties['email'] = ""
                        try:
                            properties['sn'] = record.attrs['sn']
                        except KeyError: 
                            print "No such key: sn"
                            properties['sn'] = ""
                        try:
                            properties['major'] = record.attrs['departmentNumber']
                        except KeyError: 
                            print "No such key: departmentNumber"
                            properties['major'] = ""
                        try:
                            properties['personal_title'] = record.attrs['personalTitle']
                        except KeyError: 
                            print "No such key: personalTitle"
                            properties['personal_title'] = ""
                        try:
                            properties['student_id'] = record.attrs['employeeNumber']
                        except KeyError: 
                            print "No such key: employeeNumber"
                            properties['student_id'] = ""
                            
                        print properties
                        print "\n\n"
                   
                    try:
                        #regtool.addMember(record.attrs['uid'],record.attrs['userpassword'], properties=properties)
                        #print "Successfully added %s %s (%s) with email %s" % (first, last, id, email)
                        #LOG('ldap_migration', INFO, "Successfully added %s with email %s" % (id, record.attrs['mail']))
                        imported_count += 1
                    except ValueError, e:
                        pass
                        #LOG('ldap_migration', ERROR, "Could not add %s with email %s: %s" % (id, record.attrs['mail'],e))
                    
            print "Imported %s users to Plone" % (imported_count)
          
            #second loop for adding users to groups
            for record in res:
                if ('groupOfUniqueNames' in record.attrs['objectclass']):
                    #extract group name
                    #groupname = record.attrs['cn'][0]
                    #grp = grouptool.getGroupById(groupname)
                    #fetch users
                    listOfUsersOfGroup = record.attrs['uniquemember']
                    for users in listOfUsersOfGroup:
                        #we just want the uid, not cn
                        if not(users.startswith("cn")):
                            print "adding user %s to group %s " % ((users.partition(",")[0]).partition("=")[2], groupname)
                            #grp.addMember((users.partition(",")[0]).partition("=")[0])
                else:
                    pass
    
        except ldap.INVALID_CREDENTIALS:
            print "Your username or password is incorrect."
            sys.exit()
        except ldap.LDAPError, e:
            if type(e.message) == dict:
                for (k, v) in e.message.iteritems():
                    sys.stderr.write("%s: %sn" % (k, v) )
            else:
                sys.stderr.write(e.message)
            sys.exit(1)
    
    finally:
        l.unbind()
   
def get_search_results(results):
    """Given a set of results, return a list of LDAPSearchResult
    objects.
    """
   
    res = []
    dn = ''
    if type(results) == tuple and len(results) == 2 :
       # LOG('ldap_migration', ERROR, "foobar")  
        (code, arr) = results
    elif type(results) == list:
        arr = results

    if len(results) == 0:
        return res

    for item in arr:
        (dn, attrs) = item[0]
        cidict(attrs)
        res.append( (dn,attrs) )
        
def main():
    ldap_migration("foo");

if __name__ == "__main__":
    main()

