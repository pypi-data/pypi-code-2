"""
Instantiates the apropriate controller.

It follows the naming convention defined by appending 
the hypervisor name, as gotten from the provided configuration, 
with "Controller". Such a class must be exist and be accesible.

Note that if the controller class resides in a different package,
its name must include the package name as well.
"""

try:
    import logging
    import inject

    from twisted.internet import defer
    from vmcontroller.common import support, exceptions
except ImportError, e:
    print "Import error in %s : %s" % (__name__, e)
    import sys
    sys.exit()

CONTROLLERS_PATH = "hypervisors" #relative to this file

logger = logging.getLogger( support.discoverCaller() )

@inject.param('config')
def _createController(config):
    """
    Creates the appropriate (hypervisor) controller based on the
    given configuration. 

    This is the place where to perform particular initialization tasks for 
    the particular hypervisor controller implementations.

    @param config: an instance of L{ConfigParser}
    """
    hv = config.get('hypervisor', 'name')
    hvMod = None
    logger.debug("Hypervisor specified in config: '%s'" % hv)
    fqHvName = "%s.%s" % (CONTROLLERS_PATH, hv)
  
    try:
        hvPkg = __import__(fqHvName, globals=globals(), level=-1)
        hvMod = getattr(hvPkg, hv)
    except ImportError, e:
        msg = "Hypervisor '%s' is not supported. Error: %s" % (hv, e)
        logger.fatal(msg)
        raise exceptions.ConfigError(msg)

    logger.info("Using %s as the HyperVisor" % hvMod.__name__)

    return hvMod 

_controller = None
def _getController():
    global _controller
    if not _controller:
        _controller = _createController()

    return _controller

def version():
    """Returns version string of the hypervisor"""
    return defer.maybeDeferred( _getController().version )

def createVM(vboxFile):
    """Creates virtual machine with given vbox file.
    @param vboxFile: VirtualBox Machine Definition XML file."""
    return defer.maybeDeferred( _getController().createVM, vboxFile )

def removeVM(vm):
    """Removes virtual machine. NOTE: This operation is undo-able.
    @param vm: Virtual machine's name."""
    return defer.maybeDeferred( _getController().removeVM, vm)

def start(vm, guiMode=False):
    """Starts virtual machine.
    @param vm: Virtual machine's name.
    @param guiMode: Run in a window or as a background process."""
    return defer.maybeDeferred( _getController().start, vm, guiMode )

def shutdown(vm):
    """ACPI Shutdown virtual machine.
    @param vm: Virtual machine's name."""
    return defer.maybeDeferred( _getController().shutdown, vm )

def reset(vm):
    """Sends ACPI power reset signal to virtual machine.
    @param vm: Virtual machine's name."""
    return defer.maybeDeferred( _getController().reset, vm )

def powerOff(vm):
    """Turn off virtual machine, without a proper shutdown.
    @param vm: Virtual machine's name."""
    return defer.maybeDeferred( _getController().powerOff, vm )

def pause(vm): 
    """Pauses running virtual machine.
    @param vm: Virtual machine's name."""
    return defer.maybeDeferred( _getController().pause, vm )

def resume(vm):
    """Resumes a paused virtual machine.
    @param vm: Virtual machine's name."""
    return defer.maybeDeferred( _getController().resume, vm )

def states():
    """Returns different possible states a VM can have."""
    return defer.maybeDeferred( _getController().states )

def getState(vm):
    """Returns state of a virtual machine.
    @param vm: Virtual machine's name."""
    return defer.maybeDeferred( _getController().getState, vm )

def saveState(vm):
    """Saves state of the virtual machine.
    @param vm: Virtual machine's name."""
    return defer.maybeDeferred( _getController().saveState, vm )

def discardState(vm):
    """Discards any saved state of the virtual machine.
    @param vm: Virtual machine's name."""
    return defer.maybeDeferred( _getController().discardState, vm )

def takeSnapshot(vm, name, desc = ""):
    """Saves snapshot of current virtual machines vm state.
    @param vm: Virtual machine's name.
    @param name: Name of the snapshot.
    @param desc: Snapshot's description."""
    return defer.maybeDeferred( _getController().takeSnapshot, vm, name, desc )

def restoreSnapshot(vm, name):
    """Restores snapshot
    @param vm: Virtual machine's name."""
    return defer.maybeDeferred( _getController().restoreSnapshot, vm, name )

def deleteSnapshot(vm, name):
    """Saves snapshot of current virtual machines vm state.
    @param vm: Virtual machine's name.
    @param name: Name of the snapshot."""
    return defer.maybeDeferred( _getController().deleteSnapshot, vm, name )

def listVMs():
    """Returns a list of virtual machines"""
    return defer.maybeDeferred( _getController().listVMs )

def listVMsWithState():
    """Returns a dictionary of virtual machines with state"""
    return defer.maybeDeferred( _getController().listVMsWithState )

def listRunningVMs():
    """Returns a list of running VMs"""
    return defer.maybeDeferred( _getController().listRunningVMs )

def listSnapshots(vm):
    """Returns a list of snaphots of a particular VM.
    @param vm: Virtual machine's name."""
    return defer.maybeDeferred( _getController().listSnapshots, vm )

def getNamesToIdsMapping():
    """getNamesToIdsMapping"""
    return defer.maybeDeferred( _getController().getNamesToIdsMapping )

def getIdsToNamesMapping(): 
    """getIdsToNamesMapping"""
    return defer.maybeDeferred( _getController().getIdsToNamesMapping )

def getStats(vm, key = '*'):
    """Returns all the performance data for a valid key. For VirtualBox, the useful keys are 'name' and 'values_as_string' for a metric.
    @param vm: Virtual machine's name.
    @param key: Metric key."""
    return defer.maybeDeferred( _getController().getStats, vm, key)
