import xmlrpclib
from time import sleep
from P2PEM.loggs import GeneralLogger
from P2PEM import loggs
from identification_modes import ByIPAddress, ByID
from SimpleXMLRPCServer import SimpleXMLRPCServer
import thread
from random import randint



def run_log_server(server):
    try:
        server.serve_forever()
    except:
        pass

class Director(object):
    
    MODE_MAP = {'ip': ByIPAddress,
            'id': ByID,
            }
    DEFAULT_SWAP_LIMIT = 100
    DEFAULT_MODE = 'id'
    DEFAULT_LOG = {'mode':{'file':'debug', 'console':'info'}, 'file_name':'director.log'}
    DEFAULT_MAN_TO_DIR = {'address': None, 'port': None}
    DEFAULT_SL_DELAY = (0,200)
    DEFAULT_SL_UPLOAD = (100, 5000)
    DEFAULT_SL_DOWNLOAD = (300, 10000)

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
        return GeneralLogger(log, "DirectorLogger")
    
    
    def __init__(self, machines_def, log= {}, man_to_dir_log = {}, mode=None,
                   swap_limit=None, *args):
        """
        params:
            machines_def
            log - director log settings
            man_to_dir_log - url to launch manager-to-director log server
            mode - key from MODE_MAP
            swap_limit - int, when reached, logs as warning
            
        MACHINES_DEF = {
            m1: ("localhost", 8888, shaper, log, None, args),  // manager IP, manager port, shaper settings (dict), log settings (dict), root password
            m2: ("10.5.0.2", 8888, shaper, log, None, args)
            }
        MAN_TO_DIR_LOG =
            address: '10.0.0.1',
            port: '8999',
            }
            
        """
        
        loggs.used_logger = self._tor_get_logger(log or self.DEFAULT_LOG) 
        self.dir_logger = loggs.used_logger
    
        self.man_to_dir_log = man_to_dir_log or self.DEFAULT_MAN_TO_DIR
        self.man_to_dir_server = None
    
        self.MACHINES_DEF = machines_def
        self.MODE = mode or self.DEFAULT_MODE    
        
        self.swap_limit = swap_limit or self.DEFAULT_SWAP_LIMIT
        self.managers = {}  
        self.peers = {}
        import copy
        logMD = copy.deepcopy(self.MACHINES_DEF)
        
        for k, m in logMD.iteritems():
            if m[4]:
                n = m
                m = list()
                m.extend(n)
                m[4] = "*"*6
                logMD[k] = m
                
        self.dir_logger.info("Init: Machines_def=%s" % str(logMD))        
        self.dir_logger.info("Init: Swap_limit=%s" % str(self.swap_limit))
        
        self.sl_delay = self.DEFAULT_SL_DELAY
        self.sl_download = self.DEFAULT_SL_DOWNLOAD
        self.sl_upload = self.DEFAULT_SL_UPLOAD
        
        self._tor__init__(*args)

    def _get_ids_by_managers(self, ids, err_log=""):
        """
        Divides peers among managers according to where they are running.
        params:
            ids - list of ids/ips
            err_log - log message to be used when peer does not exist
                      must include %s, >> err_log % str(id)
                      when empty, will not be used
        returns:
            dictionary - manager ids as keys, lists of peer's ids as values
        """
        
        
        m_ids = {}
        for machine_name in self.managers.keys():
            m_ids[machine_name] = list()

        for id in ids:
            if self.peers.has_key(id):
                m_ids[self.peers[id]["manager"]].append(id)
            elif err_log:
                self.dir_logger.warning(err_log % str(id))
                
        return m_ids
    
    def call_on_managers_with_ids(self, callable, ids, log_msg, err_log, *args):
        """
        Can be optionally used from scenario.
        Calls certain method on all managers using only appropriate peers from list.
        params:
            callable - function to be called - must accept manager, ids and args
            ids - list of ids/ips, peers to be divided among machines
            log_msg - log message to be used when calling method on a manager
                      must include "%s %s" >> log_msg % (machine, str(id_list))
                      when empty, will not be used
            err_log - log message to be used when peer does not exist
                      must include "%s", >> err_log % str(id)
                      when empty, will not be used
            args - args to be passed to method_name
        returs:
            boolean - success (return) of all called methods
        """
        success = True
        m_ids = self._get_ids_by_managers(ids, err_log)
        
        for machine, id_list in m_ids.iteritems():
            print args
            success = success and callable(self.managers[machine], id_list, *args)
            
            if log_msg:
                msg = log_msg % (machine, str(id_list))
                self.dir_logger.info(msg)
        return success

    
    def _tor_start(self):
        """
        To be overridden.
        Extend start method.
        returns:
            boolean - True if success
        """
        return True   
     
    def start(self):
        
        if self.MODE not in self.MODE_MAP:
            self.dir_logger.critical("Start: Wrong mode definition: mode does not exits")
            return False
        
        self.id = self.MODE_MAP[self.MODE]()
        self.dir_logger.info("Start: mode=%s" % (self.MODE))
        
        
        dirs = [ md[3]['mode'] for md in self.MACHINES_DEF.itervalues() if ('mode' in md[3] and 'director' in md[3]['mode']) ]
        
        
        if dirs and not self.man_to_dir_log['address'] or not self.man_to_dir_log['port']:            
            self.dir_logger.critical("Start: MAN_TO_DIR_LOG_ADDR or MAN_TO_DIR_LOG_PORT not defined in scenario.")
            return False
        
        if dirs:
            self.man_to_dir_server = SimpleXMLRPCServer((self.man_to_dir_log['address'], self.man_to_dir_log['port']), allow_none=True)
            self.man_to_dir_server.register_instance(self.dir_logger, False)
            thread.start_new_thread(run_log_server, (self.man_to_dir_server,))

        
        for (name, params) in self.MACHINES_DEF.iteritems():
            
            success = self._run_manager(name, 'http://%s:%i' % (params[0], params[1]), params[2], params[3], params[4], *params[5:])
            if not success:
                return False

        return self._tor_start()
        

    
    def _tor_tear_down(self):
        """
        To be overridden.
        Extends tear_down method.
        """
        
        return
    
    
    def tear_down(self):
        self.dir_logger.info("Tear-down: Started")
        
        for (name, manager) in self.managers.iteritems():
            try:
                manager.stop()
                self.dir_logger.info("Tear-down: Manager %s stopped" % name)
            except IOError as e:
                self.dir_logger.warning("Tear-down: Manager %s: ERROR: %s" % (name, e))
        
        self._tor_tear_down()
        
        if self.man_to_dir_server:
            self.man_to_dir_server.server_close()

        self.dir_logger.info("Tear-down: Finished")
    
    
    def set_ids(self, idranges):
        ids = {}

        for machine_name in self.managers.keys():
            ids[machine_name] = set()

        for (name, id_range) in idranges:
            id = self.id.id_from_range(id_range)
            if id:
                ids[name] |= set(id)


        for (machine_name, ids) in ids.iteritems():
            for id in ids:
                self.peers[id] = {"manager": machine_name, "runs": False}
            self.managers[machine_name].start(tuple(ids))
            self.dir_logger.info("Set-ids: Sent set to manager %s: ids=%s" %
                                  (str(machine_name),str(tuple(ids))) )
    
    def _tor_pre_create_peers(self, manager, ids, *args):
        """
        To be overridden. Hook method.
        Extends create_peers method. Precedes the create operation.
        params:
            manager - manager id
            ids - list of ids/ips
            args - extra arguments for the create_peer method
        returns:
            manager, ids, args (can be modified)
        """
        return manager, ids, args

    def _tor_post_create_peers(self, manager, ids, *args):
        """
        To be overridden.
        Extends create_peers method. Follows the create operation.
        params:
            manager - manager id
            ids - list of ids/ips
            args - extra arguments for the create_peer method
        """
        return
    
    def send_signal_to_peers(self, id_range, signal):
        """
        To be used from scenario functions.
        Sends signal to peers.
        params:
            id range - id_range/ip_range
            signal - subprocess.signal
        """
        ids = self.id.id_from_range(id_range)
        
        self.call_on_managers_with_ids(self._signal, ids,
                                       "Send-signal: signal sent to manager=%s, ids=%s" + (", signal=%s" % signal),
                                       "Send-signal: cannot send signal, peer does not exits: id=%s",
                                       signal)
    def _signal(self, manager, ids, signal):
        manager.send_signal_to_peers(ids, signal)
    
    def _command(self, manager, ids, command):
        manager.send_command_to_peers(ids, command)
        
    def send_command_to_peers(self, id_range, command):
        """
        To be used from scenario functions.
        Sends command to peers.
        params:
            id_range - id_range/ip_range
            command - string
        """
        ids = self.id.id_from_range(id_range)
        
        self.call_on_managers_with_ids(self._command, ids,
                                       "Send-command: command sent to manager=%s, ids=%s" + (", command=%s" % command),
                                       "Send-command: cannot send command, peer does not exits: id=%s",
                                       command)

    def create_peers(self, manager, id_range, *args):
        """
        To be used from scenario functions.
        Creates peers.
        params:
            manager - manager id
            id_range - ip_range/id_range
        """
        
        self.dir_logger.info("Create-peers: Started")
        ids = self.id.id_from_range(id_range)
               
        manager, ids, args_pre = self._tor_pre_create_peers(manager, ids, *args)
                
        if ids:
            
            self.managers[manager].create_peers(ids, *args_pre)
        
            self.dir_logger.info("Create-peers: Sent create to manager %s: ids=%s, args=%s" %
                                  (str(manager), str(ids), str(args_pre)) )
                    
        self._tor_post_create_peers(manager, ids, *args)
        
        for id in ids:
            self.peers[id]["runs"] = True
        self.dir_logger.info("Create-peers: Finished")
    def _tor_reset_all(self):
        """
        To be overridden.
        Extends reset_all method.
        """
        return

    def reset_all(self):
        """
        To be called from scenario functions.
        Resets Director and all Managers.
        """
        self.dir_logger.info("Reset-all: Started")
        for (name, manager) in self.managers.iteritems():
            manager =  self._tor_reset_manager(manager)
            manager.reset()
            self.dir_logger.info("Reset-all: Sent reset to manager %s" % name)
        for id in self.peers.keys():
            self.peers[id]["runs"] = False
            
        self._tor_reset_all()
        self.sleep_for(10)
        self.dir_logger.info("Reset-all: Finished")
    
    def _tor_reset_manager(self, manager):
        """
        To be overridden. Hook method.
        Extends reset_manager and reset_all methods.
        params:
            manager - manager id
        returns:
            manager id (can be modified)
        """ 
        return manager
    
    def reset_manager(self, manager):
        """
        To be called from scenario functions.
        Resets Manager.
        params:
            manager - manager id
        """
        self.dir_logger.info("Reset-manager: Started")
        manager = self._tor_reset_manager(manager)
        if not manager:
            return
        self.managers[manager].reset()
        self.dir_logger.info("Reset-manager: Sent reset to manager %s" % manager)
        for (id, peer) in self.peers.iteritems():
            if peer['manager'] == manager:
                self.peers[id]["runs"] = False
        
        self.sleep_for(10)
        self.dir_logger.info("Reset-manager: Finished")
                
        
    def sleep_for(self, seconds):
        """
        To be called from scenario functions.
        Stops executing the scenario for amount of seconds.
        params:
            seconds - int
        """
        self.dir_logger.info("Sleep: Will sleep for %i seconds" % seconds)
        sleep(seconds)
    
    def _tor_kill_hard(self, ids):
        """
        To be overridden. Hook function.
        Extends kill_hard method.
        params:
            ids - list of ids/ips
        returns:
            ids - list of ids/ips (can be modified)
        """
        return ids
    
    def _tor_kill_soft(self, ids):
        """
        To be overridden. Hook function.
        Extends kill_soft method.
        params:
            ids - list of ids/ips
        returns:
            ids - list of ids/ips (can be modified)
        """
        return ids
    
    def _kill(self, id_range, name, tor_method, method):
        self.dir_logger.info("Kill-%s: Started: id_range=%s" % (name, str(id_range)))
        ids = self.id.id_from_range(id_range)
        ids = tor_method(ids)
        m_ids = {}
        
        for machine_name in self.managers.keys():
            m_ids[machine_name] = list()

             
        for id in ids:
            if self.peers.has_key(id):
                m_ids[self.peers[id]["manager"]].append(id)
                self.peers[id]["runs"] = False
            else:
                self.dir_logger("Kill-%s: Cannot kill, peer does not exist: id=%s" % (name, str(id)))
        
        for (manager, ids) in m_ids.iteritems():
            if ids:
                
                method(manager, ids)
                
                self.dir_logger.info("Kill-%s: Sent kill-hard to manager %s: ids=%s" %
                                     (name, manager, str(ids)))
        
        self.dir_logger.info("Kill-%s: Finished" % name)
        
    def kill_hard(self, id_range):
        """
        To be called from scenario functions.
        Kills peers. Emulates forced departure of peers.
        params:
            id_range - id_range/ip_range
        """
        self._kill(id_range, "hard", self._tor_kill_hard, self._kill_hard)
        
    def kill_soft(self, id_range):
        """
        To be called from scenario functions.
        Kills peers. Emulates correct departure of peers.
        Preserves assigned IP address.
        params:
            id_range - id_range/ip_range
        """
        self._kill(id_range, "soft", self._tor_kill_soft, self._kill_soft)
        
    
    def _kill_hard(self, manager, ids):
        self.managers[manager].kill_hard(ids)
    
    def _kill_soft(self, manager, ids):
        self.managers[manager].kill_soft(ids)
    
                
    def _tor_kill_hard_random(self, manager, number):
        """
        To be overridden. Hook method.
        Extends kill_hard_random method.
        params:
            manager - manager id
            number - int, number of peers to kill on manager
        returns:
            manager, number (can be modified)
        """
        return manager, number
                
    def kill_hard_random(self, manager, number):
        """
        To be called from scenario functions.
        Kills number of peers on manager. Peers are choces randomly.
        Emulates forced departure of peers.
        params:
            manager - manager id
            number - int, number of peers to kill on manager
        """
        manager, number = self._tor_kill_hard_random(manager, number)
        
        killed_peers = self.managers[manager].kill_hard_random(number)
        for peer in killed_peers:
            self.peers[peer]["runs"] = False
        self.dir_logger.info("Kill-hard-random: Sent kill-hard-random to manager %s: number_to_kill=%i" %
                             (manager, number))
        
    def _tor_kill_soft_random(self, manager, number):
        """
        To be overridden. Hook method.
        Extends kill_soft_random method.
        params:
            manager - manager id
            number - int, number of peers to kill on manager
        returns:
            manager, number (can be modified)
        """
        return manager, number
    
    
    def kill_soft_random(self, manager, number):
        """
        To be called from scenario functions.
        Kills number of peers on manager. Peers are choces randomly.
        Emulates correct departure of peers. Preserves assigned IP address.
        params:
            manager - manager id
            number - int, number of peers to kill on manager
        """
        manager, number = self._tor_kill_soft_random(manager, number)
        
        killed_peers = self.managers[manager].kill_soft_random(number)
        for peer in killed_peers:
            self.peers[peer]["runs"] = False
        self.dir_logger.info("Kill-soft-random: Sent kill-soft-random to manager %s: number_to_kill=%i" %
                             (manager, number))
    
        
    def swap_control(self, manager):
        """
        To be called from scenario functions.
        Checks swap usage on manager.
        params:
            manager - manager id
        """
        swap = self.managers[manager].swap_control()
        if swap < self.swap_limit:
            self.dir_logger.info("Swap-control: Manager %s - swap usage : %d MB" % (manager, swap))
        else:
            self.dir_logger.warning("Swap-control: Manager %s - swap usage over limit: %d MB" % (manager, swap))
        
    def swap_control_all(self):
        """
        To be called from scenario functions.
        Checks swap usage on all managers.
        """
        self.dir_logger.info("Swap-control-all: Started")
        for (name,manager) in self.managers.iteritems():      
            swap = manager.swap_control()
            if swap < self.swap_limit:
                self.dir_logger.info("Swap-control-all: Manager %s - swap usage : %d MB" % (name, swap))
            else:
                self.dir_logger.warning("Swap-control-all: Manager %s - swap usage over limit: %d MB" % (name, swap))
        self.dir_logger.info("Swap-control-all: Finished")
            
    def _tor_shape(self, delay, upload, download, ids):
        """
        To be overridden. Hook method.
        Extends shape method.
        params:
            delay, upload, download - int
            ids - list of ids/ips
        returns:
            delay, upload, download, ids (can be modified)
        """
        return delay, upload, download, ids
            
    def shape(self, delay, upload, download, id_range):
        """
        To be called from scenario functions.
        Shapes peers running on managers.
        params:
            delay, upload, download - int
            ids - id_range/ip_range
        """
        self.dir_logger.info("Shape: Started: id_range=%s" % id_range)

        ids = self.id.id_from_range(id_range)

        delay, upload, download, ids = self._tor_shape(delay, upload, download, ids)
   
        self.call_on_managers_with_ids(self._shape, ids, "Shape: Sent shape to manager %s:" + 
                                       ("delay=%i, upload=%i, download=%i, " % ( delay, upload, download)) +
                                        "ids=%s",
                                      "Shape: Cannot shape, peer does not exist: id=%s",
                                      delay, upload, download)
                
        self.dir_logger.info("Shape: Finished")
        
    def _shape(self, manager, ids, delay, upload, download):
        return manager.shape(ids, delay, upload, download)
        
    def _tor_shape_non_peer(self, manager, delay, upload, download, ip_range):
        """
        To be overridden. Hook method.
        Extends shape_non_peer method.
        params:
            delay, upload, download - int
            ids - list of ids/ips
        returns:
            delay, upload, download, ids (can be modified)
        """
        return manager, delay, upload, download, ip_range 
        
    def shape_non_peer(self, manager, delay, upload, download, ip_range):
        """
        To be called from scenario functions.
        Shapes peers not managed by managers.
        params:
            delay, upload, download - int
            ip_range - ip_range
        """

        ips = ByIPAddress().id_from_range(ip_range)
        
        manager, delay, upload, download, ip_range = self._tor_shape_non_peer(manager, delay, upload, download, ip_range)
        
        self.managers[manager].shape(ips, delay, upload, download)
        self.dir_logger.info("Shape-non-peer: Sent shape to manager %s: delay=%i, upload=%i, download=%i, ids=%s" %
                                     (manager, delay, upload, download, str(ips)))
    
    def _check_shape_limits(self, limit):
        if len(limit) != 2:
            self.dir_logger.warning("Shape-limits-for-random: Wrong shape limit length, limit=%s" % str(limit))
            return False
        if limit[0] < 0:
            self.dir_logger.warning("Shape-limits-for-random: Bottom limit must be larger than 0, limit=%s" % str(limit))
            return False
        
        if limit[1] < limit[0]:
            self.dir_logger.warning("Shape-limits-for-random: Top limit must be larger than bottom limit, limit%s" % str(limit))
            return False
        return True
    
    def define_random_shape(self, delay, upload, download):
        if self._check_shape_limits(delay):
            self.sl_delay = delay
        else:
            self.dir_logger.warning("Define-random-shape: Delay limit not set")
        if self._check_shape_limits(upload):
            self.sl_upload = upload
        else:
            self.dir_logger.warning("Define-random-shape: Upload limit not set")
        if self._check_shape_limits(download):
            self.sl_download = download
        else:
            self.dir_logger.warning("Define-random-shape: Download limit not set")
        self.dir_logger.info("Define-random-shape: Shape limits were se to: delay=%s, upload=%s, download=%s" % (`self.sl_delay`, `self.sl_upload`, `self.sl_download`))
        
    
    def shape_random(self, id_range):
        ids = self.id.id_from_range(id_range)
        m_ids = self._get_ids_by_managers(ids, "Shape-random: shaping not set - peer does not exist: id=%s")
        for machine, id_list in m_ids.iteritems():
            for id in id_list:
                delay = randint(self.sl_delay[0], self.sl_delay[1])
                upload = randint(self.sl_upload[0], self.sl_upload[1])
                download = randint(self.sl_download[0], self.sl_download[1])
                self.managers[machine].shape((id, ), delay, upload, download)
            self.dir_logger.info("Shape-random: sent random shape to manager=%s, ids=%s" % (machine, str(id_list)))
            
    def shape_random_non_peer(self, manager, ip_range):
        ips = ByIPAddress().id_from_range(ip_range)
        for ip in ips:
            delay = randint(self.sl_delay[0], self.sl_delay[1])
            upload = randint(self.sl_upload[0], self.sl_upload[1])
            download = randint(self.sl_download[0], self.sl_download[1])
            self.managers[manager].shape((ip, ), delay, upload, download)
        self.dir_logger.info("Shape-random: sent random shape to manager=%s, ids=%s" % (manager, str(ips)))
    
    
    def _tor_run_manager(self, machine_name, url, shaper, log, sudo_mode, *args):
        """
        To be overridden. Hook method.
        Extends _run_manager method.
        params:
            machine_name - manager id
            url - manager's XMLRPC server url
            shaper - shaper settings
            log - log settings
            sudo_mode - root password or None
            args - additional params from MACHINES_DEF
        returns:
            machine_name, url, shaper, log, sudo_mode (can be modified)
            args (can be modified and extended)
        
        """
        return machine_name, url, shaper, log, sudo_mode, args
    
    def _run_manager(self, machine_name, url, shaper, log, sudo_mode, *args):

        log['dir_url'] = "http://%s:%d" % (self.man_to_dir_log['address'], self.man_to_dir_log['port'])

        log['dir_name'] = machine_name
        
        machine_name, url, shaper, log, sudo_mode, args = self._tor_run_manager(machine_name, url, shaper, log, sudo_mode, *args)
        print args
        try:
            proxy = xmlrpclib.ServerProxy(url, allow_none=True)
            proxy.set_manager(shaper, self.swap_limit, log, sudo_mode, *args)
            
            
            self.managers[machine_name] = proxy
            self.dir_logger.info("Connection with manager %s established: url=%s, args=%s" %
                                 (str(machine_name), str(url), str(args),
                                   ))
            return True
        except Exception as e:
            self.dir_logger.critical("Connection with manager not established: name=%s, url=%s, args=%s, ERROR: %s"
                                     % (str(machine_name), str(url), str(args), str(e)))
 
            return False
    
    def set_stats(self, all='', up='', down=''):
        """
        To be called from scenario functions.
        Registers peers managed by managers to be monitored.
        params:
            all - id_range/ip_range, to monitore upload and download
            up - id_range/ip_range, to monitore upload
            down - id_range/ip_range, to monitore download
        """
        allids = self.id.id_from_range(all)
        
        if not allids:
            allids = list()
        upids = self.id.id_from_range(up)
        if not upids:
        
            upids = list()
        
        downids = self.id.id_from_range(down)
        if not downids:
            downids = list()
