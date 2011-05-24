import subprocess, shlex

import os
from time import sleep

import logging
from P2PEM import loggs
from P2PEM.loggs import GeneralLogger

from os import environ

from random import randint
from shaping import ShapeWithStats
import xmlrpclib
import executor

class DirectorHandler(logging.Handler):
    """
    Handler to log backwards to Director.
    """
    
    director_proxy = None
    
    DIR_LEVELS = {
                  logging.DEBUG: "debug", 
                  logging.INFO: "info",
                  logging.WARNING: "warning",
                  logging.CRITICAL: "critical",
                  }
    
    
    def __init__(self, dir_proxy):
        
        logging.Handler.__init__(self)
        self.director_proxy = dir_proxy
        
    
    def emit(self, record):
        msg = self.format(record)
        self.director_proxy.getattr(self.DIR_LEVELS[self.levelno])(msg)

class ManagerLogger(GeneralLogger):  
    """
    Extended GeneralLogger able to log backwards to Director.
    example log parameter format:
        log = {
               'mode': {'file': 'defub', 'console' : 'info', 'director' : 'warning'},
               'file_name': 'manager.log',
               'dir_url': 'http://10.0.0.1/8888', //url to connent to Direcotor
               'dir_name': 'Manager1',            //string used to format log messages (identifies the Manager) 
               }
        
    """

    def _set_dir_log(self):

        if ('mode' in self.log and 'director' in self.log['mode']) or 'mode' not in self.log:

            if 'dir_url' not in self.log:
                return None
            try:
                
                director_proxy = xmlrpclib.ServerProxy(self.log['dir_url'], allow_none=True)
                name = self.log['dir_name']
                
                dirhandler = DirectorHandler(director_proxy)
                sformatter = logging.Formatter("Manager: %s: %(levelname)s - %(name)s - %(message)s" % name)
                dirhandler.setFormatter(sformatter)
                
                return self._register_handler(dirhandler, 'director'), ""                

            except Exception:
                pass

        return None

    def _tor_set_logs(self):
        
        super(ManagerLogger, self)._tor_set_logs()
        
        self.LOGGING_DEFAULT_LEVEL = super(ManagerLogger, self).LOGGING_DEFAULT_LEVEL.update( 
                        {'director': logging.WARNING})
  
        self._register_log('director', self._set_dir_log)

  
