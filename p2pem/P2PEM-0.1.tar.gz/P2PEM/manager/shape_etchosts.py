import sys
import string


START_MARK = '# CWC START_MARK #'
END_MARK = '# CWC END_MARK #'
etc_hosts = '/etc/hosts'

def tear_etc_hosts():
        lines = list()
        with open(etc_hosts, 'r') as efile:
            delete = False
            while True:
                line = efile.readline()    
                if string.find(line, '\n') == -1:
                    break
                
                if line.startswith(START_MARK):
                    delete = True
                
                if not delete:
                    lines.append(line)
                    
                if line.startswith(END_MARK):
                    delete = False
        with open(etc_hosts, 'w') as efile:
            efile.writelines(lines)
        
        
            
def init_etc_hosts(*args):    
        with open(etc_hosts, 'a') as efile:
            efile.write(START_MARK + '\n')
            ip_addrs = list()
            ip_addrs.extend(args)

            for id, ip_addr in zip(range(len(ip_addrs)), ip_addrs):
                efile.write(str(ip_addr) + '\t' + 'cwcpeer' +str(id)+'\n')
                ip_addrs.append(ip_addr)
                
            efile.write(END_MARK + '\n')

        
          
def main(argv=None):
    if argv is None:
        argv = sys.argv

    function_name = argv[1]
    module = sys.modules[__name__]
    if len(argv) > 2:
        arg = argv[2:]
        getattr(module, function_name)(*arg)
    else:
        getattr(module, function_name)()

            
if __name__ == "__main__":
    main()