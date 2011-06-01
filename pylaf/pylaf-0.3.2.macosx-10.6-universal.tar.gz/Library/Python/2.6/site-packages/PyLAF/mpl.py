# coding: utf-8

import Tkinter, ttk #@UnresolvedImport
import tkFileDialog
import numpy, matplotlib, inspect
import utils.mpl, core, gui, widgets, kitchen
from numpy import recarray, zeros
from scipy import array, real, imag, fft, fftpack, log10, arange
from core import Port, Output

class ModalAxesPanel(Tkinter.Frame):
    def __init__(self,master=None,cnf={},**kw):
        Tkinter.Frame.__init__(self,master,cnf,**kw)
        c = self.children
        
        widgets.Radiobuttons(self,modes=[('Min/Max','minmax'),('Center/Span','centerspan')],name='mode').grid(row=0,column=1)
        c['mode'].value.set('minmax')
        projection = {'minmax'    : (lambda x: x, lambda x: x),
                      'centerspan': (lambda x: [(x[0]+x[1])/2.,x[1]-x[0]],lambda x: [x[0]-x[1]/2.,x[0]+x[1]/2])}
        
        Tkinter.Label(self,text='X Axis').grid(row=1,column=0)
        widgets.MultipleEntries(self,column=2,name='xlim',projection=projection).grid(row=1,column=1)
        widgets.Button(self,text='auto',name='autoscalex').grid(row=1,column=3)
        
        Tkinter.Label(self,text='Y Axis').grid(row=2,column=0)
        widgets.MultipleEntries(self,column=2,name='ylim').grid(row=2,column=1)
        widgets.Button(self,text='auto',name='autoscaley').grid(row=2,column=3)
        
        c['mode'].value.link(c['xlim'].mode)
        
class AxesPanel(Tkinter.Frame):
    def __init__(self,master=None,cnf={},**kw):
        Tkinter.Frame.__init__(self,master,cnf,**kw)
        
        Tkinter.Label(self,text='X Axis').grid(row=1,column=0)
        widgets.MultipleEntries(self,column=2,name='xlim').grid(row=1,column=1)
        widgets.Button(self,text='auto',name='autoscalex').grid(row=1,column=3)
        
        Tkinter.Label(self,text='Y Axis').grid(row=2,column=0)
        widgets.MultipleEntries(self,column=2,name='ylim').grid(row=2,column=1)
        widgets.Button(self,text='auto',name='autoscaley').grid(row=2,column=3)
        
