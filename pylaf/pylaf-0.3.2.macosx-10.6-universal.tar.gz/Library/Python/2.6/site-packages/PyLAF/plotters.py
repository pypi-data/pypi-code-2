# coding: utf-8

import StringIO, Image, ImageTk, matplotlib, tkFileDialog
matplotlib.use('Agg',warn=False)
from matplotlib import pyplot
from scipy import array, arange, real, imag, sin, pi, fft, log10, fftpack
from Tkinter import Label, BOTTOM, Toplevel, mainloop, _cnfmerge
from framework import PortHolder, Port, SLAVE
from framework import DoubleVar, IntVar, BooleanVar, StringVar
from widgets import popcnf, Menu, GridPane

class SimplePlot(Label):
    '''
    軽量プロットウィジェット
    CanvasTkAgg を使った埋め込みはでは使用後に解放されずメモリに残ってしまうので、
    以下のような軽量プロットを作ってみた。
    matplotlib のバックエンドで画像を作成してPILで表示する。
    グラフの描画だけなら、むしろこちらの方が管理楽ちん。
    インタラクティブにしたい場合は、メインウィンドウと同じライフサイクルでひとつだけCanvasTkAggを使い
    共用するとよいだろう。
    '''
    def __init__(self,master=None,cnf={},**kw):
        if kw: cnf = _cnfmerge((cnf,kw))
        figsize, dpi = popcnf('figsize',cnf), popcnf('dpi',cnf)
        if figsize == None: figsize = (300,300)
        if dpi == None: dpi = 50
        Label.__init__(self,master,cnf,**kw)
        self.dpi = dpi # dpi は 100 で固定のようだ。なぜか dpi=xxx や set_dpi(xxx) などが反映されない。
        size = (float(figsize[0]) / dpi, float(figsize[1]) / dpi)
        self.ax = pyplot.figure(figsize=size).add_subplot(111)
    def show(self):
        imgdata = StringIO.StringIO()
        self.ax.figure.savefig(imgdata, format='png')
        imgdata.seek(0)
        im = Image.open(imgdata)
        width, height = self.ax.figure.get_size_inches()
        width, height = int(width * self.dpi), int(height * self.dpi)
        im = im.resize((width,height),Image.ANTIALIAS) # アンチエイリアス付きで拡大縮小する
        self.img = ImageTk.PhotoImage(im) # インスタンスで保持しないと show() を抜けた瞬間に画像が解放されてしまう
        self.configure(image=self.img)
    def resize(self,figsize=(300,300),dpi=50):
        self.dpi = dpi
        size = (float(figsize[0]) / dpi, float(figsize[1]) / dpi)
        self.ax = pyplot.figure(figsize=size).add_subplot(111)
        self.show()
    def destroy(self):
        Label.destroy(self)
        pyplot.close(self.ax.figure)
        self.ax = None # AxesSubplot クラスの明示的解放（これしないとゾンビが残る）

