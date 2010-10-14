"""
running

Running threads and shell commands, for procblock.
"""


import subprocess
import threading
import time
import os
import copy
import pprint
import logging


import code_python

import unidist
from unidist import error_info
from unidist.log import log
from unidist import sharedlock
from unidist import sharedstate
from unidist import sharedcounter
from unidist import timeseries



# Default number of maximum history to keep for this interval cache
RUN_CACHE_DEFAULT_HISTORY_MAXIMUM = 100

# Default interval for run cache, in seconds, if not specified
RUN_CACHE_DEFAULT_INTERVAL = 5

# Seconds to cache command
COMMAND_CACHE_TIMEOUT_DEFAULT = 60


def Run(command, cache=False, cache_timeout=COMMAND_CACHE_TIMEOUT_DEFAULT):
  """Actually run the command on the local machine.  Blocks until complete.
  
  Args:
    command: string, command to execute
    cache: boolean (default False), cache this command [TBD: Add cache timeout...]
  
  TODO(g): Store commands and cache for internals viewing?
  """
  #global ENVIRONMENT
  
  output_error = '' #Later, how to handle reading the timing stream between the two?  It's lost...

  #log('Run: %s' % command)

  #TODO(g): Remove when subprocess method works
  #(status, output, output_error) = os.popen3(command)

  # Subprocess is beautiful and finally makes this a pleasant experience!
  #   Imagine, OUTPUT, ERRORS and EXIT CODE!!!  Not exclusively choosing two!
  #   Newbs be rejoice in your ignorance.
  pipe = subprocess.Popen(command, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, shell=True)
  status = pipe.wait()
  output = pipe.stdout.read()
  output_error = pipe.stderr.read()
  
  # Close the pipes
  pipe.stderr.close()
  pipe.stdout.close()

  if status != 0:
    log('Non-Zero Exit Code: %s: %s: %s' % (status, command, output_error), logging.INFO)

  # Cache all of this, with a timestamp so we can cache, if we want
  #TODO(g): Come up with a better way to restrict logging these.  rrdtool is a hog...
  if not command.startswith('rrdtool'):
    sharedstate.Set('__internals.run', command, (time.time(), status, output, output_error))

  return (status, output, output_error)
  

def TimeSeriesCollection(run_item, result):
  """Collect time series information into timeseries data source."""
  collect_items = run_item['timeseries collect']
  
  # Process all TS's as lists of TS collection items
  for item in collect_items:
    #TODO(g): Get rid of the indirection, this is just a shim between being able
    #   to only do ONE TS collect per "timeseries collect" statement, and being
    #   able to do N of them.  Better, and simple solution, but clean up later.
    TimeSeriesCollectionItem({'timeseries collect': item}, result)

  
