import threading

from P2PEM import loggs

def run(stat, timeout):

    while True:
        if stat.event.is_set():
            break
        stat._stats()
        stat.event.wait(timeout)
    stat.stopped = True

def generate_simple(stats):
    """
    Output format function. Generates values separated by commas.
    params:
        stats - TrafficStats object
    returns:
        string
    """
    
    from cStringIO import StringIO
    file_str = StringIO()
    for key, value in stats.iteritems():
        for ip, values in value.iteritems():
            file_str.write("%s,%s," % (`key`, ip))
            file_str.write(','.join([ `value` for value in values['stats'] ]))
            file_str.write('\n')
        

    return file_str.getvalue()


class TrafficStats(object):
    """
    To be overriden by child classes.
    """
    
    REPORT_FORMATS = {
                       'simple': generate_simple
                       }
    """
    Enables output formats.
    """
    
    def init_stats(self):
        
        self.logger = loggs.used_logger
        self.stats = {}
        self.stopped = False
        self.format = self.REPORT_FORMATS['simple'] # default
        self.thread = None
        self.event = threading.Event()
        
        
    def set_report_format(self, name):
        """
        Sets the report format.
        params:
            name - name of the format (key from REPORT_FORMATS)
        returns:
            boolean - False if name does not exist
        """

        if name in self.REPORT_FORMATS:

            self.format = self.REPORT_FORMATS[name]

            return True
        else:
            self.logger.warning("Traffic_stats: Report format not found.")
            return False

    def generate_report(self):
        """
        Generates report using set format (defaul simple).
        returns:
            report: string or None if not stopped
        """
        
        if self.stopped:
            return self.format(self.stats)
        else:
            pass
            self.logger.warning("Traffic_stats: Cannot generate report. Stats not stopped.")
            return None

    def is_stopped(self):
        """
        returns:
            boolean - True if stopped, False if running or initialized
        """
        return (self.thread and self.stopped)

    def is_not_running(self):
        """
        returns:
            boolean - True if not running (stopped or initialized)
        """
        
        return (self.thread and self.stopped) or not self.thread

    def set_stats(self, *args):
        """
        To be overriden by child classes.
        Registers peers to be monitored.
        """
        pass

    def start_stats(self, timeout):
        """
        Starts collecting of statistics. The data will be gathered every number (timeout) of seconds.
        params:
            timeout - float in seconds
        returns:
            boolean - False if already running
        """
        
        if self.is_stopped():
            self.reset_stats()
            
        if not self.thread:

            self.thread = threading.Thread(target=run, args=(self, timeout))
            self.thread.start()
            return True
        else:
            self.logger.warning("Traffic_stats: Cannot start stats. Stats already running.") 
            return False
        
    def reset_stats(self):
        """
        Resets collecting of statistics.
        """
        
        self.event = threading.Event()
        self.stopped = False
        self.thread = None
        self.logger.info("Traffic_stats: Stats resetted")



    def stop_stats_and_report(self):
        """
        Stops stats and generates report using set format (defaul simple).
        returns:
            report: string or None if not stopped
        """
        
        if self.stop_stats():
            return self.generate_report()
        else:
            return False
          
    def add_report_format(self, name, callable_gen_report):
        """
        Adds report format.
        params:
            name - string, name to register the format
            callable_gen_report - callable, see genarate_simple as example
        """
        
        if name not in self.REPORT_FORMATS:
            self.REPORT_FORMATS[name] = callable_gen_report 
            self.logger.info("Traffic_stats: Report format added, format_name=%s" % name)
        else:
            self.logger.warning("Traffic_stats: Cannot add report format. Report format name already used.")
             
    def _stats(self):
        """
        To be overriden in child classes.
        Executes the collecting of statistics.
        """
        
        pass
  
    def stop_stats(self):
        """
        Stops statistics.
        returns:
            boolean - False if not running
        """
        
        if self.thread and not self.stopped:
            self.event.set()
            self.thread.join()
            return True
        else:
            self.logger.warning("Traffic_stats: Cannot stop stats. Stats already stopped.")
            return False
