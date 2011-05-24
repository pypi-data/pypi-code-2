import re
import socket
from P2PEM import loggs

class IDMOde():
    
    
    def __init__(self):
        self.logger = loggs.used_logger
        return 

class ByIPAddress(IDMOde):
    
     
    def id_from_range(self, ip_range):
        try:
            splitted = ip_range.rsplit('.')
            iprange = splitted[3]
            iprange = re.search("([0-9]{1,3})[-]([0-9]{1,3})", iprange).groups()
        except :
            try:
                iprange = re.search("([0-9]{1,3})", iprange).groups()
                iprange = (iprange[0], iprange[0])
            except:
                self.logger.warning("Wrong IP range - wrong range format: ip_range=" + ip_range)
                return False
        try:
            if (int(iprange[0]) == 0 or int(iprange[1]) >= 255):
                self.logger.warning("Wrong IP range - included subnet address or broadcast: ip_range=" + ip_range)
#                subnet address or broadcast
                return False
            
            splitted.pop()
            splitted.append(iprange[0])
            ip_first = '.'.join(splitted)
            
            splitted.pop()
            splitted.append(iprange[1])
            ip_last = '.'.join(splitted)
            
#            validate ip addresses
            socket.inet_aton(ip_first)
            socket.inet_aton(ip_last)
            
        except:
            self.logger.warning("Wrong IP range - wrong IPv4 address format: ip_range=" + ip_range)
            return False
        ip_addrs = list()
        for i in range(int(iprange[0]), int(iprange[1]) + 1):

            splitted.pop()
            splitted.append(str(i))
            ip_addrs.append('.'.join(splitted))
        
        return ip_addrs
    
    def peer_address(self, id, director):
        return id

class ByID(IDMOde):
    def id_from_range(self, id_range):
        try:

            idrange = re.search("([0-9]{1,3})[-]([0-9]{1,3})", id_range).groups()
        except:
            try:
                idrange = re.search("([0-9]{1,3})", id_range).groups()
                idrange = (idrange[0], idrange[0])
            except:
                self.logger.warning("Wrong ID range - wrong range format: id_range=" + str(id_range))
                return False
        
        ids = list()
        for i in range(int(idrange[0]), int(idrange[1]) + 1):
            ids.append(i)
        return ids
            
            
    
    def peer_address(self, id, director):

        return director.managers[director.peers[id]['manager']].get_ip_addr(id)
        
        