class BasePlot(core.Component):
    def __init__(self,master=None,name=None):
        core.Component.__init__(self,master,name)
        self.sigin  = Port(array([])).bind(self._sigin)
        self.sigout = Output(array([]))#.bind(self._sigin) # フォーマットの変化で処理を開始しないため
    def _sigin(self):
        self.sigout.set(self.sigin.get())
    class Plot(utils.mpl.BasePlot,gui.BasePanel):
        def __init__(self,*args,**kw):
            utils.mpl.BasePlot.__init__(self,*args,**kw)
            self.sigin   = Port(None).bind(self._sigin)
            self.linkmap = {'sigin' : 'sigout'}
            self.connect()
        def connect(self):
            # プロット範囲更新イベントの設定
            self._callbacks = cb = {}
            cb['cid_xlim']  = self.ax.callbacks.connect('xlim_changed',self._update_xlim)
            cb['cid_ylim']  = self.ax.callbacks.connect('ylim_changed',self._update_ylim)
        def disconnect(self):
            self.ax.callbacks.disconnect(self._callbacks['cid_xlim'])
            self.ax.callbacks.disconnect(self._callbacks['cid_ylim'])
        def destroy(self):
            self.disconnect()
            utils.mpl.BasePlot.destroy(self)
        def _sigin(self,sigin=None):
            if sigin == None: sigin = self.sigin.get()
            if sigin == None: return
            args,kw = utils.parse_port_args(sigin)
            self.plot(*args,**kw)
        def plot(self,*args,**kwargs):
            self.clear()
            self.ax.plot(*args,**kwargs)
            self.canvas.show()
            self.update_idletasks() # スレッド処理でButtonに対応するにはupdate_idletasksを使う。updateではButtonがロックすることがある。
        def _update_xlim(self,e): # ax の xlim が更新されたときに control の GUI を更新する
            control = self.sibling('control')
            if control == None: return
            self._update_xlim_called = True
            control.port('xlim').set(list(self.ax.get_xlim()))
            del self._update_xlim_called
        def _update_ylim(self,e): # ax の xlim が更新されたときに control の GUI を更新する
            control = self.sibling('control')
            if control == None: return
            self._update_ylim_called = True
            control.port('ylim').set(list(self.ax.get_ylim()))
            del self._update_ylim_called
        def resize(self,dpi=None,figsize=None):
            if (dpi == None or figsize == None): return
            subplotpars = self.ax.figure.subplotpars
            left   = subplotpars.left
            right  = subplotpars.right
            bottom = subplotpars.bottom
            top    = subplotpars.top
            title  = self.ax.get_title()
            xlabel = self.ax.get_xlabel()
            ylabel = self.ax.get_ylabel()
            self.disconnect()
            utils.mpl.BasePlot.resize(self,dpi=dpi,figsize=figsize)
            self.connect()
            self.ax.set_ylabel(ylabel)
            self.ax.set_xlabel(xlabel)
            self.ax.set_title(title)
            self.ax.figure.subplots_adjust(left = left, right = right, bottom = bottom, top = top)
            if not self.sigin.subject.value == None:
                self._sigin(self.sigin.subject.value) # Portの実装に依存してしまっている！ので後で考えよう。
    class Control(gui.Panel):
        def __init__(self,master=None,cnf={},**kw):
            gui.Panel.__init__(self,master,cnf,**kw)
            builder = gui.TableBuilder(self)
            builder.add(AxesPanel,name='axes').grid(columnspan=2)
            #
            plot = self.sibling('plot')
            if plot.ax.get_autoscalex_on(): # autoscalex ならば
                self.widget('autoscalex').config(state=Tkinter.DISABLED) # ボタンを不活性
            else: # not autoscalex ならば
                self.widget('autoscalex').config(state=Tkinter.NORMAL) # ボタンを活性
            if plot.ax.get_autoscaley_on():
                self.widget('autoscaley').config(state=Tkinter.DISABLED)
            else:
                self.widget('autoscaley').config(state=Tkinter.NORMAL)
            self.port('xlim').set(list(plot.ax.get_xlim()))
            self.port('ylim').set(list(plot.ax.get_ylim()))
            #
            self.port('xlim').bind(self._changed_xlim)
            self.port('ylim').bind(self._changed_ylim)
            self.port('autoscalex').bind(self._changed_autoscalex)
            self.port('autoscaley').bind(self._changed_autoscaley)
        def _changed_xlim(self):
            '''
            xlim エントリーが変更されたらば、
            autoscalex を disable し、
            autoscalex ボタンを enable し、
            xlim を更新し、
            プロットを再描画する
            '''
            plot = self.sibling('plot')
            try: plot._update_xlim_called
            except AttributeError:
                plot.ax.set_autoscalex_on(False)
                self.widget('autoscalex').config(state=Tkinter.NORMAL)
                #plot.autoscalex_config.set(state=Tkinter.NORMAL)
                plot.ax.set_xlim(*self.port('xlim').get())
                plot.canvas.show()
        def _changed_ylim(self):
            plot = self.sibling('plot')
            try: plot._update_ylim_called
            except AttributeError:
                plot.ax.set_autoscaley_on(False)
                self.widget('autoscaley').config(state=Tkinter.NORMAL)
                plot.ax.set_ylim(*self.port('ylim').get())
                plot.canvas.show()
        def _changed_autoscalex(self):
            '''
            autoscalexボタンを押したらば、
            autoscalexをenableし、
            autoscalexボタンをdisableし、
            再プロットする
            '''
            plot = self.sibling('plot')
            plot.ax.set_autoscalex_on(True)
            self.widget('autoscalex').config(state=Tkinter.DISABLED)
            plot._sigin()
        def _changed_autoscaley(self):
            plot = self.sibling('plot')
            plot.ax.set_autoscaley_on(True)
            self.widget('autoscaley').config(state=Tkinter.DISABLED)
            plot._sigin()
    class Config:
        class Decolation(gui.Panel):
            def __init__(self,master=None,cnf={},**kw):
                gui.Panel.__init__(self,master,cnf,**kw)
                s = {'sticky' : Tkinter.W+Tkinter.E}
                b, l, e = gui.TableBuilder(self), Tkinter.Label, widgets.Entry
                b.add(l,text='PADL').grid(**s).add(e,name='padl').grid(**s)
                b.add(l,text='PADR').grid(**s).add(e,name='padr').grid(**s)
                b.add(l,text='PADB').grid(**s).add(e,name='padb').grid(**s)
                b.add(l,text='PADT').grid(**s).add(e,name='padt').grid(**s)
                b.add(widgets.Button,name='reset_pad',text='reset').grid(columnspan=2,**s)
                b.add(l,text='TITLE').grid(**s).add(e,name='title').grid(**s)
                b.add(l,text='XLABEL').grid(**s).add(e,name='xlabel').grid(**s)
                b.add(l,text='YLABEL').grid(**s).add(e,name='ylabel').grid(**s)
                b.add(widgets.Button,name='reset_label',text='reset').grid(columnspan=2,**s)
                b.add(l,text='DPI').grid(**s).add(e,name='dpi').grid(**s)
                b.add(l,text='FIGSIZE').grid(**s).add(widgets.MultipleEntries,name='figsize').grid(**s)
                #
                plot        = self.sibling('plot')
                subplotpars = plot.ax.figure.subplotpars
                self._config = {
                                'left'   : subplotpars.left,
                                'right'  : subplotpars.right,
                                'bottom' : subplotpars.bottom,
                                'top'    : subplotpars.top,
                                'title'  : plot.ax.get_title(),
                                'xlabel' : plot.ax.get_xlabel(),
                                'ylabel' : plot.ax.get_ylabel(),
                                'figsize' : plot.figure.get_size_inches(),
                                'dpi'     : plot.figure.get_dpi(),
                                }
                self.port('padl').set(subplotpars.left)
                self.port('padr').set(subplotpars.right)
                self.port('padb').set(subplotpars.bottom)
                self.port('padt').set(subplotpars.top)
                self.port('title').set(plot.ax.get_title())
                self.port('xlabel').set(plot.ax.get_xlabel())
                self.port('ylabel').set(plot.ax.get_ylabel())
                self.port('figsize').set(self._config['figsize'])
                self.port('dpi').set(self._config['dpi'])
                #
                self.port('reset_pad').bind(self._reset_pad)
                self.port('reset_label').bind(self._reset_label)
                self.port('figsize').bind(self.resize)
                self.port('dpi').bind(self.resize)
                self.port('padl').bind(self.update_adjust)
                self.port('padr').bind(self.update_adjust)
                self.port('padb').bind(self.update_adjust)
                self.port('padt').bind(self.update_adjust)
                self.port('title').bind(self.set_title)
                self.port('xlabel').bind(self.set_xlabel)
                self.port('ylabel').bind(self.set_ylabel)
            def resize(self):
                figsize = self.port('figsize').get()
                dpi     = self.port('dpi').get()
                self.sibling('plot').resize(dpi,figsize)
            def set_title(self):
                plot = self.sibling('plot')
                plot.ax.set_title(self.port('title').get())
                plot.canvas.show()
            def set_xlabel(self):
                plot = self.sibling('plot')
                plot.ax.set_xlabel(self.port('xlabel').get())
                plot.canvas.show()
            def set_ylabel(self):
                plot = self.sibling('plot')
                plot.ax.set_ylabel(self.port('ylabel').get())
                plot.canvas.show()
            def update_adjust(self):
                plot = self.sibling('plot')
                plot.ax.figure.subplots_adjust(left   = self.port('padl').get(),
                                               right  = self.port('padr').get(),
                                               bottom = self.port('padb').get(),
                                               top    = self.port('padt').get())
                plot.canvas.show()
            def _reset_pad(self):
                self.port('padl').set(self._config['left'])
                self.port('padr').set(self._config['right'])
                self.port('padb').set(self._config['bottom'])
                self.port('padt').set(self._config['top'])
            def _reset_label(self):
                self.port('title').set(self._config['title'])
                self.port('xlabel').set(self._config['xlabel'])
                self.port('ylabel').set(self._config['ylabel'])
    class Menu(gui.DefaultMenu):
        ITEMS = [
                 ['File',
                  ['add_command', utils.functions.kw(label='Import',command='_import')],
                  ['add_command', {'label' : 'Export', 'command' : '_export'}],
                  ['add_separator', {}],
                  ['add_command', {'label' : 'Clear', 'command' : '_clear'}],
                  # Export Original Data
                  # Export Processed Data
                  ],
                 ]
        def _clear(self):
            plot = self.master.panel('plot')
            plot.clear()
            plot.canvas.show()
            plot.update_idletasks() # スレッド処理でButtonに対応するにはupdate_idletasksを使う。updateではButtonがロックすることがある。
            self.master.component().sigout.set(None)
        def _import(self):
            fname = tkFileDialog.askopenfilename()
            a    = numpy.loadtxt(fname).transpose()
            #component = self.master.component()
            #component.sigout.set(self.import_format(a))
            self.master.panel('plot').plot(*self.import_format(a))
        def _export(self):
            ax    = self.master.panel('plot').ax
            lines = ax.get_lines()
            if len(lines) == 0: return
            buf   = []
            buf.append(lines[0].get_xdata())
            for line in lines:
                buf.append(line.get_ydata())
            fname = tkFileDialog.asksaveasfilename()
            if not fname == None:
                numpy.savetxt(fname,self.export_format(array(buf).transpose()))
        def import_format(self,a):
            return a[0,:], a[1:,:].transpose()
        def export_format(self,buf):
            return buf
            