def TimeSeriesCollectionItem(run_item, result):
  """Collect time series information into timeseries data source."""
  collect = run_item['timeseries collect']
  graph = collect.get('graph', None)
  
  key_series = collect.get('key', None)
  filename = collect['path']
  filename_template = filename # Used with keyseries
  interval = collect['interval']
  
  #NOTE(g): Marking THIS as the time all this collection occured, even if it
  #   happened at a different time.
  #TODO(g): That sucks, have to figure out clever way to keep primitives as
  #   the data types (JUST a dict being returned), and track that time it was
  #   completed.  I suppose the RunThread or whatever that ran it, Process(),
  #   would know that and could track it and be accessable in request_state?
  #   Ponder and illuminate.
  occurred = time.time()
  
  #print 'TSCollect: %s' % collect
  #print 'Result: %s' % result
  
  # Get all the keys we will process
  if key_series:
    if key_series not in result:
      Exception('Key series key not found in result: %s: %s: %s' % (filename, key_series, result))
    
    items = {}
    for key in result[key_series]:
      items[key] = result[key_series]
    
    #log('*** Key Series graph:  %s' % items)
  else:
    items = [None]
  
  
  create_fields = collect['fields']
  if not create_fields:
    log('No field data returned: %s ')
    return
  
  for key_series_item in items:
    # If this is not a keyed time series
    if key_series_item != None:
      # Do not conflict with directory structures or add stupid spaces
      key_str = key_series_item.replace('/', 'slash').replace(' ', 'space')
      
      # Format the filename
      filename = filename_template.replace('%(key)', key_str)
    
    # If this file_template also has a node name tag, replace it
    if '%(node)s' in filename:
      node_name = unidist.node.GetNamePathReady()
      filename = filename.replace('%(node)s', node_name)
    
    # If the directory doesnt exist yet, create it
    #TODO(g): This is for the nodes to have individual dirs, in the future I can
    #   add a test to make sure it only does ONE directory level of creation,
    #   and raise an exception on more as it's structure should be there so we
    #   arent running in the wrong directory.  Structure is important, and
    #   testing it allows us to more accurately run, because we know were
    #   running in a valid structure, which gives a certain level of assurance
    #   we're running in the right path structure and so our functioning will
    #   be as expected.
    if not os.path.isdir(os.path.dirname(filename)):
      # Make all the paths for this file to have a directory to be put in
      try:
        os.makedirs(os.path.dirname(filename))
      except Exception, e:
        pass
    
    # If we dont have this time series file yet, create it
    if not os.path.exists(filename):
      timeseries.Create(filename, interval, create_fields)
    
    # Create the fields from our create_fields and result
    # Only add fields that are in create_fields, from the result
    fields = {}
    # If this is not a keyed time series
    if key_series_item == None:
      for key in create_fields:
        # Save the key, if we have it
        if key in result:
          fields[key] = result[key]
        # Else, we dont have it: Not a Number
        else:
          fields[key] = 'NaN'
    
    # Else, this is a keyed item series, dig into the result appropriately
    else:
      for key in create_fields:
        # Save the key, if we have it
        if key_series in result and key_series_item in result[key_series] and \
              key in result[key_series][key_series_item]:
          fields[key] = result[key_series][key_series_item][key]
        else:
          print 'Couldnt find field: %s: %s: %s: %s' % (key_series, key_series_item, key, filename)
          fields[key] = 'NaN'
    
    # Store our values in the time series file
    #print 'Store: %s: %s: %s: %s' % (filename, interval, occurred, fields)
    timeseries.Store(filename, interval, occurred, fields)
    
    # Cache this entry
    sharedstate.Set('__internals.timeseries', filename, (occurred, collect, fields))
    
    # Graph the RRD
    #TODO(g): Remove, instead of just not using...
    if 0 and graph:
      for graph_item in graph:
        method = graph_item.get('method', 'STACK')
        
        node_name = unidist.node.GetNamePathReady()
        
        # Title
        if key_series_item:
          title = str(graph_item.get('title', 'title')).replace('%(key)s', key_series_item).replace('%(node)s', node_name)
          graph_path = graph_item['path'].replace('%(key)s', key_series_item.replace('/', 'slash').replace(' ', 'space')).replace('%(node)s', node_name)
        else:
          title = graph_item.get('title', 'title')
          graph_path = graph_item['path'].replace('%(node)s', node_name)
        
        label_vertical = graph_item.get('vertical label', 'vertical label')
        
        # If the directory doesnt exist yet, create it
        #TODO(g): This is for the nodes to have individual dirs, in the future I can
        #   add a test to make sure it only does ONE directory level of creation,
        #   and raise an exception on more as it's structure should be there so we
        #   arent running in the wrong directory.  Structure is important, and
        #   testing it allows us to more accurately run, because we know were
        #   running in a valid structure, which gives a certain level of assurance
        #   we're running in the right path structure and so our functioning will
        #   be as expected.
        if not os.path.isdir(os.path.dirname(graph_path)):
          # Make all the paths for this file to have a directory to be put in
          os.makedirs(os.path.dirname(graph_path))
        
        #TODO(g): Delay graphing by INTERVAL seconds, also, node restrict or \
        #   flag restrict or something, to make it easy to specify only some \
        #   hosts graph at all.  Then theres the different time periods to \
        #   autograph...
        timeseries.Graph(filename, graph_path, create_fields, graph_item['fields'], method, title, label_vertical)



