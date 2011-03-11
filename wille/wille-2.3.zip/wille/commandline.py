"""Command-line Execution Module
"""

import os
import sys

import argparse

from services import LocalService
from server import Server

def run_server():
	"""
	Command-line adapter for Wille server
	"""
	server = create_server()
	server.run(background=False, multi_thread=True)
	return

def run_app(urls,
		    appname=None,
		    services_dir_default=None):
	"""
	Command-line adapter for Wille Apps
		Arguments:
			urls 					- URL mappings
			appname					- Appname (extracted from sys.argv by default)
			services_dir_default	- Default services directory (used if none other specified)
	"""
	
	# Default appname
	if appname is None:
		appname = sys.argv[0].split('.')[0]
		
	# Default services dir
	if services_dir_default is None:
		services_dir_default = '../../services'
	
	workdir = os.getcwd()
	server = create_server(services_dir_default)
	server.quiet=False
	server.register_app(os.path.join(workdir, '..'), appname)
	if not server.quiet:
		print("App available at:\n\n%s\n" % server.resolve_app_url(appname))
	server.run(background=False, multi_thread=True)

def run_service():
	"""
	Command-line adapter for Wille Services
	
	EXPERIMENTAL -- has currently only limited support:
	
	- Does not support optional arguments
	
	- Does not support file-type arguments (@file)
	
	- Wille client is not passed to service
	
	"""
	
	# Find out service folder name based on current working dir
	servicename = os.path.split( os.getcwd() )[-1] 

	# Instantiate service
	service = LocalService('../', servicename, '../../libs')
	
	# Create option parser for this service
	required_params_str = ''
	if service.required_params:
		for param in service.required_params:
			required_params_str += '[%s]' % param
	
	usage = '%s %s\n\n%s' % ('%prog', required_params_str, service.description)
	parser = OptionParser(usage=usage)
	parser.set_conflict_handler("resolve")
	parser.add_option("-d", "--debug", action="store_true", dest="debug", default=False,
					  help="Debug mode: Print debugging messages to stdout")
	#if service.all_params:
	#	for param in service.all_params:
	#		parser.add_option("", ("--%s" % param), dest=param)
	(options, args) = parser.parse_args()
	
	# Prepare parameters for service execution
	
	# Start with empty dictionary
	params = dict()
	if service.all_params:
		for param in service.all_params:
			params[param] = ''  

	# Add required parameters
	count = 0
	if service.required_params:
		for param in service.required_params:
			# Missing arguments?
			if not len(args)>count:
				print("Error: required parameters missing. See --help for details")
				sys.exit(-1)
				
			# Arg found -> add to params
			params[param] = args[count]
			count += 1

	# Display retrieved parameters
	if options.debug:
		print ("Parameters:")
		for param in params:
			print ("\t%s=%s" % (param, params[param]))
	
	# Execute
	result = service.execute(params)
	
	# Print out result
	if type(result.data) == str:
		print result.data
	else:
		print result.data.encode('utf-8')
	
def create_server():
	""" Create a server instance with given command-line arguments """
	parser = argparse.ArgumentParser(prog='wille-server')
	parser.add_argument("-v", "--visibility", dest="visibility", default="localhost",
                  	    help="Restrict access to server (Valid values: localhost, public, or a list of IP addresses)")
	parser.add_argument("-p", "--port", type=int, dest="port", default=80,
					    help="Server port (Default: 80)")
	parser.add_argument("-s", "--services", dest="services_dir", default="services",
					    help="Directory from which services are loaded. Separate multiple directories with semicolon (;)")
	parser.add_argument("-a", "--apps", dest="apps_dir", default="apps", 
					    help="Directory from which apps are loaded")
	parser.add_argument("-u", "--data", dest="data", default="data", help="Project data directory")
	parser.add_argument("-n", "--neighbours", dest="neighbours", default="",
					    help="Comma-separated (,) list of addresses to neighbouring Wille nodes")
	parser.add_argument("-d", "--debug", action="store_true", dest="debug", default=False,
					    help="Debug mode: Print debugging messages to stdout")
	parser.add_argument("-r", "--reloader", action="store_true", dest="reloader", default=False,
					    help="Reload Python source codes whenever they change (slow, but good for developers!)")
	parser.add_argument("-q", "--quiet", action="store_true", dest="quiet", default=False,
					    help="Quiet operation; print as few messages as possible")
	parser.add_argument("-f", "--profiles", dest="profiles", default="",
					    help="Comma-separated (,) list of profiles to load")
	parser.add_argument('project', nargs=1, default='.', help='Directory to load Wille project from (default=.)')
	
	# Add default value for project if its not already provided
	DEFAULT_PROJECT_DIR = '.'
	if len(sys.argv)<= 1:
		sys.argv.append( DEFAULT_PROJECT_DIR )
	if len(sys.argv)>2:
		first_char = sys.argv[1][-1]
		if first_char == '-':
			sys.argv.append( DEFAULT_PROJECT_DIR )
	
	# Parse args
	args = parser.parse_args()

	if not args.quiet:
		print("Starting Wille Server")
		print("For details on command-line usage, run with '-h' or '--help'") 
	
	# Load project from different folder?
	project_dir = args.project[0]
	wille_root_dir = project_dir
	args.services_dir = os.path.join( wille_root_dir, args.services_dir )
	args.apps_dir = os.path.join( wille_root_dir, args.apps_dir )
	args.data = os.path.join( wille_root_dir, args.data )
	
	server = Server(args.port, args.visibility.split(','), args.services_dir, \
				    args.apps_dir, wille_root_dir, args.data, args.profiles, \
				    args.neighbours.split(','), args.quiet, args.debug, \
				    args.reloader)
	
	return server
