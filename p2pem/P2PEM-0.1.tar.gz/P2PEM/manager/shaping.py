import shapy
from shapy.emulation.shaper import Shaper
import imp
import sys
import os

from traffic_stats import TrafficStats
from P2PEM import loggs
import executor
import shape_etchosts



def fixsrcip(ip_addr, env, logger): 
    dir = os.path.dirname(__file__)
    dir = os.path.realpath(dir)
    path = os.path.join(dir, "fixsrcip-0.1")
    path = os.path.join(path, "fixsrcip.so")
    if os.path.exists(path):
        
        if 'LD_PRELOAD' in env:
            env["LD_PRELOAD"] = str(env["LD_PRELOAD"]) + ":" +path
        else:
            env["LD_PRELOAD"] = path
        env["FIXSRCIP"] = ip_addr
    else:
        logger.warning("Run peer - Could not run in bind_send mode. '%s' not found. Try to build the file." % path)
    logger.info("Run peer - Running peer in bind_send mode: ip_addr=%s" % ip_addr)
    return env

def forcebind(ip_addr, env, logger):
    dir = os.path.dirname(__file__)
    dir = os.path.realpath(dir)
    path = os.path.join(dir, "force_bind-0.4")
    path = os.path.join(path, "force_bind.so")
    if os.path.exists(path):
        
        if 'LD_PRELOAD' in env:
            env["LD_PRELOAD"] = str(env["LD_PRELOAD"]) + ":" +path
        else:
            env["LD_PRELOAD"] = path
        env["FORCE_BIND_ADDRESS"] = ip_addr
    else:
        logger.warning("Run peer - Could not run in bind_recv mode. '%s' not found. Try to build the file." % path)
    logger.info("Run peer - Running peer in bind_recv mode: ip_addr=%s" % ip_addr)
    return env

class ShapeManager(object):
    """
    Basic manager of traffic shaping.
    """
    
    MODE_MAP = {'bind_send': fixsrcip,
            'bind_recv': forcebind,
            }
    """
    bind_send - bind IP address to sending sockets
    bind_recv - bind IP address to recieving sockets
    """
    
    NETWORK_MASK = '%i.%i'   
    

    
    def __init__(self, peer_dev, no_shape, shape_modes, network, passwd):
        """
        params:
           peer_dev - network interface to create IP addresses on
           no_shape -  list of ports to exclude from shaping
           shape_modes - list of keys from MODE_MAP
           network - network mask /24, format 'x.x.'
           passwd - root password or None 
        """
        
        self.logger = loggs.used_logger
        self.network = (network) + self.NETWORK_MASK
        self.peer_dev = peer_dev
        
        if not passwd:
            passwd = ''
        settings = imp.new_module('shapy_settings')
        sys.modules.update(shapy_settings=settings)
        setattr(settings, 'SUDO_PASSWORD', passwd)
        setattr(settings, 'EMU_INTERFACES', (peer_dev, 'lo'))
        setattr(settings, 'EMU_NOSHAPE_PORTS', no_shape)
        shapy.register_settings('shapy_settings')
        self.shapr = Shaper()

        self.logger.info("Init: Peer_interface=" + str(self.peer_dev))
        self.__set_shape_mode(shape_modes)
        self.shaped = set()
        directory = os.path.dirname(os.path.realpath(__file__))
        path = os.path.join(directory, "shape_etchosts.py")
        self.etc_shape_path = path
        
        
    def is_shaped(self, id):
        """
        Returns True if id shaped.
        params:
            id - id or ip
        returns:
            boolean
        """
        
        return self.get_ip_address(id) in self.shaped
        
    def __convert_id_to_ip(self, id):