def ExecuteScript(python_script, pipe_data, block, request_state, input_data, tag=None, cwd=None, env=None, block_parent=None):
#def ExecuteScript(python_script, tag, block, data, state, chain_output, env=None, block_parent=None):
  """Execute the specified script.  This will ensure it is imported, and
  re-imported if the code changes on the disk.
  
  TODO(g): Implement in-memory cache of md5-sums from the Manager, specifying
      the md5-sum of each script, and do not import if it is not the same.
      Instead, alert on a locally changed script.
  """
  
  # Import the Python Script module
  script_module = code_python.GetPythonScriptModule(python_script)
  
  if script_module == None:
    log('Failed to find python script: %s' % os.path.abspath(python_script), logging.ERROR)
    return
  
  # Execute the script, and return the data (which will update chain_output)
  try:
  #if 1:
    ##DONE(g): SUPER AWESOME!: Change Execute() to ProcessBlock() so that EVERY
    #   program written for procblock is SEEN as a block processor.  So people
    #   think that they are writing another processor in a chain of processors
    #   which can spawn more chains of processors at whim.  It's an integrated
    #   way of thinking about how code fits into the bigger picture...
    #         ...AND ITS THE SAME!!!  The SAME as all the data procblocks.
    result = script_module.ProcessBlock(pipe_data, block, request_state,
                                        input_data, tag=tag, cwd=cwd, env=env,
                                        block_parent=block_parent)
    #result = script_module.ProcessBlock(tag, block, data, state, chain_output, env=env, block_parent=block_parent)
    #TODO(g): Remove this old method when it's not needed any more.
    #result = script_module.Execute(data, chain_output, state, env)
    
    # Cache this entry
    sharedstate.Set('__internals.execute', python_script, (time.time(), result))
    
  except Exception, e:
    #TODO(g): Print the exception out here, so we keep all this data together,
    #   Im only doing it this less-optimal way (exception and python script
    #   are not in the same lines, and will be hard to see when threaded),
    #   because I havent baked Python 2.6 into the EC2 AMIs yet.
    log('Exception in script: %s: %s' % (python_script, e))
    #raise RunScriptFailedCondition(e)#TODO(g): Better...
    raise
  
  return result


class RunScriptFailedCondition(Exception):
  """Failed to pass all "if" conditions."""



class RunThreadHandler:

  def __init__(self):
    self.run_thread_id_next = 0
    self.run_thread_id_lock = threading.Lock()
    
    self.run_thread_objects = {}
  
  
  def GetNextRunThreadId(self):
    """Returns the next action_id, for a new RunThread."""
    self.run_thread_id_lock.acquire()
    
    # Save next ID
    next_id = self.run_thread_id_next
    
    # Increment next ID
    self.run_thread_id_next += 1
    
    self.run_thread_id_lock.release()
    
    return next_id
  
  
  def Add(self, run_thread_object):
    """Adds this run_thread_object.  Get() by run_thread_object.id"""
    self.run_thread_objects[str(run_thread_object.id)] = run_thread_object
  
  
  def Get(self, run_thread_id):
    """Returns run_threadObject specified, or None if not found."""
    if run_thread_id in self.run_thread_objects:
      return self.run_thread_objects[str(run_thread_id)]
    else:
      return None