class BasePlotPanel(gui.Panel):
    def __init__(self,master=None,cnf={},**kw):
        gui.Panel.__init__(self,master,cnf,**kw)
        gui.Embed(self,BasePlot,text='BasePlot').pack(side=Tkinter.LEFT)

class Oscilloscope(BasePlot):
    def __init__(self,master=None,name=None):
        BasePlot.__init__(self,master,name)
        self.xunit      = Port(1e-3)
        self.yunit      = Port(1e-3)
        self.samplerate = Port(1.)
        members = [key for key,o in inspect.getmembers(master,core.isPort)]
        if members.count('samplerate'): master.samplerate.link(self.samplerate,set=True)
    class Plot(BasePlot.Plot):
        def __init__(self,*args,**kw):
            BasePlot.Plot.__init__(self,*args,**kw)
            self.ax.set_xlabel('Time [us]')
            self.ax.set_ylabel('Signal [mV]')
            self.samplerate = Port(1.)
            self.decimation = Port(1)
        def _sigin(self,sigin=None):
            if sigin == None: sigin = self.sigin.get()
            if sigin == None: return
            sig, kw = utils.parse_port_args(sigin)
            samplerate = self.samplerate.get()
            decimation = self.decimation.get()
            sig = sig[0]
            sig = sig[...,::decimation]
            time  = arange(sig.shape[-1]) / samplerate * decimation
            BasePlot.Plot.plot(self,time,sig.transpose(),**kw)
    class Control(BasePlot.Control):
        def __init__(self,master=None,cnf={},**kw):
            BasePlot.Control.__init__(self,master,cnf,**kw)
            b, tkl, e, l = gui.TableBuilder, Tkinter.Label, widgets.Entry, widgets.Label
            b = gui.TableBuilder(self)
            b.add(tkl,text='Sample Rate [MS/sec]').grid().add(l,name='samplerate').grid()
            b.add(tkl,text='Decimation Index').grid().add(e,name='decimation').grid()
            #
            plot = self.sibling('plot')
            plot.decimation.link(self.port('decimation'),set=True)
            self.port('decimation').bind(self._trig)
        def _trig(self): self.component().sigout.set(self.component().sigout.get())
    class Config(BasePlot.Config):
        class Decolation(BasePlot.Config.Decolation):
            def __init__(self,master=None,cnf={},**kw):
                BasePlot.Config.Decolation.__init__(self,master,cnf,**kw)
                b, l, e = gui.TableBuilder(self), Tkinter.Label, widgets.Entry
                b.add(l,text='XUNIT').grid().add(e,name='xunit').grid()
                b.add(l,text='YUNIT').grid().add(e,name='yunit').grid()
