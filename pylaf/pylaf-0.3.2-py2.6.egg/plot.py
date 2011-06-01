# coding: utf-8
import gc, Tkinter, tkFileDialog, matplotlib, mpl
from Tkinter import Frame
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
matplotlib.rcParams['figure.facecolor'] = 'white'
matplotlib.rcParams['figure.edgecolor'] = 'white'
matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['font.size']   = 9.0

class MPLFrame(Frame):
    '''
    軽量プロットウィジェット
    tkaggバックエンドでのメモリ解放に関する不具合を修正したプロッタ
    '''
    def __init__(self,master,figsize=(5,4),dpi=75):
        Frame.__init__(self,master)
        self.figure = figure = Figure(figsize=figsize,dpi=dpi)
        self.canvas = canvas = FigureCanvasTkAgg(figure,master=self)
        canvas.get_tk_widget().pack()
        self.ax = None
    def destroy_figure_canvas_axes(self):
        # === Axesオブジェクト廃棄の準備
        self.figure.clf()
        self.ax = None
        # === Figureオブジェクト廃棄の準備
        self.canvas.figure = None
        self.figure = None
        # === Canvasオブジェクトの廃棄
        self.canvas._tkcanvas.destroy()
        self.canvas._tkcanvas = None # 解放を確認
        # === disconnect callbacks
        for cid in range(self.canvas.callbacks._cid):
            self.canvas.mpl_disconnect(cid+1)
        # === free MouseEvent
        matplotlib.backend_bases.LocationEvent.lastevent = None
        self.canvas = None
        # === 循環参照の回収
        gc.collect()
    def destroy(self):
        self.destroy_figure_canvas_axes()
        Frame.destroy(self)

from scipy import array
from Tkinter import Toplevel, BOTTOM
from framework import PortHolder, Port, BooleanVar, DoubleVar, StringVar, IntVar
from widgets import Menu, GridPane
class BasePlot(MPLFrame,PortHolder):
    def destroy(self):
        self.canvas.mpl_disconnect(self.cid)
        PortHolder.destroy(self)
        MPLFrame.destroy(self)
    def __init__(self,master=None,cnf={},**kw):
        MPLFrame.__init__(self,master,**kw)
        # メニューポップアップイベント
        self.cid = self.canvas.mpl_connect('button_press_event',self._rclicked)
    def _rclicked(self,e):
        if e.button == 3:
            canvas = self.canvas.get_tk_widget()
            x = canvas.winfo_rootx() + int(e.x)
            y = canvas.winfo_rooty() + self.canvas.get_width_height()[1] - int(e.y)
            self.menu(self).tk_popup(x, y)
    def _savefig(self):
        fname = tkFileDialog.asksaveasfilename(title='Enter Filename')
        self.ax.figure.savefig(fname)
    def _load(self):
        from numpy import genfromtxt
        fname = tkFileDialog.askopenfilename(title='Enter Filename')
        data = genfromtxt(fname,delimiter=',').transpose()
        self.sig_in.set(data)
    def gui(self,master,cnf={},**kw): o = self.console(master); o.pack(side=BOTTOM); return self
    def console(self,master): o = GridPane(master); return o
    def decoration(self,master): o = GridPane(master); return o
    def menu(self,master,cnf={},**kw):
        menu = Menu(master,cnf,**kw)
        menu.add_command(label="Load",command=self._load)
        menu.add_command(label="Save Figure",command=self._savefig)
        menu.add_command(label="Popup Console",command=lambda:self.console(Toplevel(self)).pack())
        menu.add_command(label="Popup Decolation",command=lambda:self.decoration(Toplevel(self)).pack())
        return menu