class RunThread(threading.Thread):

  def __init__(self, run_thread_id, pipe_data, block, request_state,
               input_data, tag=None, cwd=None, env=None, block_parent=None):
  #def __init__(self, run_thread_id, run_block_data, data, state, chain_output,
  #             env=None, cwd=None):
    self.id = run_thread_id
    self.run_block_data = copy.deepcopy(block)
    
    self.pipe_data = pipe_data
    self.request_state = request_state
    # Ensure input_data is a separate dictionary, and will not update the
    #   original if a programmer does something sloppy.
    #NOTE(g): This is NOT a deepcopy, so a programmer could still update a
    #   sub-item, since they are still the same references.  If they want to
    #   do that, I'm letting them, even though it is sloppy design wise, it is
    #   not worth the effort to build the wall, and still provide easy access.
    #   This is a rapid development effort, all optimization is for short
    #   development times and desired functionality correctness, not stopping
    #   people from hanging themselves with the rope that gives them.
    if type(input_data) in (dict, ):
      self.input_data = dict(input_data)
    else:
      self.input_data = None
    self.tag = tag
    self.cwd = cwd
    self.env = env
    self.block_parent = block_parent
    
    # When we have finished running, the chain_output goes here
    self.output = None
    
    # Add ourselves to our pipe_data, our run script block needs this
    self.pipe_data['run_thread.%s' % self.id] = self
    
    # Running flags
    self.create_time = time.time()
    self.has_started = False
    self.is_running = False
    self.status = None
    self.success = None
    self.run_start = None
    self.run_finish = None
    self.error = None
    
    # For now, just save each of these as text, can create objects later
    #TODO(g): Create ActionStage(name, message, status), for BEGIN/UPDATE/END
    #   so we can track all stages of running hyper-intelligently...
    self.stages = []
    
    # Cache this entry
    sharedstate.Set('__internals.threads', run_thread_id, self)
    
    # Initialize the super class for the thread
    threading.Thread.__init__(self)
  
  
  def __repr__(self):
    # Clean the data for printing
    scripts = []
    
    if type(self.run_block_data) == dict:
      if 'script' in self.run_block_data:
        scripts.append(self.run_block_data['script'])
    elif type(self.run_block_data) == list:
      # Process run block entries
      for item in self.run_block_data:
        if 'script' in item:
          scripts.append(item['script'])
    
    if self.is_running:
      output = '<span style="color:green;">%s</span>: <b>Is Running:</b> %s  <b>Scripts:</b> %s' % (self.id, self.is_running, scripts)
    else:
      output = '<span style="color:red;">%s</span>: <b>Is Running:</b> %s  <b>Scripts:</b> %s' % (self.id, self.is_running, scripts)
    
    return output
  
  
  def HtmlDescription(self):
    output = '<h2>Thread %s:</h2>\n<br>' % self.id
    output += '<b>Tag:</b> %s<br>\n' % self.tag
    output += '\n<b>Created:</b> %s<br>\n' % unidist.html.PrintTime(self.create_time)
    output += '<b>Has Started:</b> %s<br>\n' % self.has_started
    if self.is_running:
      output += '<font color="green"><b>Is Running:</b> %s</font><br>\n' % self.is_running
    else:
      output += '<font color="red"><b>Is Running:</b> %s</font><br>\n' % self.is_running
    output += '<b>Started:</b> %s<br>\n' % unidist.html.PrintTime(self.run_start)
    output += '<b>Finished:</b> %s<br>\n' % unidist.html.PrintTime(self.run_finish)
    #TODO(g): Turn into TimeAgo() format which has nicer minutes/hour/weeks/etc
    if self.run_finish:
      output += '<b>Duration:</b> %0.1f seconds<br>\n' % (self.run_finish - self.run_start)
    
    output += '<br><b>Input Data:</b><br>\n<pre><code>%s</code></pre><br>\n' % pprint.pformat(self.input_data)
    output += '<br><b>Run Block:</b><br>\n<pre><code>%s</code></pre><br>\n' % pprint.pformat(self.run_block_data)
    output += '<br><b>Pipe Data:</b><br>\n<pre><code>%s</code></pre><br>\n' % pprint.pformat(self.pipe_data)
    output += '<br><b>Output:</b><br>\n<pre><code>%s</code></pre><br>\n' % pprint.pformat(self.output)
    output += '<br><b>Block Parent:</b><br>\n<pre><code>%s</code></pre><br>\n' % pprint.pformat(self.block_parent)
    
    return output
  
  
  def StageBegin(self, name, message):
    """Logging Stages: Begin a new stage"""
    data = {'type':'begin', 'time':time.time(), 'name':name, 'message':message}
    self.stages.append(data)
  
  
  def StageUpdate(self, name, message):
    """Logging Stages: Begin a new stage"""
    data = {'type':'update', 'time':time.time(), 'name':name, 'message':message}
    self.stages.append(data)
  
  
  def StageEnd(self, name, message, status):
    """Logging Stages: Begin a new stage"""
    data = {'type':'end', 'time':time.time(), 'name':name, 'message':message,
            'status':status}
    self.stages.append(data)
  
  
  def StageError(self, name, message):
    """Logging Stages: Begin a new stage"""
    data = {'type':'error', 'time':time.time(), 'name':name, 'message':message}
    self.stages.append(data)
  
  
  def Log(self, name, message):
    """Logging:  Regular old logging."""
    data = {'type':'log', 'time':time.time(), 'name':name, 'message':message}
    self.stages.append(data)
  
  
  def GetOutput(self):
    """For the base class, just return the output, whatever it is."""
    return self.output
  
  
  def run(self):
    # We're starting
    self.has_started = True
    self.run_start = time.time()
    
    self.is_running = True
    
    #TODO(g): Add the ActionObject to data, so we can do StageStart/StageUpdate/StageEnd function calls and shit
    #TODO(g): Get the scripts path out of the run_block_data['scripts']?
    try:
      self.output = RunScriptBlock(self.pipe_data, self.run_block_data,
                                   self.request_state, self.input_data,
                                   tag='run', cwd=self.cwd, env=self.env,
                                   block_parent=self.block_parent)
    except Exception, e:
      details = error_info.GetExceptionDetails()
      self.error = details
      log(details, logging.ERROR)
    
    self.is_running = False
    self.run_finish = time.time()
  
  
  def Render(self):
    """Render all the interesting information about the state and our Stages."""
    if self.error:
      output = '<h4 style="color: red">ERROR: %s</h4>\n' % self.error
    elif self.run_finish:
      output = '<h4>Completed: Duration %0.1f seconds</h4>\n' % (self.run_finish - self.run_start)
      if 'output' in self.output:
        output += '<br>%s<br><br>' % self.output['output']
    elif self.is_running:
      output = '<h4>Running... %0.1f seconds</h4>\n' % (time.time() - self.run_start)
    else:
      output = '<h4>Not yet running...</h4>\n'
    
    # Render our stages, in reverse order so newest is first
    stages = list(self.stages)
    stages.reverse()
    output += '<table border="1" cellspacing="0">\n'
    for stage in stages:
      output += '<tr>'
      output += '  <td valign="top"><b>%s</b></td>\n' % stage['name']
      output += '  <td valign="top" width="10%%">%0.1fs</td>\n' % (stage['time'] - self.run_start)
      output += '  <td valign="top">%s</td>\n' % stage['type'].upper()
      output += '  <td valign="top">%s</td>\n' % stage['message']
      if 'status' in stage:
        if stage['status']:
          output += '  <td valign="top" style="color: green">Success</td>\n'
        else:
          output += '  <td valign="top" style="color: red">Failure</td>\n'
      else:
        output += '  <td valign="top">&nbsp;</td>\n'
      
      output += '</tr>\n'
    output += '</table>\n'
    
    #output += '<br><br>Run Thread: %s' % self.id
    
    self.output = output
    
    return output


