#!/usr/bin/env python

import sys
from PyQt4 import QtCore, QtGui

from qIsing_ui import Ui_MainWindow
import threading
from Ising import Ising
from numpy import zeros, int8, mean, std, arange, array
from re import split
from time import  time

import matplotlib
matplotlib.use('QTAgg')
from matplotlib.figure import Figure
import matplotlib.patches as patches
import matplotlib.transforms as transforms
from matplotlib.backends.backend_qt4agg import \
    FigureCanvasQTAgg as FigureCanvas, \
    NavigationToolbar2QTAgg as NavigationToolbar

class CGCEIsing(Ising):
    def __init__(self):
        Ising.__init__(self)#must use 'self'
        self.RefreshSamp = 100
        self.Stride = 1
        self.Using_wolff = False
    def Reset(self, dim0, dim1):
        self.InitParameters()
        self.conf = zeros((dim0, dim1), int8)
        self.SetConf(self.conf, dim0, dim1)
        self.E = self.PyGetEnergyRange()#numpy array E(n)
        self.H = zeros(len(self.E), int) #for self.model.PyTraj2Hist(ydata, self.model.H)
        self.MH = zeros((self.m_uN + 1, 1), int) #for self.model.PyTraj2Hist(ydata, self.model.H)
        self.ETR = []#for energy
        self.MTR = []#for magnetism
        self.Stack_p, self.Seq_p = self.PySetGEWolff()
    def ResetWolff(self):
        self.m_dGCEWFavgE = self.m_curHami
        self.m_dGCEWFsegAccumE = 0
    def SetGCE(self, beta, alpha, un):
        self.m_dBeta = beta
        self.m_dAlpha = alpha
        self.m_dUn = un
    def RunGCE(self):
        if self.Using_wolff:
            for CurSample in range(self.RefreshSamp):
                self.WolffClusterGCE(self.Stride) #C++ extension Function from Ising in pymcsim model
                self.ETR.append(self.m_curHami)
                self.MTR.append(self.m_curMag)
        else:
            Stride = self.Stride * self.m_uN
            for CurSample in range(self.RefreshSamp):
                self.MetroplisTrialGCE(Stride) #C++ extension Function from Ising in pymcsim model
                self.ETR.append(self.m_curHami)
                self.MTR.append(self.m_curMag)
                self.Gauge()
                