#    class Menu(BasePlot.Menu):
#        def import_format(self,a):
#            dt = a[0,1] - a[0,0]
#            self.master.component().samplerate.set(dt)
#            return a[1:,:]
            
class OscilloscopePanel(gui.Panel):
    def __init__(self,master=None,cnf={},**kw):
        gui.Panel.__init__(self,master,cnf,**kw)
        gui.Embed(self,Oscilloscope,text='Oscilloscope').pack(side=Tkinter.LEFT)
        
class Gauss(BasePlot):
    #def _sigin(self):
    #    sigin = self.sigin.get()
    #    c, kw = utils.parse_port_args(sigin)
    #    c = c[0]
    #    self.sigout.set(real(c),imag(c),**kw)
    class Plot(BasePlot.Plot):
        def __init__(self,*args,**kw):
            BasePlot.Plot.__init__(self,*args,**kw)
            self.ax.set_title('Gauss Plane')
            self.ax.set_xlabel('Real(x)')
            self.ax.set_ylabel('Imag(x)')
        def _sigin(self,sigin=None):
            if sigin == None: sigin = self.sigin.get()
            if sigin == None: return
            c, kw = utils.parse_port_args(sigin)
            c = c[0]
            BasePlot.Plot.plot(self,real(c),imag(c),**kw)