class Plot(BasePlot):
    '''
    プロットの基本機能を提供する。オートスケール、書き出し、デコレーションなど。
    '''
    def destroy(self):
        self.ax.callbacks.disconnect(self.cid_ylim)
        self.ax.callbacks.disconnect(self.cid_xlim)
        BasePlot.destroy(self)
    def __init__(self,master=None,cnf={},**kw):
        BasePlot.__init__(self,master,**kw)
        self._passed_update_xlim  = False
        self._passed_update_ylim  = False
        self._passed_changed_xylim = False
        self.ax = self.figure.add_subplot(111,projection='rectilinear')
        self.sig_in = Port(array([])).bind(self._sig_in)
        self.left   = Port(0.15)
        self.right  = Port(0.9)
        self.bottom = Port(0.1)
        update_adjust = lambda:self.ax.figure.subplots_adjust(left=self.left.get(),right=self.right.get(),bottom=self.bottom.get())
        self.left.bind(update_adjust).bind(self.canvas.show)
        self.right.bind(update_adjust).bind(self.canvas.show)
        self.bottom.bind(update_adjust).bind(self.canvas.show)
        self.title  = Port('').bind(lambda:self.ax.set_title(self.title.get())).bind(self.canvas.show)
        self.xlabel = Port('xlabel').bind(lambda:self.ax.set_xlabel(self.xlabel.get())).bind(self.canvas.show)
        self.ylabel = Port('ylabel').bind(lambda:self.ax.set_ylabel(self.ylabel.get())).bind(self.canvas.show)
        xlim        = self.ax.get_xlim()
        self.xmin   = Port(xlim[0]).bind(self._changed_xlim)
        self.xmax   = Port(xlim[1]).bind(self._changed_xlim)
        ylim        = self.ax.get_ylim()
        self.ymin   = Port(ylim[0]).bind(self._changed_ylim)
        self.ymax   = Port(ylim[1]).bind(self._changed_ylim)
        self.autoscalex = Port(True).bind(self._changed_autoscale)
        self.autoscaley = Port(True).bind(self._changed_autoscale)
        self.style      = Port('-').bind(self._sig_in)
        # グラフ装飾パラメータの適用
        self.left.set(self.left.get())
        self.right.set(self.right.get())
        self.bottom.set(self.bottom.get())
        self.title.set(self.title.get())
        self.xlabel.set(self.xlabel.get())
        self.ylabel.set(self.ylabel.get())
        # プロット範囲更新イベント
        self.cid_xlim = self.ax.callbacks.connect('xlim_changed',self._update_xlim)
        self.cid_ylim = self.ax.callbacks.connect('ylim_changed',self._update_ylim)
    def resize(self,figsize=(5,4),dpi=75):
        self.destroy_figure_canvas_axes()
        self.figure = figure = Figure(figsize=figsize,dpi=dpi)
        self.canvas = canvas = FigureCanvasTkAgg(figure,master=self)
        self.cid = self.canvas.mpl_connect('button_press_event',self._rclicked)
        canvas.get_tk_widget().pack()
        self.ax = self.figure.add_subplot(111,projection='rectilinear')
    def clear_line(self):
        while len(self.ax.lines): # lineを削除する
            line = self.ax.lines[-1]
            self.ax.lines.remove(line)
            line._lineFunc = None # Line2Dの循環参照を解放する
            for key,item in self.ax.xaxis.callbacks.callbacks['units'].items(): # コールバックを解除する
                if item == line.recache:
                    del self.ax.xaxis.callbacks.callbacks['units'][key]
            for key,item in self.ax.yaxis.callbacks.callbacks['units'].items(): # コールバックを解除する
                if item == line.recache:
                    del self.ax.yaxis.callbacks.callbacks['units'][key]
        self.ax.ignore_existing_data_limits = True # dataLimをアップデートする
        self.ax._get_lines._clear_color_cycle() # カラーサイクルを初期状態に戻す
    def clear_patch(self):
        while len(self.ax.patches): # きちんとパッチが解放されることを確認した
            patch = self.ax.patches[-1]
            self.ax.patches.remove(patch)
    def clear(self,line=True,patch=False):
        if line: self.clear_line()
        if patch: self.clear_patch()
    def _sig_in(self):
        self.clear()
        self.ax.plot(self.sig_in.get().transpose(),self.style.get())
        self.canvas.show()
        self.master.update()
    def _changed_xlim(self):
        if self._passed_update_xlim: return
        self._passed_changed_xylim = True
        self.autoscalex.set(False)
        self._passed_changed_xylim = False
        self.ax.set_xlim(self.xmin.get(), self.xmax.get())
        self.canvas.show()
    def _changed_ylim(self):
        if self._passed_update_ylim: return
        self._passed_changed_xylim = True
        self.autoscaley.set(False)
        self._passed_changed_xylim = False
        self.ax.set_ylim(self.ymin.get(), self.ymax.get())
        self.canvas.show()
    def _changed_autoscale(self):
        self.ax.set_autoscalex_on(self.autoscalex.get())
        self.ax.set_autoscaley_on(self.autoscaley.get())
        if not self._passed_changed_xylim: self._sig_in()
    def _update_xlim(self,e):
        self._passed_update_xlim = True
        xlim = self.ax.get_xlim()
        self.xmin.set(xlim[0]); self.xmax.set(xlim[1])
        self._passed_update_xlim = False
    def _update_ylim(self,e):
        self._passed_update_ylim = True
        ylim = self.ax.get_ylim()
        self.ymin.set(ylim[0]); self.ymax.set(ylim[1])
        self._passed_update_ylim = False
    def console(self,master):
        o = GridPane(master)
        o.entry_with_tcb('XLIM',BooleanVar(self.autoscalex),DoubleVar(self.xmin),DoubleVar(self.xmax))
        o.entry_with_tcb('YLIM',BooleanVar(self.autoscaley),DoubleVar(self.ymin),DoubleVar(self.ymax))
        o.entry('Plot Style',StringVar(self.style))
        return o
    def decoration(self,master):
        o = GridPane(master)
        o.entry('PADL',DoubleVar(self.left))
        o.entry('PADR',DoubleVar(self.right))
        o.entry('PADB',DoubleVar(self.bottom))
        o.entry('TITLE',StringVar(self.title))
        o.entry('XLABEL',StringVar(self.xlabel))
        o.entry('YLABEL',StringVar(self.ylabel))
        return o

