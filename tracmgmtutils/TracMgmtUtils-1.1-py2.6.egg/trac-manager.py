#!/usr/bin/env python
import trac_utils, sys

# options
base_path = "/Users/stefan/tmp/trac"
scm_paths = {'svn' : "/Users/stefan/tmp/svn", 'hg' : "/Users/stefan/tmp/hg", 'git' : "/Users/stefan/tmp/git"}
inherit_file = "/Users/stefan/tmp/trac/admin/conf/trac.ini"

if len(sys.argv) != 2:
    print "Wrong argument count."
    sys.exit()

command = sys.argv[1]
manager = trac_utils.TracInstanceManager(base_path, scm_paths, inherit_file)

if command == "list":
    for instance in manager.get_instances():
        print instance.get_name() + ": " + instance.get_description()
elif command == "create":
    name = raw_input("Name: ")
    user = raw_input("Main user: ")
    scm = raw_input("SCM (svn/hg/git): ")
    manager.new_instance(name, user, scm)