#        jen peery ke spravnym managerum?
        self._set_stats(allids, upids, downids)
    
    def _set_stats(self, all, up, down):
        
        success = True
        for manager in self.managers.values():
            success = success and manager.set_stats(all, up, down)
        if success:    
            self.dir_logger.info("Shaped stats: sent set stats to managers: all=%s, upload=%s, download=%s" % (`all`, `up`, `down`))
        else:
            
            self.dir_logger.warning("Shaped stats: Could not set stats.")
    
    def set_no_peer_stats(self, all='', up='', down=''):
        """
        To be called from scenario functions.
        Registers peers not managed by managers to be monitored.
        params:
            all - id_range/ip_range, to monitore upload and download
            up - id_range/ip_range, to monitore upload
            down - id_range/ip_range, to monitore download
        """
        id = ByIPAddress()
        allids = id.id_from_range(all)
        if not allids:
            allids = list()
            
        upids = id.id_from_range(up)
        if not upids:
            upids = list()
        
        downids = id.id_from_range(down)
        if not downids:
            downids = list()
        self._set_stats(allids, upids, downids)
            

    def start_shaped_stats(self, timeout):
        """
        To be called from scenario functions.
        Starts collecting of statistics. The data will be gathered every number (timeout) of seconds.
        params:
            timeout - float in seconds
        """
        success = True
        for manager in self.managers.values():
            success = success and manager.start_stats(timeout)
        if success:    
            self.dir_logger.info("Shaped stats: send start stats to managers")
        else:
            self.dir_logger.warning("Shaped stats: Could not start stats.")
            
    def stop_shaped_stats(self):
        """
        To be called from scenario functions.
        Stops statistics on all managers.
        """
        success = True
        for manager in self.managers.values():
            success = success and manager.stop_stats()
        if success:
            self.dir_logger.info("Shaped stats: report generated from shaped stats to file=%s" % str(file))
        else:
            self.dir_logger.warning("Shaped stats: Could not stop stats.")
    
    def _stats_report(self, file, method):
        report = ""
        for manager in self.managers.values():
            rep = method(manager)

            if rep != None:
                report = report + rep
            else:
                self.dir_logger.warning("Shaped stats: Could not generate report")
                return False
        try:
            with open(file, 'w') as efile:
                efile.write(report)
        except Exception as e:
            self.dir_logger.warning("Shaped stats: Could not generate report: could not write to file, ERR=%s" % str(e))
            
        self.dir_logger.info("Shaped stats: report generated from shaped stats to file=%s" % str(file))
        return True
    
    def _stop_rep(self, manager):
        return manager.stop_stats_and_report()
        
    def _rep(self, manager):
        return manager.generate_stats_report()
        
    
        
    def generate_stats_report(self, file):
        """
        To be called from scenario functions.
        Generates report using set format (defaul simple) from all managers.
        """
        self._stats_report(file, self._rep)
    
    def shaped_stats_set_report_format(self, format_name):
        """
        To be called from scenario functions.
        Sets the report format.
        params:
            name - name of the format (key from TrafficStats.REPORT_FORMATS)
        """
        success = True
        for manager in self.managers.values():
            success = success and manager.stats_set_report_format(format_name)

        if success:

            self.dir_logger.info("Shaped stats: Report format set, format_name=%s" % format_name)
        else:
            self.dir_logger.warning("Shaped stats: Could not set report format.")
    
    def stop_shaped_stats_and_report(self, file):
        """
        To be called from scenario functions.
        Stops stats and generates report using set format (defaul simple) from all managers.
        params:
            file - file to save report
        """
        if self._stats_report(file, self._stop_rep):
            self.dir_logger.info("Shaped stats: Stats stopped.")
        
           
def get_director_params(scenario):
    """
    To be overridden.
    Gather params from scenario to be used as initial argumets for extended Director.
    params:
        scenario - loaded module
    returns:
        list of params
    """
    return list() 

def tor_pre_scenario(sc, director):
    """
    To be overridden.
    Can initiate operations on director using scenario before the scenario execution.
    params:
        director - extended Director instance
        sc - loaded module - scenario
    
    """
    return