class RunThread_IntervalCache(RunThread):
  """This run thread will run a block at a specified interval until a timer
  has expired or a lock is released.
  """
  
  def __init__(self, run_thread_id, pipe_data, block, request_state,
               input_data, tag=None, cwd=None, env=None, block_parent=None,
               interval=None, run_lock='__running', duration=None,
               history_maximum=None):
    """Creates a RunThread with extra parameters to cache the content, and
    repeat the run every interval-seconds, until either a run_lock is released
    or the duration (if specified) is over.
    """
    # Initialize the run thread.
    RunThread.__init__(self, run_thread_id, pipe_data, block, request_state, input_data,
              tag=tag, cwd=cwd, env=env, block_parent=block_parent)
    
    # Get our lock name, use when running
    self.mutex = 'mutex.thread.%s' % self.id
    
    # Save extra information
    if interval != None:
      self.interval = interval
    else:
      self.interval = RUN_CACHE_DEFAULT_INTERVAL
    self.run_lock = run_lock
    #NOTE(g): Duration allows impromtu timeseries collection!  Just run a
    #   5 second interval (or 1 second!) script for 30 seconds, and return the
    #   result, and process the time series, to discover data you dont want to
    #   monitor all the time!
    self.duration = duration
    if history_maximum != None:
      self.history_maximum = history_maximum
    else:
      self.history_maximum = RUN_CACHE_DEFAULT_HISTORY_MAXIMUM
    
    # History of outputs
    self.history = []
    
    # The last time this interval RunThread was run
    self.last_run = None
    
    # The last time this interval RunTHread was finished running
    self.last_finished = None


  def GetOutput(self):
    """For running in an interval, return the last output, unless it hasnt
    finishing running once then, then stall until it finishes running."""
    while self.last_finished == None:
      #log('Waiting for interval thread output: %s' % self.id)
      time.sleep(0.1)
    
    return self.output


  def run(self):
    log('Running Thread: Starting: %s' % self.id)
    
    # We're starting
    self.has_started = True
    self.run_start = time.time()
    
    self.is_running = True
    
    # Loop forever, until either the run_lock is released, or the duration has expired
    while (self.run_lock and sharedlock.IsLocked(self.run_lock)) or (self.duration and self.create_time + self.duration < time.time()):
      # Force quit if the program is quitting
      if not sharedlock.IsLocked('__running'):
        break
      
      try:
        # The last time we were run...
        self.last_run = time.time()
        
        # This thread will 
        if sharedlock.Acquire(self.mutex):
          #print 'Interval %s: Running block: %s' % (self.id, self.run_block_data['script'])
          
          # Do not cache this run
          input_data = dict(self.input_data)
          input_data['__nocache'] = True
          
          #self.output = ExecuteScript(self.run_block_data[0]['script'],
          #                            self.pipe_data,
          #                       self.run_block_data, request_state, input_data,
          #                       tag=tag, cwd=cwd, env=env,
          #                       block_parent=block_parent)
          self.output = ExecuteScript(self.run_block_data['script'],
                                      self.pipe_data, self.run_block_data,
                                      self.request_state, self.input_data,
                                      tag='run', cwd=self.cwd, env=self.env,
                                      block_parent=self.block_parent)
          
          #print 'Interval Run Thread Output: %s' % self.output
          
          # Add the latest output to our history
          self.history.append(self.output)
          
          # If our history is over the max, then crop it to the max
          if len(self.history) > self.history_maximum:
            self.history = self.history[-self.history_maximum:]
          
          # Mark the last time we finished running
          self.last_finished = time.time()
          
          if 'timeseries collect' in self.run_block_data:
            TimeSeriesCollection(self.run_block_data, self.output)
          
          # Release the lock
          sharedlock.Release(self.mutex)
          
          # Sleep our interval
          #TODO(g): CRITICAL: Reduce out time it took to run, intervals should be
          #   even, not gapped
          time.sleep(self.interval)
      
      except Exception, e:
        details = error_info.GetExceptionDetails()
        self.error = details
        log(details, logging.ERROR)
      
      ## If we hold the mutex, always release it
      #finally:
      #  if mutex_held:
      #    sharedlock.Release('mutex.run_thread.%s' % self.id)
    
    self.is_running = False
    self.run_finish = time.time()
    
    log('Running Thread: Quitting: %s' % self.id)