class Smith(BasePlot):
    '''
    プロットの基本機能を提供する。オートスケール、書き出し、デコレーションなど。
    '''
    def destroy(self):
        #self.ax.callbacks.disconnect(self.cid_ylim)
        #self.ax.callbacks.disconnect(self.cid_xlim)
        BasePlot.destroy(self)
    def __init__(self,master=None,cnf={},**kw):
        BasePlot.__init__(self,master,**kw)
        self._passed_update_xlim  = False
        self._passed_update_ylim  = False
        self._passed_changed_xylim = False
        self.ax = self.figure.add_subplot(111,projection='smith')
        self.sig_in = Port(array([])).bind(self._sig_in)
        self.left   = Port(0.15)
        self.right  = Port(0.9)
        self.bottom = Port(0.1)
        update_adjust = lambda:self.ax.figure.subplots_adjust(left=self.left.get(),right=self.right.get(),bottom=self.bottom.get())
        self.left.bind(update_adjust).bind(self.canvas.show)
        self.right.bind(update_adjust).bind(self.canvas.show)
        self.bottom.bind(update_adjust).bind(self.canvas.show)
        self.title  = Port('').bind(lambda:self.ax.set_title(self.title.get())).bind(self.canvas.show)
        self.style      = Port('-').bind(self._sig_in)
        # グラフ装飾パラメータの適用
        self.left.set(self.left.get())
        self.right.set(self.right.get())
        self.bottom.set(self.bottom.get())
        self.title.set(self.title.get())
    def resize(self,figsize=(5,4),dpi=75):
        self.destroy_figure_canvas_axes()
        self.figure = figure = Figure(figsize=figsize,dpi=dpi)
        self.canvas = canvas = FigureCanvasTkAgg(figure,master=self)
        self.cid = self.canvas.mpl_connect('button_press_event',self._rclicked)
        canvas.get_tk_widget().pack()
        self.ax = self.figure.add_subplot(111,projection='smith')
    def clear_line(self):
        while len(self.ax.lines): # lineを削除する
            line = self.ax.lines[-1]
            self.ax.lines.remove(line)
            line._lineFunc = None # Line2Dの循環参照を解放する
            for key,item in self.ax.xaxis.callbacks.callbacks['units'].items(): # コールバックを解除する
                if item == line.recache:
                    del self.ax.xaxis.callbacks.callbacks['units'][key]
            for key,item in self.ax.yaxis.callbacks.callbacks['units'].items(): # コールバックを解除する
                if item == line.recache:
                    del self.ax.yaxis.callbacks.callbacks['units'][key]
        self.ax.ignore_existing_data_limits = True # dataLimをアップデートする
        self.ax._get_lines._clear_color_cycle() # カラーサイクルを初期状態に戻す
    def clear_patch(self):
        while len(self.ax.patches): # きちんとパッチが解放されることを確認した
            patch = self.ax.patches[-1]
            self.ax.patches.remove(patch)
    def _sig_in(self):
        self.ax.cla()
        sig = self.sig_in.get().transpose()
        self.ax.plot(real(sig),imag(sig),self.style.get())
        self.canvas.show()
        self.master.update()
    def _changed_xlim(self):
        if self._passed_update_xlim: return
        self._passed_changed_xylim = True
        self.autoscalex.set(False)
        self._passed_changed_xylim = False
        self.ax.set_xlim(self.xmin.get(), self.xmax.get())
        self.canvas.show()
    def _changed_ylim(self):
        if self._passed_update_ylim: return
        self._passed_changed_xylim = True
        self.autoscaley.set(False)
        self._passed_changed_xylim = False
        self.ax.set_ylim(self.ymin.get(), self.ymax.get())
        self.canvas.show()
    def _changed_autoscale(self):
        self.ax.set_autoscalex_on(self.autoscalex.get())
        self.ax.set_autoscaley_on(self.autoscaley.get())
        if not self._passed_changed_xylim: self._sig_in()
    def _update_xlim(self,e):
        self._passed_update_xlim = True
        xlim = self.ax.get_xlim()
        self.xmin.set(xlim[0]); self.xmax.set(xlim[1])
        self._passed_update_xlim = False
    def _update_ylim(self,e):
        self._passed_update_ylim = True
        ylim = self.ax.get_ylim()
        self.ymin.set(ylim[0]); self.ymax.set(ylim[1])
        self._passed_update_ylim = False
    def console(self,master):
        o = GridPane(master)
        o.entry('Plot Style',StringVar(self.style))
        return o
    def decoration(self,master):
        o = GridPane(master)
        o.entry('PADL',DoubleVar(self.left))
        o.entry('PADR',DoubleVar(self.right))
        o.entry('PADB',DoubleVar(self.bottom))
        o.entry('TITLE',StringVar(self.title))
        return o
    
