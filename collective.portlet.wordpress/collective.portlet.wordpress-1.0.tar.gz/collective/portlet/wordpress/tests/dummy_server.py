import sys, os
import subprocess
import time
from BaseHTTPServer import HTTPServer 
from BaseHTTPServer import BaseHTTPRequestHandler

current_dir = os.path.dirname(__file__)
path_to_test_res = os.path.sep.join([current_dir] + ['data', 'test?feed=rss2'])


# this module is for modeling server that takes request and doesn't send answer
# for a long time
class MyHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        time.sleep(3)
        # we assume that portlet waits for response less than 30 sec
        # if it is not so we will be able to check if portlet receives test_file
        test_file = open(path_to_test_res)
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        for line in test_file.readlines():
            self.wfile.write(line)
        test_file.close()
        return 

def main():
    if sys.argv[1:]:
        port = int(sys.argv[1])
    else:
        port = 8500
    server_address = ('', port)
    
    try:
        httpd = HTTPServer(server_address, MyHandler)
        sys.stdout.write("I'm ready\n")
        sys.stdout.flush()
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
        
if __name__ == '__main__':
    main()