class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
    def __init__(self, parent=None, statusbar=None, width=8.0, height=3.5, dpi=100, bgcolor=None):
        self.parent = parent
        self.statusbar = statusbar
        self.fig = Figure((width, height), dpi=dpi)
        self.axes_left = self.fig.add_subplot(121)
        self.axes_right = self.fig.add_subplot(122)
        self.axes_left.set_axis_bgcolor('gray')
        self.axes_right.set_axis_bgcolor('gray')
        self.fig.subplots_adjust(bottom=0.14, left=0.11, right=0.96)
        FigureCanvas.__init__(self, self.fig)
        #if self.parent:
        #    bgc = parent.backgroundBrush().color()
        #    bgcolor = float(bgc.red()) / 255.0, float(bgc.green()) / 255.0, float(bgc.blue()) / 255.0
        #bgcolor = "#%02X%02X%02X" % (bgc.red(), bgc.green(), bgc.blue())

        self.fig = Figure(figsize=(width, height), dpi=dpi, facecolor=bgcolor, edgecolor=bgcolor)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.job = None
        self.ploting = False
        self.keeping = False
        self.LeftPlot = 'ETraj'
        self.range = None
        self.reset = False
        self.starting_time = time()
        self.timer = QtCore.QTimer(self)
        QtCore.QObject.connect(self.timer, QtCore.SIGNAL("timeout()"), self.on_redraw_timer)
        self.timer.start(400)
        
        self.model = CGCEIsing()
        self.model.Reset(20, 20)
    def sizeHint(self):
        w = self.fig.get_figwidth()
        h = self.fig.get_figheight()
        return QtCore.QSize(w, h)
    def on_reset(self, l1l2, bau, iconf):
        self.model.Reset(int(l1l2[0]), int(l1l2[1]))
        self.model.InitConf(iconf)
        self.model.Gauge()
        self.model.SetGCE(float(bau[0]), float(bau[1]), float(bau[2]))

        self.axes_left.clear()
        self.axes_left.text(0.1, 0.85, "Generalized canonical ensemble", color="blue", size=12, transform=self.axes_left.transAxes)
        self.axes_left.text(0.1, 0.6, "$Z=\sum_E g(E) e ^{-\\beta E-\\alpha(E-U)^2/(2N)}$", color="red", size=14, transform=self.axes_left.transAxes)
        self.axes_left.text(0.1, 0.4, "Ising model $H=-\sum_{<i,j>} s_i \cdot s_j$", color="red", size=14, transform=self.axes_left.transAxes)
        self.axes_left.set_axis_bgcolor('black')
        # for configuration plotting
        self.axes_right.clear()
        self.axes_right.set_title(r'Ising Model $N=%d\times%d$, $bright=\downarrow$, $green=\uparrow$' % (self.model.m_uDim0, self.model.m_uDim1), size=10)
        self.axes_right.set_xlabel('L2', fontsize=9)
        self.axes_right.set_ylabel('L1', fontsize=9)
        self.axes_right.grid(False)# interpolation='nearest', animated=True,matplotlib.cm.YlGn
        self.im = self.axes_right.imshow(self.model.conf, cmap=matplotlib.cm.BuGn, interpolation='nearest', origin='lower', animated=True)

        self.draw()
        self.reset = True;
        
    def on_redraw_timer(self):
        if self.ploting:
            return
        if not self.keeping:
            return
        if  self.job == None:
            self.job = threading.Thread(target=self.model.RunGCE)# args=(self.model, self.u)
            self.job.start()
        else:
            if not self.job.isAlive():
                self.ploting = True
                self.draw_figure()
                self.statusbar.showMessage("%lg seconds" % (time() - self.starting_time))
                self.job = threading.Thread(target=self.model.RunGCE)
                self.job.start()
                self.ploting = False

    def draw_figure(self):
        """ Redraws the figure
        """
        self.axes_left.clear()
        #self.axes_left.lines.remove(self.axes_left_line)
        self.axes_left.set_title(r'GCE %s: $\beta(E)=\beta+\alpha(E-U)/N$' % ("Wolff" if self.model.Using_wolff else ""), size=10)
        self.axes_left.grid(True, color='gray')
        self.axes_left.set_axis_bgcolor('black')

        if self.LeftPlot == 'ETraj':
            if not self.get_data(self.model.ETR):
                return
            self.axes_left.set_xlabel('Samples', fontsize=9)
            self.axes_left.set_ylabel('Energy', fontsize=9)
            self.axes_left.plot(self.tdata, array(self.ydata) / float(self.model.m_uN))

        elif self.LeftPlot == 'EHist':
            if not self.get_data(self.model.ETR):
                return
            self.axes_left.set_xlabel('Energy', fontsize=9)
            self.axes_left.set_ylabel('Histogram', fontsize=9)
            e0, e1, Erange = self.model.PyETraj2Hist(self.ydata, self.model.H)
            self.axes_left.plot(arange(e0 / 4, e1 / 4 + 1) * 4 / float(self.model.m_uN), Erange[(e0 + 2 * self.model.m_uN) / 4:(e1 + 2 * self.model.m_uN) / 4 + 1], '.', markersize=3)
        elif self.LeftPlot == 'MTraj':
            if not self.get_data(self.model.MTR):
                return
            self.axes_left.set_xlabel('Samples', fontsize=9)
            self.axes_left.set_ylabel('Magnetism', fontsize=9)
            self.axes_left.plot(self.tdata, self.ydata, 'g-')
        elif self.LeftPlot == 'MHist':
            if not self.get_data(self.model.MTR):
                return
            self.axes_left.set_xlabel('Magnetism', fontsize=9)
            self.axes_left.set_ylabel('Histogram', fontsize=9)
            m0, m1, Hrange = self.model.PyMTraj2Hist(self.ydata, self.model.MH)
            m0i = (m0 + self.model.m_uN) / 2
            m1i = (m1 + self.model.m_uN) / 2
            self.axes_left.plot(arange(m0 , m1 + 2, 2) , Hrange[m0i:m1i + 1 ], 'g.', markersize=2)

        for label in self.axes_left.xaxis.get_ticklabels():
            # label is a Text instance
            #label.set_color('red')
            label.set_rotation(20)
            label.set_fontsize(9)

        #plotting configuration

        if self.model.m_initConf == -1:#YlGn
            self.axes_right.imshow(self.model.conf, cmap=matplotlib.cm.BuGn, interpolation='nearest', origin='lower', animated=True)
        else:
            self.im.set_array(self.model.conf) #not suitable for ground state

        self.draw()        
    def get_data(self, TR):
        if len(self.range) == 1:
            return False
        try:
            f = int(self.range[0])
        except:
            self.statusbar.showMessage("Unknown range:" + ":".join(self.range))
            return False

        if self.range[1] == '':
            self.ydata = TR[f:]
            self.tdata = range(len(TR) - len(self.ydata), len(TR));
        else:
            try:
                to = int(self.range[1])
            except:
                self.statusbar.showMessage("Unknown range:" + ":".join(self.range))
                return False

            self.ydata = TR[f:to]
            x0 = len(TR) - len(self.ydata) if f < 0 else f
            self.tdata = range(x0, x0 + len(self.ydata))
        if len(self.ydata) == 0:
            return False
        return True
    
    def save_traj(self):
        if self.keeping:
            QtGui.QMessageBox.warning(self, "Error", "Stop runing first!")
            return
        if not self.reset:
            QtGui.QMessageBox.warning(self, "Error", "No resetting!")
            return

        file_choices = "traj (*.txt)|*.txt"
        if self.model.Using_wolff:
            trajfile = "gcewfi%d_%d~%d~%.15lg_%.15lg_%.15lg_%ld_%ldTraj.txt" % (self.model.m_uDim0, self.model.m_uDim1, self.model.m_initConf, \
            self.model.m_dBeta, self.model.m_dAlpha, self.model.m_dUn, \
            self.model.Stride, self.model.RefreshSamp);
        else:
            trajfile = "gce%d_%d~%d~%.15lg_%.15lg_%.15lg_%ld_%ldTraj.txt" % (self.model.m_uDim0, self.model.m_uDim1, self.model.m_initConf, \
            self.model.m_dBeta, self.model.m_dAlpha, self.model.m_dUn, \
            self.model.Stride, self.model.RefreshSamp);

        trajfile = QtGui.QFileDialog.getOpenFileName(self, 'Open file', '.')
        if trajfile != '':
            f = open(trajfile, 'w')
            if f:
                for item in self.model.ETR:
                    f.write(str(item) + "\n")
                self.statusbar.showMessage('Trajectory Saved to %s' % trajfile)
            
    