#        ne x.x.x.0 - adresa site, a ne x.x.x.255 - broadcast, takze modulo 254 + 1 ... rozsah 1 - 254
        net = id / 254
        if id < 255:
            return self.network % (net, (id) )
        else:
            return self.network % (net, (id % 254) + 1)

        
    def get_ip_address(self, id):
        """
        Converts id to ip address.
        params:
            id
        returns:
            ip
        """
        
        if isinstance(id, int):
            return self.__convert_id_to_ip(id)
        else:
            return id
        
    def get_ip_addresses(self, ids):
        """
        Converts ids to ips address.
        params:
            id - list of ids
        returns:
            ip - list of ips
        """
        
        ip_addrs = [  self.get_ip_address(id) for id in ids  ]
        return ip_addrs
        
    def run_node(self, identif, command, env):
        """
        Creates network identity for a peer.
        params:
            identif - id or ip
            command - command that will be used to run the peer
            env - environment variable that will be used to run a peer
        returns:
            command - can be modified
            env - can be modified
        """
        
        ip_addr = self.get_ip_address(identif)
        executor.execute_as_root('ip addr add %s/24 dev %s' % (ip_addr, self.peer_dev))
        

        for mode in self.shape_modes:
            env = mode(ip_addr, env, self.logger)
        
        return (command, env)
    
    def tear_peer(self, identif):
        """
        Tears the network identity of a peer.
        params:
            identif - id or ip
        """
        
        ip_addr = self.get_ip_address(identif)
        executor.execute_as_root('ip addr del %s/24 dev %s' % (ip_addr, str(self.peer_dev)))
    
    def tear_down(self):
        """
        Tears down all shaping related settings.
        """
        
        self.logger.info("Tear down - shaping")
        
        executor.execute_as_root_simple("python %s tear_etc_hosts" % self.etc_shape_path)
        self.logger.info("Tear down - removed hosts from " + shape_etchosts.etc_hosts)
        
        self.shapr.teardown_all()
        
        self.shaped = set()
        
        
    
    def init(self, ids):
        """
        Initializes shaping. May be called only once or after tear_down.
        params:
            ids - ids or ips of all peer that could be shaped
        """
        
        if not ids:
            return

        ip_addrs = self.get_ip_addresses(ids)
        ips = ' '.join(ip_addrs)

        executor.execute_as_root_simple("python %s init_etc_hosts %s" % (self.etc_shape_path, ips))

        self.logger.info("Scenario pre - added hosts to " + shape_etchosts.etc_hosts + ": ip_addrs="+ `ip_addrs`)  

   

    def __set_shape_mode(self, shape_modes):

        self.shape_modes = list()
        
        for mode in shape_modes:
            if mode in self.MODE_MAP:
                self.shape_modes.append(self.MODE_MAP[mode])
            else:
                shape_modes.remove(mode)
                
        self.logger.debug("Init: Shaping_modes=%s" % str(shape_modes))

    def reset_all(self):
        """
        Resets all shaping 
        """
        
        self.shapr.reset_all()
        self.shaped = set()
    
    def shape(self, delay, upload, download, ids):
        """
        Shapes peers.
        params:
            delay - int, peer delay in ms
            upload - int, peer upload limit in Kb/s
            download - int, peer download limit in Kb/s
            ids - list of ids or ips to be shaped
        """
        
        ip_addrs = list()
        for id in ids:
            ip_addrs.append(self.get_ip_address(id))
        
        self.shapr.set_shaping({tuple(ip_addrs): {'delay': delay, 'upload': upload, 'download': download}})
        
        self.shaped.update(ip_addrs)
        
        self.logger.info("Set shaping: delay=" + str(delay) + " upload_speed=" + str(upload)+ " download_speed=" +str(download) +  " ip_addresses=" + str(ip_addrs))
 
class ShapeWithStats(ShapeManager, TrafficStats):
    """
    Extended manager of traffic shaping, enables collecting of traffic statistics.
    """
    
    
    def __init__(self, peer_dev, no_shape, shape_modes, network, passwd):
        """
        See ShapeManager for the desctiption of params.
        """
 
        ShapeManager.__init__(self, peer_dev, no_shape, shape_modes, network, passwd)
        TrafficStats.__init__(self)
        self.init_stats()
        
        self.stats['up'] = {}
        self.stats['down'] = {}

    def set_stats(self, all=list(), up=list(), down=list()):
        """
        Adds peers to monitored peers.
        params:
            all - list of ips/ids, to monitore upload and download
            up - list of ips/ids, to monitore upload
            down - list of ips/ids, to monitore download
        returns:
            boolean - False if stats are running
        """
        
        if self.is_stopped() or not self.thread:
            
            up = self.get_ip_addresses(up)
            down = self.get_ip_addresses(down)
            all = self.get_ip_addresses(all)        
            upn = list()
            downn = list()
            upn.extend(up)
            downn.extend(down)
            upn.extend(all)
            downn.extend(all)
            up = self.shaped.intersection(upn)
            down = self.shaped.intersection(downn)
            for ip in down:
                self.stats['down'][ip] = {}
                self.stats['down'][ip]['stats'] = list()
                self.stats['down'][ip]['total'] = 0
                
            for ip in up:
                self.stats['up'][ip] = {}
                self.stats['up'][ip]['stats'] = list()
                self.stats['up'][ip]['total'] = 0
            return True
        return False    
   
    def _stats(self):
    
        for ip in self.stats['up'].keys():
            up, down = self.shapr.get_traffic(ip)
            self.stats['up'][ip]['stats'].append(up - self.stats['up'][ip]['total'])
            self.stats['up'][ip]['total'] = up
            
        for ip in self.stats['down'].keys():
            up, down = self.shapr.get_traffic(ip)
            self.stats['down'][ip]['stats'].append(down - self.stats['down'][ip]['total'])
            self.stats['down'][ip]['total'] = down

    def reset_all(self):
        """
        Reset shaping and collecting of statistics.
        """
        
        super(ShapeWithStats, self).reset_all()
        self.reset_stats()
    
    def reset_stats(self):
        """
        Resets collecting of statistics.
        """
        
        TrafficStats.reset_stats(self)
        self.stats['ip'] = {}
        self.stats['down'] = {} 
    
    def tear_down(self):
        """
        Tears down shaping and statisctics.
        """
        
        ShapeManager.tear_down(self)
        if not self.is_not_running():
            self.stop_stats()