class GaussPanel(gui.Panel):
    def __init__(self,master=None,cnf={},**kw):
        gui.Panel.__init__(self,master,cnf,**kw)
        gui.Embed(self,Gauss,text='Gauss').pack(side=Tkinter.LEFT)

class Spectrum(BasePlot):
    def __init__(self,master=None,name=None):
        BasePlot.__init__(self,master,name)
        self.samplerate = Port(1.)
        members = [key for key,o in inspect.getmembers(master,core.isPort)]
        if members.count('samplerate'): master.samplerate.link(self.samplerate,set=True)
    class Plot(BasePlot.Plot):
        def __init__(self,*args,**kw):
            BasePlot.Plot.__init__(self,*args,**kw)
            self.ax.set_title('Spectrum')
            self.ax.set_xlabel('Frequency [MHz]')
            self.ax.set_ylabel('Power [dBm]')
            self.samplerate = Port(1.)
            self.decimation = Port(1)
        def _sigin(self,sigin=None):
            if sigin == None: sigin = self.sigin.get()
            if sigin == None: return
            sig, kw = utils.parse_port_args(sigin)
            #if len(sig.shape) == 1: sig = sig.reshape(1,len(sig))
            samplerate = self.samplerate.get()
            decimation = self.decimation.get()
            sig = sig[0]
            sig = sig[...,::decimation]
            # sig  = sig[:2**int(log2(sig.size))]
            try:
                f   = fft(sig)
            except ValueError:
                from warnings import warn
                warn('ValueError has occur.')
                return
            # f[0] = f[0] * .5 # 片側スペクトルを見たい場合にはこの行をアクティベート
            v   = fftpack.fftshift(f * 2.0 / sig.shape[-1])
            freq = fftpack.fftshift(fftpack.fftfreq(sig.shape[-1],1./samplerate*decimation))
            value = 10 * log10(real(v*v.conj())/2/50) - 30
            BasePlot.Plot.plot(self,freq,value.transpose(),**kw)
            #self.sigout.set(freq, value.transpose())
    class Control(BasePlot.Control):
        def __init__(self,master=None,cnf={},**kw):
            BasePlot.Control.__init__(self,master,cnf,**kw)
            b, tkl, e, l = gui.TableBuilder, Tkinter.Label, widgets.Entry, widgets.Label
            b = gui.TableBuilder(self)
            b.add(tkl,text='Sample Rate [MS/sec]').grid().add(l,name='samplerate').grid()
            b.add(tkl,text='Decimation Index').grid().add(e,name='decimation').grid()
            #
            plot = self.sibling('plot')
            plot.decimation.link(self.port('decimation'),set=True)
            self.port('decimation').bind(self._trig)
        def _trig(self):
            self.component().sigout.set(self.component().sigout.get())
            