class MyMainWindow(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.myCanvas = MyMplCanvas(self.centralwidget, self.statusbar)

        self.mpl_toolbar = NavigationToolbar(self.myCanvas, self.centralwidget)
        self.MyGUI()
        # Other GUI controls
        # 
    def MyGUI(self):
        
        self.connect(self.actionSave_Trajectory, QtCore.SIGNAL('triggered()'), self.myCanvas.save_traj)
        self.connect(self.actionQuit, QtCore.SIGNAL('triggered()'), QtGui.qApp, QtCore.SLOT('quit()'))
        self.connect(self.actionAbout, QtCore.SIGNAL('triggered()'), self.on_about)
        
        self.l1l2 = QtGui.QLabel('L1,L2')
        self.l1l2_textbox = QtGui.QLineEdit()
        self.l1l2_textbox.setText('96,96')
        
        self.bau = QtGui.QLabel('beta,alpha,U/n')
        self.bau_textbox = QtGui.QLineEdit()
        self.bau_textbox.setText('0.431, 1, -1.5')

        self.initconf_type = QtGui.QLabel('InitConf')
        self.initconf_type_cb = QtGui.QComboBox()
        self.initconf_type_cb.addItem("Random")
        self.initconf_type_cb.addItem("Antiground")
        self.initconf_type_cb.addItem("Ground")

      
        self.reset_button = QtGui.QPushButton("&Reset")
        self.connect(self.reset_button, QtCore.SIGNAL('clicked()'), self.on_reset)
        
        self.start_button = QtGui.QPushButton("&Start")
        self.connect(self.start_button, QtCore.SIGNAL('clicked()'), self.on_start)
          
        
        self.lfplot_type_cb = QtGui.QComboBox()
        self.lfplot_type_cb.addItem("ETraj")
        self.lfplot_type_cb.addItem("EHist")
        self.lfplot_type_cb.addItem("MTraj")
        self.lfplot_type_cb.addItem("MHist")
        self.connect(self.lfplot_type_cb, QtCore.SIGNAL('activated(QString)'), self.on_lfplot_type)
        
        self.traj_range = QtGui.QLabel('Traj. Range')
        self.traj_range_textbox = QtGui.QLineEdit()    
        self.traj_range_textbox.setText('10:')    
        self.connect(self.traj_range_textbox, QtCore.SIGNAL('textChanged(QString)'), self.on_range)
        
        self.wolff_cluster_cb = QtGui.QCheckBox("Wolff &Cluster")
        self.wolff_cluster_cb.setChecked(False)
        self.connect(self.wolff_cluster_cb, QtCore.SIGNAL('stateChanged(int)'), self.on_check_wolff)
        self.wolff_avelen = QtGui.QLabel('AVE.length')
        self.wolff_avelen_textbox = QtGui.QLineEdit()    
        self.wolff_avelen_textbox.setText('20')  
        self.wolff_avelen_textbox.setEnabled(False)
        self.connect(self.wolff_avelen_textbox, QtCore.SIGNAL('textChanged(QString)'), self.on_wolff_Eavg)
        
        #
        # Layout with box sizers
        # 
        gbox = QtGui.QGridLayout()
        ctrs = [ self.l1l2, self.l1l2_textbox, self.bau, self.bau_textbox, self.initconf_type, self.initconf_type_cb, self.reset_button, self.traj_range, self.traj_range_textbox, self.lfplot_type_cb, self.wolff_cluster_cb, self.wolff_avelen, self.wolff_avelen_textbox, self.start_button]
        for i in range(2):
            for j in range(7):
                n = i * 7 + j
                if n >= len(ctrs):break
                gbox.addWidget(ctrs[n], i, j)
                #hbox.setAlignment(w, QtCore.Qt.AlignVCenter)
        
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.myCanvas)
        vbox.addWidget(self.mpl_toolbar)
        vbox.addLayout(gbox)
        
        self.centralwidget.setLayout(vbox)     
    def on_start(self):
        if not self.myCanvas.keeping:
            self.myCanvas.keeping = True;
            label = "Pause"
            self.l1l2_textbox.setEnabled(False)
            self.bau_textbox.setEnabled(False)    
            self.initconf_type_cb.setEnabled(False)        
            self.reset_button.setEnabled(False)
            self.myCanvas.starting_time = time()#clock() takes negative when it lasts long
        else:
            self.myCanvas.keeping = False;
            label = "Start"
            self.bau_textbox.setEnabled(True)      
            self.reset_button.setEnabled(True)
            self.initconf_type_cb.setEnabled(True)        
            self.l1l2_textbox.setEnabled(True)

        self.start_button.setText(label)

    def on_reset(self):
        str = unicode(self.l1l2_textbox.text())
        if str == '':return
        l1l2 = map(int, split('[,;]?', str))
        self.myCanvas.range = split('[,;:]?', unicode(self.traj_range_textbox.text()))
        str = unicode(self.bau_textbox.text())
        if str == '':return
        bau = map(float, split('[,;]?', str))
        iconf = self.initconf_type_cb.currentIndex()
        if iconf == 2:iconf = -1
        return self.myCanvas.on_reset(l1l2, bau, iconf)
    def on_range(self, range):
        self.myCanvas.range = split('[,;:]?', unicode(range))
        
    def on_check_wolff(self, isChecked):
        self.myCanvas.model.Using_wolff = isChecked
        self.wolff_avelen_textbox.setEnabled(isChecked)
        if isChecked:
            self.on_wolff_Eavg(self.wolff_avelen_textbox.text())
            self.myCanvas.model.ResetWolff()
    def on_wolff_Eavg(self, avg):
        try:
            f = int(avg)
        except:
            self.statusbar.showMessage("Unknown wolff_Eavg:%s" % avg)
            return
        if f < 2:
            self.statusbar.showMessage("Too small value %d" % f + " and reset to 2")
            f = 2
            return
        self.myCanvas.model.m_GCEWFavgC = f;
          
    def on_lfplot_type(self, text):
        self.myCanvas.LeftPlot = unicode(text)
            
    def _create_action(self, text, slot=None, shortcut=None,
                        icon=None, tip=None, checkable=False,
                        signal="triggered()"):
        action = QtGui.QAction(text, self)
        if icon is not None:
            action.setIcon(QtGui.QIcon(":/%s.png" % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action
    def on_about(self):
        msg = """Statistical model simulator based on PyQt with matplotlib and cpp swig wrapper:

         * Junior Research Group of Multiscale modeling
         * Asia Pacific Center for Theoretical Physics
         * Shun Xu (alwintsui@gmal.com)
         * Xin Zhou (xinzhou71@gmail.com)
         * 2011, Jan 3
        """
        QtGui.QMessageBox.about(self, "About", msg.strip())
        
def main():
    app = QtGui.QApplication(sys.argv)
    myapp = MyMainWindow()
    myapp.show()
    sys.exit(app.exec_())
    
if __name__ == "__main__":
    main()