class Manager(object):

    DEFAULT_SHAPER = {'peer_dev':'lo', 'no_shape': list(), 'modes':list()}
    DEFAULT_LOG = {'mode':{'file':'debug', 'console':'info'}, 'file_name':'manager.log'}
    DEFAULT_PEER_DEV = 'lo'
    DEFAULT_NO_SHAPE = list()
    DEFAULT_SHAPE_MODES = list()
    DEFAULT_NETWORK = "10.13."
    PEER_LOGS_DIR = "peer-logs"
    PEER_LOG_NAME = "peer-%s.log"
    PEER_ERROR_LOG_NAME = "peer-%s.err"
    
    
    def _set_shaping(self, shaper):
        
        if 'peer_dev' not in shaper:
            shaper['peer_dev'] = self.DEFAULT_PEER_DEV
        if 'no_shape' not in shaper:
            shaper['no_shape'] = self.DEFAULT_NO_SHAPE
        if 'modes' not in shaper:
            shaper['modes'] = self.DEFAULT_SHAPE_MODES
        if 'network' not in shaper:
            shaper['network'] = self.DEFAULT_NETWORK

        self.shaper = self._tor_get_shaper(shaper['peer_dev'], shaper['no_shape'], shaper['modes'], shaper['network'], shaper, executor.password) 

  
    def _tor__init__(self, *args):
        """
        To be overridden.
        Extends the init operation.
        params:
            args: extra arguments for the constructor method
        """
        return
    
    def _tor_get_logger(self, log):
        """
        To be overridden.
        returns:
            GeneralLogger instance or child.
        """
        return ManagerLogger(log, "ManagerLogger")
        

    def _tor_get_shaper(self, peer_dev, no_shape, modes, network, shaper, passwd):
        """
        To be overridden.
        returns:
            ManagerShaper instance or child.
        """
        return ShapeWithStats(peer_dev, no_shape, modes, network, passwd)

    def __init__(self,  shaper={}, swap_limit=100, log=None, sudo_passwd=None, *args):
        """
        params:
            shaper - dictionary with shaper settings
            swap_limit - int, when reached, logs as warning
            log - dictionary with log settings
            sudo_passwd - root passwd or None
        shaper keys: peer_dev, no_shape, modes, network (see ShapeManager init params)
        """
        

        loggs.used_logger = self._tor_get_logger(log or self.DEFAULT_LOG)
        
        executor.set_mode(sudo_passwd) 
        
        self.man_logger = loggs.used_logger
        self._set_shaping(shaper)
        self.swap_limit = swap_limit
        self.man_logger.info("Init: Swap_limit=%d" % swap_limit)
        
        self.process_id_map = {}
        """
            self.process_id_map[id]['process']    // process id
            self.process_id_map[id]['killed']     // True if killed (ip address still asigned)
            self.process_id_map[id]['logfile']    // file to save stdout of peer
            self.process_id_map[id]['logerrfile'] // file to save stderr of peer
        """
        self._init_peer_logs()
        self._tor__init__(*args)
        
    
    def start(self, identifs):
        """
        To be called from Director.
        Inits shaping.
        params:
            identifs - list of ids/ips
        """
        
        self.shaper.init(identifs)
        

       
    def _init_peer_logs(self):
        
        dirname = os.getcwd()
        path = os.path.join(dirname, self.PEER_LOGS_DIR)
        if not os.path.exists(path) or not os.path.isdir(path):
            os.mkdir(path)
        self.peer_log_dir = path
            
    def _tor_tear_down(self):
        """
        To be overridden.
        Extends the tear down method.
        """
        return
                
    def tear_down(self):
        """
        To be called from Director.
        Tears down the Manager.
        """
        self.man_logger.info("Tear down")

        self.shaper.tear_down()
        self._tear_perees()
        self._tor_tear_down()

        self.man_logger.info("Tear down - finished")
      
    def _tor_tear_peer(self, id, process_id):
        """
        To be overridden.
        Extends the tear peer method.
        params:
            id - id/ip, peer to tear
            process_id - id of peer's process
        """
        return
      
    def _tear_perees(self):


        for (id, process) in self.process_id_map.iteritems():
        
            try:
                self.shaper.tear_peer(id)
                self.process_id_map[id]['process'].kill()
                self._tear_peer_log_file(id)
                self._tor_tear_peer(id, process['process'].pid)

                self.man_logger.info("Tear down - killed peer: pid=%d, id=%s" % (process['process'].pid,str(id)))
            except Exception as e:
                self.man_logger.warning("Tear down peer - ERROR: peer_id=%s, process_id=%d, err=%s" % (str(id), process['process'].pid, e))
    
    def _tear_peer_log_file(self, id):    
        self.process_id_map[id]['logfile'].close()
        self.process_id_map[id]['logerrfile'].close()
    
    def _kill_peer_hard(self, id):
        
        try:
            process = self.process_id_map.get(id)
            
            self.shaper.tear_peer(id)
            
            self.process_id_map[id]['process'].kill()
            
            self._tor_tear_peer(id, process['process'].pid)
            
            self._tear_peer_log_file(id)
            
            self.process_id_map.pop(id)
            
            self.man_logger.info("Kill peer hard - killed peer: pid=" + str(process['process'].pid) + " id=" + str(id))
        except Exception as e:
            self.man_logger.warning("Kill peer hard - could not kill a peer: pid=" + str(process['process'].pid) + " id=" + str(id) + " err: " + str(e))
    
            
    def _tor_tear_peer_soft(self, id, process_id):
        """
        To be overridden.
        Extends kill_soft method and kill_soft_random.
        """
        self._tor_tear_peer(id, process_id)
    
    
    def _kill_peer_soft(self, id):
        try:
            
            process = self.process_id_map.get(id)

            self.process_id_map[id]['process'].terminate()
            self._tor_tear_peer_soft(id, process['process'].pid)
            self.process_id_map[id]['killed'] = True
            self._tear_peer_log_file(id)
            self.man_logger.info("Kill peer soft - killed peer: pid=" + str(process['process'].pid) + " id=" + `id`)
        except Exception as e:
            self.man_logger.warning("Kill peer soft - could not kill a peer: pid=" + str(process['process'].pid) + " id=" + `id` + " err: " + str(e))
        

    def _tor_get_command(self, ip_addr, env, *args):
        """
        To be overridden. Hook method.
        params:
            ip_addr - ip address of peer
            env - list of environment variables
            
        returns:
            string - command to launch peer
            string - log message
            env - can be modified
        """
        
        return "echo 'running peer'", "", env
        
    def _run_node(self, id, *args):

        if id in self.process_id_map and self.process_id_map[id]['killed'] == True:
            self.shaper.tear_peer(id)
            if not self.process_id_map[id]['process'].poll():
                self.process_id_map[id]['process'].kill()
                self.process_id_map.pop(id)
        
        if id in self.process_id_map:
            self.man_logger.warning("Run peer: Peer already running, id=%s" % id)
            return
        try:
            
            
            ip_addr = self.shaper.get_ip_address(id)          
            
            
            env = environ.copy()
            
            command, logmsg, env = self._tor_get_command(ip_addr, env, *args)
            
            (command, env) = self.shaper.run_node(id, command, env)
            
            self.man_logger.debug("Run peer: command=%s, env=%s" % (command, str(env)))

            
            pargs = shlex.split(command)
            
            logfile = open(os.path.join(self.peer_log_dir, self.PEER_LOG_NAME % str(id)), "a")
            
            logerrfile = open(os.path.join(self.peer_log_dir, self.PEER_ERROR_LOG_NAME % str(id)), "a")
            
            p = subprocess.Popen(pargs, env=env, stdout=logfile, stderr=logerrfile, stdin=subprocess.PIPE)
            
            if p.returncode and p.returncode > 0:
                self.man_logger.warning("Create peer - Not created successfully, returncode%s: id=%s, ip_addr=%s" % (p.returncode, str(id), ip_addr))
                return
            
            self.process_id_map[id] = {}
            self.process_id_map[id]['process'] = p
            self.process_id_map[id]['killed'] = False
            self.process_id_map[id]['logfile'] = logfile
            self.process_id_map[id]['logerrfile'] = logerrfile

            self.man_logger.info("Created peer: pid=%d, id=%s, ip_addr=%s, %s" % (self.process_id_map[id]['process'].pid, str(id), ip_addr, logmsg))
        except Exception as e:
            self.man_logger.warning("Create peer - ERROR: id=%s, ip_addr=%s, err=%s" % (str(id), ip_addr, e))
            return
        
    def _tor_create_peer(self, id, *args):
        """
        To be overridden.
        Extends the create_peers method.
        Extra arguments for the create_peer. _run_node method will be alse call with these. 
        params:
            id - id/ip
            agrs - 
        """
        return
    
    def send_command_to_peers(self, peer_ids, command):
        """
        To be called from Director.
        Sends command to peers.
        params:
            peer_ids - list of ids/ips
            command - string
        """
        for peer in peer_ids:
            self.process_id_map[peer]['process'].stdin.write(command)
        self.man_logger.info("Command sent to peers: ids=%s, command=%s" % (`peer_ids`, command))    
        
        
    def send_signal_to_peers(self, peer_ids, signal):
        """
        To be called from Director.
        Sends signal to peers.
        params:
            peer_ids - list of ips/ids
            signal - constants from subprocess.signal
        """
        for peer in peer_ids:
            self.process_id_map[peer]['process'].send_signal(signal)
        
        self.man_logger.info("Signal sent to peers: ids=%s, signal=%s" % (`peer_ids`, `signal`))
        
    
    def create_peers(self, ids, *args):
        """
        To be called from Director.
        Creates peers.
        params:
            ids - list of ids/ips
        """        
        if not ids:
            self.man_logger.warning("Peers not created due to wrong id range specification: no valid id")
            return
        
        for id in ids:
            self._run_node(id, *args)
            self._tor_create_peer(id, *args)
            self.swap_control()
            
    def _tor_reset(self):
        """
        To be overridden.
        Extends the reset method.
        """
        return
            
    def reset(self):
        """
        To be called from Director.
        Resets the director.
        """       
        self.man_logger.info("Reset operation started")
        self.shaper.reset_all()
        self._tear_perees()
        self.process_id_map = {}
        self._tor_reset()
        self.man_logger.info("Reset operation finished")
        

    
    def kill_hard(self, ids):
        """
        To be called from Director.
        Emulates forced departure of peers. Simulation of 'Turn off' button.
        params:
            ids - list of ids/ips
        """

        for id in ids:
            self._kill_peer_hard(id)
            
          
    def kill_hard_random(self, number):
        """
        To be called from Director.
        Emulates forced departure of number of peers.
        Simulation of 'Turn off' button of computer.
        params:
            number - int
        returns:
            list of ids/ips of killed peers
        """
        return self._kill_random(number, 'hard', self._kill_peer_hard)
    
    def kill_soft_random(self, number):
        """
        To be called from Director.
        Emulates correct departure of number of peers. Preserves assigned IP address.
        Simulation of 'Exit' button of application.
        params:
            number - int
        returns:
            list of ids/ips of killed peers
        """
        
        return self._kill_random(number, 'soft', self._kill_peer_soft)  
     
    def get_runnnig_peers(self):
        peers = list()
        keys = self.process_id_map.keys()
        for key in keys:
            if self.process_id_map[key]["killed"] == False:
                peers.append(key)
        return peers
            
    def _kill_random(self, number, name, kill_callable):
        self.man_logger.info("Kill %s random: number_of_peers_to_kill: %i" % (name, number))
        keys = self.get_runnnig_peers()
        if number > len(keys):
            self.man_logger.warning("Kill %s random - cancelling operation, too many peers to kill" % name)
            return
    
        killed_peers = list()
        
        for i in range(number):
            ind = randint(0, len(keys) - 1)
            key = keys[ind]
            kill_callable(key)
            killed_peers.append(key)
            keys.pop(ind)
        
        return killed_peers
    
    def kill_soft(self, ids):
        """
        To be called from Director.
        Emulates correct departure of peers. Preserves assigned IP address.
        Simulation of 'Exit' button of application.
        params:
            ids - list of ids/ips
        """
        for id in ids:
            self._kill_peer_soft(id)
            
    
    def _sleep_for(self, seconds):
        self.man_logger.info("Will sleep: seconds=" + str(seconds))
        sleep(seconds)

    
    def shape(self, ids, delay, upload, download):
        """
        To be called from Director.
        Shapes peers.
        params:
            ids - list of ips/ids
            delay - int, peer delay in ms
            upload - int, peer upload limit in Kb/s
            download - int, peer download limit in Kb/s

        """
        for id in ids:
            if self.shaper.is_shaped(id):
                self.man_logger.warning("Peer already shaped: id=%s" % `id`)

        if not ids:
            self.man_logger.warning("Shaping not performed due to wrong id range specification: no valid id")
            return       
 
        self.shaper.shape(delay, upload, download, ids)
        
    
    def get_ip_addr(self, id):
        """
        To be called from Director.
        Converts id/ip to ip.
        params:
            id - id/ip
        returns:
            ip
        """
        return self.shaper.get_ip_address(id)
    
    def swap_control(self):
        """
        To be called from Director.
        Checks swap usage.
        returns:
            swap - string
        """
        try:
            rc, out, err = executor.execute("free -m | tail -1 | tr -s ' ' | cut -d ' ' -f 3")
            swap = int(out)
            if swap < self.swap_limit:
                self.man_logger.info("Swap usage: %d MB" % swap)
            else:
                self.man_logger.warning("Swap usage over limit: %d MB" % swap)
            return swap
        except Exception as e:
            self.man_logger.warning("Cannot establish swap usage: err=%s" % str(e))
            
            
    def set_stats(self, all=list(), up=list(), down=list()):
        """
        To be called from Director.
        See ShapeWithStats and TrafficStats.
        """
        print "set stats"
        self.man_logger.info("Adding peers to shaped stats monitoring, all=%s, up=%s, down=%s" % (`all`, `up`, `down`))
        return self.shaper.set_stats(all, up, down)
    
            
    def start_stats(self, timeout):
        """
        To be called from Director.
        See ShapeWithStats and TrafficStats.
        """
        
        self.man_logger.info("Starting shaped stats.")
        return self.shaper.start_stats(timeout)
        
    def stop_stats_and_report(self):
        """
        To be called from Director.
        See ShapeWithStats and TrafficStats.
        """
        
        self.man_logger.info("Stopping shaped stats and generating the report")
        return self.shaper.stop_stats_and_report()
        
    def generate_stats_report(self):
        """
        To be called from Director.
        See ShapeWithStats and TrafficStats.
        """
        
        self.man_logger.info("Generating shaped stats report.")
        return self.shaper.generate_report()
        
    def stop_stats(self):
        """
        To be called from Director.
        See ShapeWithStats and TrafficStats.
        """
        
        self.man_logger.info("Stopping shaped stats")
        return self.shaper.stop_stats()
        
    def stats_set_report_format(self, format_name):
        """
        To be called from Director.
        See ShapeWithStats and TrafficStats.
        """
        self.man_logger.info("Setting shaped stats report format, format_name=%s" % format_name)
        return self.shaper.set_report_format(format_name)