class SpectrumPanel(gui.Panel):
    def __init__(self,master=None,cnf={},**kw):
        gui.Panel.__init__(self,master,cnf,**kw)
        gui.Embed(self,Spectrum,text='Spectrum').pack(side=Tkinter.LEFT)

import weakref, scipy
if __name__ == '__main__':
    class MyComponent(core.Component):
        def __init__(self,master=None,name=None):
            core.Component.__init__(self,master,name)
            scope = Oscilloscope(self,name='scope') # メモリリークを起こしますのでメンバ変数として保持しないでください
            self.sigout = Port(array([])); self.sigout.link(scope.sigin)
            self.freq = Port(1.)
        def _trig(self):
            tim = scipy.arange(1000) / 100.
            omg = 2 * scipy.pi * self.freq.get() * tim
            self.sigout.set(scipy.sin(omg))
            self.freq.set(self.freq.get() + .1)
        class Plot(gui.Panel):
            def __init__(self,master=None,cnf={},**kw):
                gui.Panel.__init__(self,master,cnf,**kw)
                gui.Embed(self,Oscilloscope,name='scope',text='Scope1').pack(side=Tkinter.LEFT)
                gui.Embed(self,Oscilloscope,text='Scope2').pack(side=Tkinter.LEFT)
        class Control(gui.Panel):
            def __init__(self,master=None,cnf={},**kw):
                gui.Panel.__init__(self,master,cnf,**kw)
                builder = gui.TableBuilder(self)
                builder.add(Tkinter.Label,text='Frequency').grid()
                builder.add(widgets.Entry,name='freq').grid().bind('<Return>',self._trig)
                builder.add(Tkinter.Button,name='trig',text='trig',command=self._trig).grid(columnspan=2,sticky=Tkinter.W+Tkinter.E)
                #
            def _trig(self,*args): self.component()._trig()
    tk = Tkinter.Tk()
    a = MyComponent()
    a1 = gui.Console(tk,a)#; a1.assign(a); a1.pack(); 
    a1.master.title('master')
    a2 = gui.Console(Tkinter.Toplevel(tk),Oscilloscope())
    a2.master.title('osc')
    a1.component().sigout.link(a2.component().sigin)
    Tkinter.mainloop()
    import gc
    a1 = weakref.ref(a1); gc.collect(); print 'a1:', a1
    a  = weakref.ref(a);  gc.collect(); print 'a :', a
    a2 = weakref.ref(a2); gc.collect(); print 'a2:', a2
    