def RunScriptBlock(pipe_data, block, request_state, input_data, tag=None, cwd=None, env=None, block_parent=None):
  # Get the script path prefix, if there is one, from the block
  #TODO(g): Document or improve this.
  if block_parent:
    script_path_prefix = block_parent.get('script_path_prefix', None)
  else:
    script_path_prefix = None
  
  # Time the script started
  start_time = time.time()
  
  # Execute the chain of scripts
  for item in block:
    
    #log('RunBlock: Item: %s' % item)
    
    # If this is a script
    if 'script' in item:
      
      # If this in an Interval Caching script...
      if 'cache' in item and '__nocache' not in input_data:
        
        if 'thread_id' not in item:
          #TODO(g): This will keep creating them forever, fix!
          thread_id = sharedcounter.GetIncrement('run_thread')
          raise Exception('thread_id not found: This will keep creating them forever, fix!')
        else:
          thread_id = item['thread_id']
        
        # Try to get the run thread
        try:
          run_thread = sharedstate.Get('threads', thread_id)
        except Exception, e:
          run_thread = None
        
        # If we dont already have a run thread by this name, create it
        if run_thread == None:
          # Create the run thread
          log('Creating interval thread: %s: %s' % (thread_id, item))
          run_item = item
          run_thread = RunThread_IntervalCache(thread_id, pipe_data, run_item, request_state, input_data, tag=tag, cwd=cwd, env=env,
                                               block_parent=block_parent, interval=item.get('interval', None),
                                               duration=item.get('duration', None), history_maximum=item.get('history', None))
          
          # Save the thread
          sharedstate.Set('threads', thread_id, run_thread)
          
          # Start the thread
          run_thread.start()
        
        # Get the result, the last entry in it's history of output
        result = run_thread.GetOutput()
        
        # Update chain_output with result
        if type(result) == dict:
          pipe_data.update(result)
          
          # Timeseries Collection
          #TODO(g): Generalize this so we can do it from anywhere and it is a
          #   normal tag processing.
          if 'timeseries collect' in item:
            TimeSeriesCollection(item, result)
        
        else:
          # Get the python script
          python_script = item['script']
          log('Python Script Execute did not return dict: %s: %s' % (python_script, result), logging.ERROR)
      
      
      # Else, this is not an Interval Caching script, so just run it
      else:
        #print 'Running Python Script: Directly'
        
        # Get the python script
        python_script = item['script']
        
        # If we have a script prefix, and this isnt an absolute path, prefix it
        if script_path_prefix and not python_script.startswith('/'):
          python_script = '%s/%s' % (script_path_prefix, python_script)
        
        # Execute the script, get the result to update chain_output
        result = ExecuteScript(python_script, pipe_data, block, request_state,
                               input_data, tag=tag, cwd=cwd, env=env,
                               block_parent=block_parent)
        
        # Update chain_output with result
        if type(result) == dict:
          pipe_data.update(result)
          
          # Timeseries Collection
          #TODO(g): Generalize this so we can do it from anywhere and it is a
          #   normal tag processing.
          if 'timeseries collect' in item:
            TimeSeriesCollection(item, result)
        else:
          log('Python Script Execute did not return dict: %s: %s' %
              (python_script, result), logging.ERROR)
    
    
    # Else, if we are 
    elif 'set' in item:
      # Set all the keypairs specified into our data
      for (key, value) in item['set'].items():
        # Update the data, we are using
        pipe_data[key] = value
    
    
    # Else, if we are Changing Directories
    elif 'cd' in item:
      dir = item['cd']
      
      # Check if any of our script_input keys are variables here
      found = False
      for key in pipe_data:
        if '%%(%s)' % key in dir:
          found = True
          break
      
      # If we found a script_input variable, then expand the variables
      if found:
        dir = dir % data
      
      #TODO(g): NOTTHREADSAFE: Is this safe to do outside of a child thread?
      #   It could screw things up...
      #TODO(g): ACTUAL FIX: DO THIS!: Just keep track of the CWD string, and
      #   append it, so it is ALWAYS an absolute path (security is better too),
      #   and that way it will be thread safe and not fucking up our relative
      #   pathed file loads!  (Dont do those relative EITHER!  Not thread safe!)
      log('Changing working directory: %s' % dir)
      os.chdir(dir)
    
    # Else, if we are execute Shell commands
    elif 'shell' in item:
      cmd = item['shell']
      
      log('Executing shell command: %s' % cmd)
      
      #TODO(g): Set up the ENV vars!
      #TODO(g): SECURITY:CRITICAL: Totally shit security.  FIX FIX FIX!!!
      #os.system(cmd)
      (status, output, output_error) = Run(cmd)
      
      if 'status' not in pipe_data:
        pipe_data['status'] = []
      if 'output' not in pipe_data:
        pipe_data['output'] = ''
      if 'output_error' not in pipe_data:
        pipe_data['output_error'] = ''
      
      pipe_data['status'].append(status)
      pipe_data['output'] += output
      pipe_data['output_error'] += output_error
    
    # Else, if we are invoking a script
    elif 'call' in item:
      log('ERROR: Not yet implemented.  This will call another script, but its name.  invoked=True', logging.CRITICAL)
      pass
    
    # Else, if we are invoking a script
    elif 'except' in item:
      #log('ERROR: Not yet implemented.  This will deal with any exceptions in any of the preceding items.', logging.CRITICAL)
      log('ERROR: Not yet implemented.  This will deal with any exceptions in any of the preceding items.', logging.ERROR)
      pass
    
    
    # Else, error
    else:
      raise Exception('Unknown type of script: %s' % item)
  
  
  # Get the duration
  duration = time.time() - start_time
  
  # If the chain_output doesnt already have a duration, add it
  #TODO(g): How to make this not stomp on things?  So that this can be tracked
  #   in a useful way for things in a pipe...
  if 'duration' not in pipe_data:
    pipe_data['__duration'] = duration
  
  
  # Save when this script started, so we know which RRD slot it's best for
  pipe_data['__start_time'] = start_time

  
  #log('Script result: %s.%s.%s.%s: %s' % (script, deployment, service, instance_name, chain_output))
  
  
  return pipe_data