class BasePlot(SimplePlot,PortHolder):
    '''
    プロットの基本機能を提供する。オートスケール、書き出し、デコレーションなど。
    '''
    def destroy(self):
        PortHolder.destroy(self)
        SimplePlot.destroy(self)
    def __init__(self,master=None,cnf={},**kw):
        SimplePlot.__init__(self,master,cnf,**kw)
        self.sig_in = Port(array([])).bind(self._sig_in)
        self.kwargs = Port({}).bind(self._sig_in)
        self.left   = Port(0.15).bind(self._decolation_autoshow)
        self.right  = Port(0.9).bind(self._decolation_autoshow)
        self.bottom = Port(0.1).bind(self._decolation_autoshow)
        self.title  = Port('').bind(self._decolation_autoshow)
        self.xlabel = Port('xlabel').bind(self._decolation_autoshow)
        self.ylabel = Port('ylabel').bind(self._decolation_autoshow)
        xlim        = self.ax.get_xlim()
        self.xmin   = Port(xlim[0]).bind(self._xlim_fixed_autoshow)
        self.xmax   = Port(xlim[1]).bind(self._xlim_fixed_autoshow)
        ylim        = self.ax.get_ylim()
        self.ymin   = Port(ylim[0]).bind(self._ylim_fixed_autoshow)
        self.ymax   = Port(ylim[1]).bind(self._ylim_fixed_autoshow)
        self.autoscalex = Port(True).bind(self._sig_in)
        self.autoscaley = Port(True).bind(self._sig_in)
        self.menu(self,popup=True,tearoff=0)
    def configure(self,figsize=None,dpi=None,cnf={},**kw):
        if not figsize == None and dpi == None:
            self.resize(figsize)
        elif not dpi == None and figsize == None:
            self.resize(dpi)
        elif not figsize == None and not dpi == None:
            self.resize(figsize,dpi)
        SimplePlot.configure(self,cnf,**kw)
    def menu(self,master,cnf={},**kw):
        menu = Menu(master,cnf,**kw)
        menu.add_command(label="Save Figure",command=self._savefig)
        menu.add_command(label="Popup Console",command=self._popup_console)
        menu.add_command(label="Popup Decolation",command=self._popup_decoration)
        return menu
    def gui(self,master,cnf={},**kw):
        self.plot(); self.show()
        o = self.console(master); o.pack(side=BOTTOM)
        return self
    def _sig_in(self):
        self.plot(self.sig_in.get().transpose()); self.show()
    def _popup_decoration(self):
        self.decoration(Toplevel(self)).pack()
    def _popup_console(self):
        self.console(Toplevel(self)).pack()
    def _savefig(self):
        fname = tkFileDialog.asksaveasfilename(title='Enter Filename')
        self.ax.figure.savefig(fname)
    def _xlim_fixed_autoshow(self):
        self.autoscalex.set(False,mode=SLAVE)
        self.ax.set_xlim(self.xmin.get(), self.xmax.get())
        self.show()
    def _ylim_fixed_autoshow(self):
        self.autoscaley.set(False,mode=SLAVE)
        self.ax.set_ylim(self.ymin.get(), self.ymax.get())
        self.show()
    def plot(self,*args,**keys):
        self.ax.cla()
        self._decolation()
        kwargs = self.kwargs.get()
        kwargs['scalex'] = self.autoscalex.get()
        kwargs['scaley'] = self.autoscaley.get()
        self.ax.plot(*args,**kwargs)
        self._update_scale()
    def replot(self):
        self._sig_in()
    def _decolation(self):
        self.ax.figure.subplots_adjust(left=self.left.get())
        self.ax.figure.subplots_adjust(right=self.right.get())
        self.ax.figure.subplots_adjust(bottom=self.bottom.get())
        self.ax.set_title(self.title.get())
        self.ax.set_xlabel(self.xlabel.get())
        self.ax.set_ylabel(self.ylabel.get())
    def _decolation_autoshow(self):
        self._decolation()
        self.show()
    def _update_scale(self):
        xlim = self.ax.get_xlim()
        self.xmin.set(xlim[0],mode=SLAVE)
        self.xmax.set(xlim[1],mode=SLAVE)
        ylim = self.ax.get_ylim()
        self.ymin.set(ylim[0],mode=SLAVE)
        self.ymax.set(ylim[1],mode=SLAVE)
    def console(self,master):
        o = GridPane(master)
        o.entry_with_tcb('XLIM',BooleanVar(self.autoscalex),DoubleVar(self.xmin),DoubleVar(self.xmax))
        o.entry_with_tcb('YLIM',BooleanVar(self.autoscaley),DoubleVar(self.ymin),DoubleVar(self.ymax))
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

class Constellation(BasePlot):
    '''
    デシメーションなどの機能を多重継承して追加できるといいけどね。
    '''
    def __init__(self,master=None,cnf={},**kw):
        BasePlot.__init__(self,master,cnf,**kw)
        self.samplerate = Port(1.).bind(self._sig_in)
        self.style      = Port('.').bind(self._sig_in)
        self.alpha      = Port(1.).bind(self._sig_in)
        self.begin      = Port(0.).bind(self._sig_in) # プロット開始（％）
        self.end        = Port(100.).bind(self._sig_in) # プロット終了（％）
        self.decimation = Port(1).bind(self._sig_in)
        self.xlabel.set('I Channel [mV]',mode=SLAVE)
        self.ylabel.set('Q Channel [mV]',mode=SLAVE)
    def _sig_in(self):
        sig = self.sig_in.get()
        b,e = self.begin.get(), self.end.get()
        sig = sig[...,::self.decimation.get()]
        sig = sig[...,(b / 100 * sig.shape[-1]):(e / 100 * sig.shape[-1])]
        sig = sig.transpose()
        kwargs = self.kwargs.get()
        kwargs['alpha'] = self.alpha.get()
        self.kwargs.set(kwargs,mode=SLAVE)
        self.plot(real(sig), imag(sig), self.style.get())
        self.show()
        self.master.update()
    def decoration(self,master):
        o = BasePlot.decoration(self,master)
        o.entry('Plot Style',StringVar(self.style))
        return o
    def console(self,master):
        o = BasePlot.console(self,master)
        o.entry('Sample Rate [MS/sec]',DoubleVar(self.samplerate))
        o.entry('Alpha Index',DoubleVar(self.alpha))
        o.entry('Decimation Index',IntVar(self.decimation))
        return o

