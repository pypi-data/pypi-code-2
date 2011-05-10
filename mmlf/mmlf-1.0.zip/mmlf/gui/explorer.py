# Maja Machine Learning Framework
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.


import sys

from threading import Thread

from PyQt4 import QtGui, QtCore

import mmlf
from mmlf.gui.viewers import VIEWERS
from mmlf.framework.observables import OBSERVABLES, StateActionValuesObservable, \
                                    FunctionOverStateSpaceObservable
from mmlf.gui.log_viewer import LogViewer

class MMLFExplorer(QtGui.QWidget):
        
    def __init__(self, parent=None):
        super(MMLFExplorer, self).__init__(parent)
        self.parent = parent
        
        self.world = None
        
        # Redirect stdout/stderr to viewer (first thing to do)
        mmlfStdOutViewer = QtGui.QTextEdit()
        class OutLog(object):       
            def __init__(self, wrappedOutput):
                self.wrappedOutput = wrappedOutput
            def write(self, m):       
                mmlfStdOutViewer.append(m)
                self.wrappedOutput.write(m)
            def flush(self):
                self.wrappedOutput.flush()
            
        sys.stdout = OutLog(sys.stdout)
        sys.stderr = OutLog(sys.stderr)
        
        # Forwarding of exceptions to GUI
        self.parent.exceptionOccurredSignal.connect(parent._exceptionOccurred)
        
        # The main layout
        self.vlayout = QtGui.QVBoxLayout()
        # Add WorldConfigEditor to vlayout
        from mmlf.gui.world_config_editor import WorldConfigEditor # must be imported lazily!s
        self.worldConfigEditor = WorldConfigEditor(self, self.vlayout)
        
        # Viewer Selection
        viewerLabel = QtGui.QLabel("Viewer")
        self.viewerComboBox = QtGui.QComboBox(self)
        self.viewerComboBox.addItems(sorted(VIEWERS.getViewerNames()))
        self.viewerComboBox.setToolTip("Viewer that will be added to monitor "
                                       "progress of agent in environment")
        self.selectedViewer = sorted(VIEWERS.getViewerNames())[0]
        viewerAddButton = QtGui.QPushButton("Add")
              
        parent.connect(self.viewerComboBox,
                       QtCore.SIGNAL('activated (const QString&)'), 
                       self._viewerSelectionChanged)
        self.connect(viewerAddButton, QtCore.SIGNAL('clicked()'), 
                     self._addViewer)
        # Automatically update viewer combobox when new viewers are created
        # during runtime
        def updateViewersComboBox(viewer, action):
            self.viewerComboBox.clear()
            self.viewerComboBox.addItems(sorted(VIEWERS.getViewerNames()))
            self.selectedViewer = sorted(VIEWERS.getViewerNames())[0]           
        self.updateViewersComboBox = updateViewersComboBox
        
        VIEWERS.addObserver(self.updateViewersComboBox)

        # Monitor Configuration
        monitorConfigureButton = QtGui.QPushButton("Configure Monitor")
        parent.connect(monitorConfigureButton, QtCore.SIGNAL('clicked()'), 
                       self._configureMonitor)
        
        # Help button
        helpButton = QtGui.QPushButton("Help")
        parent.connect(helpButton, QtCore.SIGNAL('clicked()'), 
                       self._help)

        # World control
        worldInitButton = QtGui.QPushButton("Init World")
        worldStartButton = QtGui.QPushButton("Run World")
        worldStopButton = QtGui.QPushButton("Stop World")
        worldStepButton = QtGui.QPushButton("Step")
        worldEpisodeButton = QtGui.QPushButton("Episode")

        self.connect(worldInitButton, QtCore.SIGNAL('clicked()'), 
                     self._initWorld)       
        self.connect(worldStartButton, QtCore.SIGNAL('clicked()'), 
                     self._startWorld)
        self.connect(worldStopButton, QtCore.SIGNAL('clicked()'), 
                     self._stopWorld)
        self.connect(worldStepButton, QtCore.SIGNAL('clicked()'), 
                     self._executeSteps)
        self.connect(worldEpisodeButton, QtCore.SIGNAL('clicked()'), 
                     self._executeEpisode)
        
        # Load and store world config
        configLoadButton = QtGui.QPushButton("Load Config")
        configStoreButton = QtGui.QPushButton("Store Config")
        
        self.connect(configLoadButton, QtCore.SIGNAL('clicked()'), 
                     self.worldConfigEditor.loadConfig)       
        self.connect(configStoreButton, QtCore.SIGNAL('clicked()'), 
                     self.worldConfigEditor.storeConfig)
        
        # Log viewer
        mmlfLogView = LogViewer(self)
        
        # Creating the main Tab-Widget
        self.tabWidget = QtGui.QTabWidget(self)
        self.tabWidget.setTabsClosable(True)
        self.tabWidget.addTab(mmlfStdOutViewer, "StdOut/Err")
        self.tabWidget.addTab(mmlfLogView, "MMLF Log")
        self.tabWidget.setCurrentWidget(mmlfLogView)
        self.connect(self.tabWidget, QtCore.SIGNAL('tabCloseRequested (int)'), 
                     self._closeTab)

        # Creating layouts       
        self.hlayoutViewer = QtGui.QHBoxLayout()
        self.hlayoutViewer.addWidget(viewerLabel)
        self.hlayoutViewer.addWidget(self.viewerComboBox)
        self.hlayoutViewer2 = QtGui.QHBoxLayout()
        self.hlayoutViewer2.addWidget(viewerAddButton)
        self.hlayoutViewer.addLayout(self.hlayoutViewer2)
        
        self.hlayoutWorld = QtGui.QHBoxLayout()
        self.hlayoutWorld.addWidget(worldInitButton)
        self.hlayoutWorld.addWidget(worldStartButton)
        self.hlayoutWorld.addWidget(worldStopButton)
        self.hlayoutWorld.addWidget(worldStepButton)
        self.hlayoutWorld.addWidget(worldEpisodeButton)
        self.hlayoutWorld.addWidget(configLoadButton)
        self.hlayoutWorld.addWidget(configStoreButton)
        self.hlayoutWorld.addWidget(monitorConfigureButton)
        self.hlayoutWorld.addWidget(helpButton)
        
        self.vlayout.addLayout(self.hlayoutViewer)
        self.vlayout.addLayout(self.hlayoutWorld)
        self.vlayout.addWidget(self.tabWidget)
        
        self.setLayout(self.vlayout)
        
    def tearDown(self):
        if self.world is not None:
            self._stopWorld()
            
    def _help(self):
        self.parent.documentationTab.load(QtCore.QUrl("http://mmlf.sourceforge.net/tutorials/quick_start_gui.html#explorer"))
        self.parent.tabWidget.setCurrentWidget(self.parent.documentationTab)
                
    def _viewerSelectionChanged(self, selectedViewer):
        self.selectedViewer = str(selectedViewer)
        
    def _addViewer(self):
        viewerWidget = VIEWERS.getViewer(self.selectedViewer)()
        self.tabWidget.addTab(viewerWidget, self.selectedViewer)

    def _closeTab(self, tabIndex):
        if tabIndex <= 1: return # The stdout and log windows cannot be removed
        self.tabWidget.widget(tabIndex).close()
        self.tabWidget.removeTab(tabIndex)        
    
    def _initWorld(self):
        self.worldConfigObject = self.worldConfigEditor.createWorldConfigObject()

        self.world = mmlf.loadWorld(worldConfigObject=self.worldConfigObject,
                                    useGUI=True, 
                                    keepObservers=[self.updateViewersComboBox])
        
    def _configureMonitor(self):
        # Should not be configured before world is loaded
        if self.world is None:
            ret = QtGui.QMessageBox.warning(self, "Warning", 
                                            "Please initialize world first.")
            return
            
        from mmlf.gui.config_editor import ConfigEditorWindow, ListEditorWindow
        from mmlf.framework.monitor import Monitor
            
        # Allow user to configure monitor in GUI 
        def monitorConfiguredCallback(configDict):
            self.worldConfigObject['monitor'] = configDict
            self.worldConfigEditor.monitorConf = configDict
            
        # The non-standard config elements
        nonStandardConfigs = {}
        nonStandardConfigs["stateDims"] \
            = lambda initialValue, closeCallback, parent: \
                ListEditorWindow(self.world.environment.stateSpace.getDimensionNames(),
                                 initialValue, "stateDims", closeCallback,
                                 parent=self)
        nonStandardConfigs["actions"] \
            = lambda initialValue, closeCallback, parent: \
                ListEditorWindow(self.world.environment.actionSpace.getActionList(),
                                 initialValue, "actions", closeCallback,
                                 parent=self)

        observables = []
        for observable in OBSERVABLES.getAllObservablesOfType(FunctionOverStateSpaceObservable):
            observables.append("".join(observable.title.split(" ")[1:]).strip("()"))
        for observable in OBSERVABLES.getAllObservablesOfType(StateActionValuesObservable):
            observables.append("".join(observable.title.split(" ")[1:]).strip("()"))
        observables.append("All")
        nonStandardConfigs["plotObservables"] \
            = lambda initialValue, closeCallback, parent: \
                ListEditorWindow(observables, initialValue, "plotObservables", 
                                 closeCallback, parent=self)
                
        configEditorWindow = \
            ConfigEditorWindow(self.worldConfigObject['monitor'],
                               title = "Monitor",
                               infoString = Monitor.__doc__,
                               closeCallback = monitorConfiguredCallback,
                               nonStandardConfigs=nonStandardConfigs,
                               parent=self)
        configEditorWindow.show()
           
    def _startWorld(self):                   
        # Start the world
        mmlf.log.debug("Starting world...")
        # Run experiment in a separate thread to keep GUI responsive
        def secureWorldRunner():
            try:
                self.world.run(self.worldConfigObject['monitor'])
            except Exception, e:
                errorMessage = e.__class__.__name__ + ": " + str(e)
                self.parent.exceptionOccurredSignal.emit(errorMessage)
                raise
        self.mainThread = Thread(target=lambda : secureWorldRunner(), args=()) 
        self.mainThread.start()
        mmlf.log.debug("Starting world...Done!")
        
    def _executeSteps(self):                
        self.world.executeSteps(n=1, monitorConf=self.worldConfigObject['monitor'])

    def _executeEpisode(self):                
        self.world.executeEpisode(self.worldConfigObject['monitor'])
        
    def _stopWorld(self):
        # Stop the world
        mmlf.log.debug("Stopping world...")
        self.world.stop()
        if hasattr(self, "mainThread"):
            self.mainThread.join()
        mmlf.log.debug("Stopping world... Done!")
        
    
        
        