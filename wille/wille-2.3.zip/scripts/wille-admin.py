""" Wille Admin Scripts """
import os
import sys

# Create Project
def create_project(project_name):
    # Create folder
    os.mkdir(project_name)    
    os.mkdir(os.path.join(project_name, 'services'))
    os.mkdir(os.path.join(project_name, 'apps'))
    os.mkdir(os.path.join(project_name, 'libs'))
    os.mkdir(os.path.join(project_name, 'scripts'))
    
    # Done
    return("Created a skeleton for project '%s'" % project_name)

# Create Service
def create_service(service_name):
    # Parse path from service name
    service_path = service_name
    service_name = os.path.split(service_name)[-1]
    
    # Create path
    os.mkdir( service_path )
    f = open( os.path.join( service_path, 'willeservice.properties'), 'wt')
    f.write('# Service description (recommended)\n')
    f.write('description=\n\n')
    f.write('# Adapter (HTTPGet, PythonService, CommandLine, IsolatedCommandLine)\n')
    f.write('adapter=CommandLine\n\n')
    f.write('# Adapter command\n')
    f.write('adapter.command=servicename.exe\n\n')
    f.close()
        
    # Done
    return("Created a skeleton for service '%s'" % service_name)

# Create App
def create_app(app_name):
    # Parse app_name in case it contains a path
    app_path = app_name
    app_name = os.path.split(app_path)[-1]
    
    # Make App folder
    os.mkdir(app_path)
    
    # Create App property file
    f = open(os.path.join(app_path, 'willeapp.properties'), 'wt')
    f.write('description=%s\n' % app_name)
    f.close()
    
    # Create App script
    f = open(os.path.join(app_path, app_name+'.py'), 'wt')
    f.write('class IndexPage:\n')
    f.write('\tdef GET(self, request):\n')
    f.write('\t\t# (Insert your code here)\n')
    f.write('\t\treturn "Result view"\n\n')
    f.write('urls = ( ("/", IndexPage),)\n' )    
    f.close()
    
    # Done
    return("Created a skeleton for app '%s'" % app_name)

# Run Server
def run_server():
    import wille.commandline
    wille.commandline.run_server()

# Bind commands
commands = { \
        'createproject': (create_project, ('project_name',)),
        'createservice': (create_service, ('service_name',)),
        'createapp': (create_app, ('app_name',)),
        'runserver': (run_server, None),
}

# Print help
if len(sys.argv)<2 or sys.argv[1]=='-h':
    print("Usage: wille-admin [command]")
    print("")
    print("Available commands:")
    for command in commands:
        args_str = ''
        args = commands[command][1]
        if args:
            for arg in commands[command][1]:
                args_str = '%s [%s]' % (args_str, arg)
        print ("\t%s %s" % (command, args_str))
    sys.exit(1)

# Find and execute given command
commandname = sys.argv[1]

# Exists?
if commands.has_key(commandname):
    # Read command
    (command_callback, command_args) = commands[commandname]
    sys.argv = [sys.argv[0]] + sys.argv[2:]

    # Parse args    
    args = []
    if command_args:
        for argname in command_args:
            if len(sys.argv)<2:
                print ("Argument missing: %s" % argname)
                sys.exit(1)
            args.append( sys.argv[1] )
            sys.argv = [sys.argv[0]] + sys.argv[2:]
    
    # Run command
    try:
        result = command_callback(*args)
        if result:
            print result
    except Exception, e:
        print("Error while executing '%s':" % commandname)
        print(e)
        sys.exit(1)
        
else:
    # Not found
    print("Unknown command: '%s'" % commandname)
    print("Use -h option for help")
    sys.exit(1) 