class XYPlot(BasePlot):
    def __init__(self,master=None,cnf={},**kw):
        BasePlot.__init__(self,master,cnf,**kw)
        self.xaxis = Port(array([])).bind(self._sig_in)
        self.yaxis = Port(array([])).bind(self._sig_in)
        self.style = Port('-').bind(self._sig_in)
        self.xlabel.set('X Axis',mode=SLAVE)
        self.ylabel.set('Y Axis',mode=SLAVE)
    def _sig_in(self):
        xaxis, yaxis = self.xaxis.get(), self.yaxis.get()
        if xaxis.shape[-1] == yaxis.shape[-1]:
            self.plot(xaxis, yaxis.transpose(), self.style.get())
        self.show()

class Oscilloscope(BasePlot):
    def __init__(self,master=None,cnf={},**kw):
        BasePlot.__init__(self,master,cnf,**kw)
        self.samplerate = Port(1.).bind(self._sig_in)
        self.decimation = Port(1).bind(self._sig_in)
        self.style      = Port('-').bind(self._sig_in)
        self.xlabel.set('Time [us]',mode=SLAVE)
        self.ylabel.set('Signal [mV]',mode=SLAVE)
    def _sig_in(self):
        sig = self.sig_in.get()
        sig = sig[...,::self.decimation.get()]
        samplerate = self.samplerate.get() / self.decimation.get()
        time  = 1. / samplerate * arange(sig.shape[-1])
        self.plot(time, sig.transpose(), self.style.get())
        self.show()
    def console(self,master):
        o = BasePlot.console(self,master)
        o.entry('Sample Rate [MS/sec]',DoubleVar(self.samplerate))
        o.entry('Decimation Index',IntVar(self.decimation))
        return o

class Spectrum(BasePlot):
    def __init__(self,master=None,cnf={},**kw):
        BasePlot.__init__(self,master,cnf,**kw)
        self.samplerate   = Port(1.).bind(self._sig_in)
        self.style        = Port('-').bind(self._sig_in)
        self.decimation   = Port(1).bind(self._sig_in)
        self.xlabel.set('Frequency [MHz]',mode=SLAVE)
        self.ylabel.set('Power [dBm]',mode=SLAVE)
    def _sig_in(self):
        sig = self.sig_in.get()
        samplerate = self.samplerate.get() / self.decimation.get()
        style = self.style.get()
        sig = sig[...,::self.decimation.get()]
        # sig  = sig[:2**int(log2(sig.size))]
        try:
            f   = fft(sig)
            # f[0] = f[0] * .5 # 片側スペクトルを見たい場合にはこの行をアクティベート
            v   = fftpack.fftshift(f * 2.0 / sig.size)
            freq = fftpack.fftshift(fftpack.fftfreq(sig.size,1./samplerate))
            value = 10 * log10(real(v*v.conj())/2/50) - 30
            self.plot(freq, value, style)
            self.show()
            self.master.update()
        except ValueError:
            self.plot()
            self.show()
            self.master.update()
            from warnings import warn
            warn('Invalid number of FFT data points (0) specified.')
    def console(self,master):
        o = BasePlot.console(self,master)
        o.entry('Sample Rate [MS/sec]',DoubleVar(self.samplerate))
        o.entry('Decimation Index',IntVar(self.decimation))
        return o

def test(master=None):
    from framework import App
    o = App(master,Spectrum); o.pack()
    osc = App(Toplevel(master),Oscilloscope); osc.pack()
    o.sig_in.link(osc.sig_in)
    o.samplerate.link(osc.samplerate)
    o.samplerate.set(250.,mode=SLAVE)
    osc.xmin.set(0)
    osc.xmax.set(1000)
    d = 1. / o.samplerate.get()
    t = arange(1e+6) * d # [us]
    y = 1000. * sin(2 * pi * 9.12 * t) # 10Vpp -> 30dBm 1Vpp -> 10dBm
    y = y + 787.3 * (sin(2 * pi * 10 * t) > 0.) # [mV]
    o.sig_in.set(y)
    
if __name__ == '__main__':
    test()
    mainloop()