from mpl_toolkits.mplot3d import Axes3D
class Plot3D(BasePlot):
    '''
    プロットの基本機能を提供する。オートスケール、書き出し、デコレーションなど。
    '''
    def __init__(self,master=None,cnf={},**kw):
        BasePlot.__init__(self,master,**kw)
        self.ax = Axes3D(self.figure)
        self.ax.mouse_init()
        self.sig_in = Port(array([])).bind(self._sig_in)
    def clear(self):
        self.ax.clear()
    def _sig_in(self):
        sig = self.sig_in.get()
        try:
            x, y, z = sig[0,:], sig[1,:], sig[2,:]
        except IndexError:
            return
        i = (x + 1j * y) / 50.
        g = (i - 1.) / (i + 1.)
        self.clear()
        self.ax.scatter(real(g),imag(g),z)
        self.canvas.show()
        self.master.update()

from scipy import real, imag
class Constellation(Plot):
    '''
    デシメーションなどの機能を多重継承して追加できるといいけどね。
    '''
    def __init__(self,master=None,cnf={},**kw):
        if not kw.has_key('figsize'): kw['figsize'] = (4,4)
        Plot.__init__(self,master,cnf,**kw)
        self.samplerate = Port(1.).bind(self._sig_in)
        self.alpha      = Port(1.).bind(self._sig_in)
        self.begin      = Port(0.).bind(self._sig_in) # プロット開始（％）
        self.end        = Port(100.).bind(self._sig_in) # プロット終了（％）
        self.decimation = Port(1).bind(self._sig_in)
        self.xlabel.set('I Channel [mV]')
        self.ylabel.set('Q Channel [mV]')
        self.style.set('.')
    def _sig_in(self):
        sig = self.sig_in.get()
        b,e = self.begin.get(), self.end.get()
        sig = sig[...,::self.decimation.get()]
        sig = sig[...,(b / 100 * sig.shape[-1]):(e / 100 * sig.shape[-1])]
        sig = sig.transpose()
        self.clear()
        self.ax.plot(real(sig), imag(sig), self.style.get(), alpha=self.alpha.get())
        self.canvas.show()
        self.master.update()
    def console(self,master):
        o = Plot.console(self,master)
        o.entry('Sample Rate [MS/sec]',DoubleVar(self.samplerate))
        o.entry('Alpha Index',DoubleVar(self.alpha))
        o.entry('Decimation Index',IntVar(self.decimation))
        return o

class XYPlot(Plot):
    def __init__(self,master=None,cnf={},**kw):
        Plot.__init__(self,master,cnf,**kw)
        self.xaxis = Port(array([])).bind(self._sig_in)
        self.yaxis = Port(array([])).bind(self._sig_in)
        self.xlabel.set('X Axis')
        self.ylabel.set('Y Axis')
    def _sig_in(self):
        xaxis, yaxis, style = self.xaxis.get(), self.yaxis.get(), self.style.get()
        if xaxis.shape[-1] == yaxis.shape[-1]:
            self.clear()
            self.ax.plot(xaxis, yaxis, style)
            self.canvas.show()
            self.master.update()

from scipy import arange
class Oscilloscope(Plot):
    def __init__(self,master=None,cnf={},**kw):
        Plot.__init__(self,master,cnf,**kw)
        self.samplerate = Port(1.).bind(self._sig_in)
        self.decimation = Port(1).bind(self._sig_in)
        self.xlabel.set('Time [us]')
        self.ylabel.set('Signal [mV]')
    def _sig_in(self):
        sig = self.sig_in.get()
        sig = sig[...,::self.decimation.get()]
        samplerate = self.samplerate.get() / self.decimation.get()
        time  = 1. / samplerate * arange(sig.shape[-1])
        self.clear()
        self.ax.plot(time,sig.transpose(),self.style.get())
        self.canvas.show()
        self.master.update()
    def console(self,master):
        o = Plot.console(self,master)
        o.entry('Sample Rate [MS/sec]',DoubleVar(self.samplerate))
        o.entry('Decimation Index',IntVar(self.decimation))
        return o

from scipy import fft, fftpack, log10
class Spectrum(Plot):
    def __init__(self,master=None,cnf={},**kw):
        Plot.__init__(self,master,cnf,**kw)
        self.samplerate   = Port(1.).bind(self._sig_in)
        self.decimation   = Port(1).bind(self._sig_in)
        self.xlabel.set('Frequency [MHz]')
        self.ylabel.set('Power [dBm]')
    def _sig_in(self):
        sig = self.sig_in.get()
        if len(sig.shape) == 1: sig = sig.reshape(1,len(sig))
        samplerate = self.samplerate.get() / self.decimation.get()
        sig = sig[...,::self.decimation.get()]
        # sig  = sig[:2**int(log2(sig.size))]
        try:
            f   = fft(sig)
            # f[0] = f[0] * .5 # 片側スペクトルを見たい場合にはこの行をアクティベート
            v   = fftpack.fftshift(f * 2.0 / sig.shape[-1])
            freq = fftpack.fftshift(fftpack.fftfreq(sig.shape[-1],1./samplerate))
            value = 10 * log10(real(v*v.conj())/2/50) - 30
            self.clear()
            for v in value: self.ax.plot(freq, v, self.style.get())
            self.canvas.show()
            self.master.update()
        except ValueError:
            self.clear()
            self.ax.plot()
            self.canvas.show()
            self.master.update()
            from warnings import warn
            warn('ValueError has occur.')
    def console(self,master):
        o = Plot.console(self,master)
        o.entry('Sample Rate [MS/sec]',DoubleVar(self.samplerate))
        o.entry('Decimation Index',IntVar(self.decimation))
        return o

if __name__ == '__main__':
    master = None
    from scipy import sin, pi, rand
    from framework import App
    o = App(master,Spectrum); o.pack()
    osc = App(Toplevel(master),Oscilloscope); osc.pack()
    sms = App(Toplevel(master),Smith); sms.pack()
    sms.sig_in.set(rand(1000)+1j*rand(1000))
    o.sig_in.link(osc.sig_in)
    o.samplerate.link(osc.samplerate)
    o.samplerate.set(250.)
    osc.xmin.set(0)
    osc.xmax.set(1000)
    d = 1. / o.samplerate.get()
    t = arange(1e+6) * d # [us]
    y = 1000. * sin(2 * pi * 9.12 * t) # 10Vpp -> 30dBm 1Vpp -> 10dBm
    y = y + 787.3 * (sin(2 * pi * 10 * t) > 0.) # [mV]
    o.sig_in.set(y)
    o = App(Tkinter.Toplevel(master),Plot3D); o.pack()
    Tkinter.mainloop()
