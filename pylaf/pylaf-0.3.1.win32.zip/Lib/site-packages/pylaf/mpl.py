# coding: utf-8

import Tkinter
import utils.mpl, core, gui
from scipy import array
from core import Port

class ModalAxesPanel(Tkinter.Frame):
    def __init__(self,master=None,cnf={},**kw):
        Tkinter.Frame.__init__(self,master,cnf,**kw)
        c = self.children
        
        gui.Radiobuttons(self,modes=[('Min/Max','minmax'),('Center/Span','centerspan')],name='mode').grid(row=0,column=1)
        c['mode'].value.set('minmax')
        projection = {'minmax'    : (lambda x: x, lambda x: x),
                      'centerspan': (lambda x: [(x[0]+x[1])/2.,x[1]-x[0]],lambda x: [x[0]-x[1]/2.,x[0]+x[1]/2])}
        
        Tkinter.Label(self,text='X Axis').grid(row=1,column=0)
        gui.MultipleEntries(self,column=2,name='xlim',projection=projection).grid(row=1,column=1)
        gui.Button(self,text='auto',name='autoscalex').grid(row=1,column=3)
        
        Tkinter.Label(self,text='Y Axis').grid(row=2,column=0)
        gui.MultipleEntries(self,column=2,name='ylim').grid(row=2,column=1)
        gui.Button(self,text='auto',name='autoscaley').grid(row=2,column=3)
        
        c['mode'].value.link(c['xlim'].mode)
        
class AxesPanel(Tkinter.Frame):
    def __init__(self,master=None,cnf={},**kw):
        Tkinter.Frame.__init__(self,master,cnf,**kw)
        
        Tkinter.Label(self,text='X Axis').grid(row=1,column=0)
        gui.MultipleEntries(self,column=2,name='xlim').grid(row=1,column=1)
        gui.Button(self,text='auto',name='autoscalex').grid(row=1,column=3)
        
        Tkinter.Label(self,text='Y Axis').grid(row=2,column=0)
        gui.MultipleEntries(self,column=2,name='ylim').grid(row=2,column=1)
        gui.Button(self,text='auto',name='autoscaley').grid(row=2,column=3)
        
class BasePlot(gui.ComponentWithGUI):
    def __init__(self,master=None,name=None):
        gui.ComponentWithGUI.__init__(self,master,name)
        self.sigin      = Port(array([])).bind(self._sigin)
        self.sigout     = Port(array([]))
        self.console    = Port({})
        self.xlim       = Port([0.,1.])
        self.autoscalex = Port(None)
        self.autoscalex_config = Port(None)
        self.ylim       = Port([0.,1.])
        self.autoscaley = Port(None)
        self.autoscaley_config = Port(None)
        self.padl        = Port(0.15)
        self.padr        = Port(0.9)
        self.padb        = Port(0.1)
        self.reset_pad   = Port(None)
        self.title       = Port('')
        self.xlabel      = Port('xlabel')
        self.ylabel      = Port('ylabel')
        self.reset_label = Port(None).bind(self._reset_label)
    def _sigin(self):
        self.sigout.set(self.sigin.get())
    def _reset_label(self):
        self.title.set('')
        self.xlabel.set('xlabel')
        self.ylabel.set('ylabel')
    class Plot(utils.mpl.BasePlot):
        def __init__(self,*args,**kw):
            utils.mpl.BasePlot.__init__(self,*args,**kw)
            self.sigin      = core.Port(array([])).bind(self._sigin)
            self.xlim       = Port(None).bind(self._changed_xlim)
            self.autoscalex = Port(None).bind(self._changed_autoscalex)
            self.ylim       = Port(None).bind(self._changed_ylim)
            self.autoscaley = Port(None).bind(self._changed_autoscaley)
            self.padl       = Port(None)
            self.padr       = Port(None)
            self.padb       = Port(None)
            update_adjust   = lambda:self.ax.figure.subplots_adjust(left=self.padl.get(),right=self.padr.get(),bottom=self.padb.get())
            self.padl.bind(update_adjust).bind(self.canvas.show)
            self.padr.bind(update_adjust).bind(self.canvas.show)
            self.padb.bind(update_adjust).bind(self.canvas.show)
            self.title      = Port(None).bind(lambda:self.ax.set_title(self.title.get())).bind(self.canvas.show)
            self.xlabel     = Port(None).bind(lambda:self.ax.set_xlabel(self.xlabel.get())).bind(self.canvas.show)
            self.ylabel     = Port(None).bind(lambda:self.ax.set_ylabel(self.ylabel.get())).bind(self.canvas.show)
            self._callbacks = cb = {}
            # プロット範囲更新イベントの設定
            cb['cid_xlim']  = self.ax.callbacks.connect('xlim_changed',self._update_xlim)
            cb['cid_ylim']  = self.ax.callbacks.connect('ylim_changed',self._update_ylim)
            
            self.autoscalex_config = Port(None)
            self.autoscaley_config = Port(None)
        def destroy(self):
            self.ax.callbacks.disconnect(self._callbacks['cid_xlim'])
            self.ax.callbacks.disconnect(self._callbacks['cid_ylim'])
            utils.mpl.BasePlot.destroy(self)
        def assign(self,component):
            component.sigout.link(self.sigin)
            for name in ['xlim','ylim','padl','padr','padb','title','xlabel','ylabel']:
                getattr(self,name).set(getattr(component,name).get())
            for name in ['xlim','ylim','autoscalex','autoscaley',
                         'padl','padr','padb',
                         'title','xlabel','ylabel']:
                getattr(component,name).link(getattr(self,name))
            self.ax.set_autoscalex_on(True)
            self.ax.set_autoscaley_on(True)
            component.autoscalex_config.link(self.autoscalex_config)
            component.autoscaley_config.link(self.autoscaley_config)
        def _sigin(self,sigin=None):
            if sigin == None: sigin = self.sigin.get()
            args,kw = utils.parse_port_args(sigin)
            self.clear()
            self.ax.plot(*args,**kw)
            self.canvas.show()
            self.update_idletasks() # スレッド処理でButtonに対応するにはupdate_idletasksを使う。updateではButtonがロックすることがある。
        def _update_xlim(self,e):
            self._update_xlim_called = True
            self.xlim.set(list(self.ax.get_xlim()))
            del self._update_xlim_called
        def _update_ylim(self,e):
            self._update_ylim_called = True
            self.ylim.set(list(self.ax.get_ylim()))
            del self._update_ylim_called
        def _changed_xlim(self):
            try: self._update_xlim_called
            except AttributeError:
                self.ax.set_autoscalex_on(False)
                self.autoscalex_config.set(state=Tkinter.NORMAL)
                self.ax.set_xlim(*self.xlim.get())
                self.canvas.show()
        def _changed_ylim(self):
            try: self._update_ylim_called
            except AttributeError:
                self.ax.set_autoscaley_on(False)
                self.autoscaley_config.set(state=Tkinter.NORMAL)
                self.ax.set_ylim(*self.ylim.get())
                self.canvas.show()
        def _changed_autoscalex(self):
            self.ax.set_autoscalex_on(True)
            self.autoscalex_config.set(state=Tkinter.DISABLED)
            self._sigin()
        def _changed_autoscaley(self):
            self.ax.set_autoscaley_on(True)
            self.autoscaley_config.set(state=Tkinter.DISABLED)
            self._sigin()
    class Console(gui.Grid):
        def __init__(self,master=None,cnf={},**kw):
            gui.Grid.__init__(self,master,cnf,**kw)
            self.append(AxesPanel(self,name='axes'))
            self.autoscalex_config = Port(None).bind(self._autoscalex_config)
            self.autoscaley_config = Port(None).bind(self._autoscaley_config)
        def assign(self,component):
            axes = self.children['axes'].children
            for name in ['xlim','ylim','autoscalex','autoscaley']:
                axes[name].value.set(getattr(component,name).get())
                getattr(component,name).link(axes[name].value)
            component.autoscalex_config.link(self.autoscalex_config)
            component.autoscaley_config.link(self.autoscaley_config)
        def _autoscalex_config(self):
            args,kw = utils.parse_port_args(self.autoscalex_config.get())
            self.children['axes'].children['autoscalex'].config(*args,**kw)
        def _autoscaley_config(self):
            args,kw = utils.parse_port_args(self.autoscaley_config.get())
            self.children['axes'].children['autoscaley'].config(*args,**kw)
    class Config(Tkinter.Frame):
        class Decolation(gui.Grid):
            def __init__(self,master=None,cnf={},**kw):
                gui.Grid.__init__(self,master,cnf,**kw)
                self.append(gui.Entry(self,name='padl'),label='PADL')
                self.append(gui.Entry(self,name='padr'),label='PADR')
                self.append(gui.Entry(self,name='padb'),label='PADB')
                self.append(gui.Button(self,name='reset_pad',text='reset'))
                self.children['reset_pad'].value.bind(self._reset_pad)
                self.append(gui.Entry(self,name='title'),label='TITLE')
                self.append(gui.Entry(self,name='xlabel'),label='XLABEL')
                self.append(gui.Entry(self,name='ylabel'),label='YLABEL')
                self.append(gui.Button(self,name='reset_label',text='reset'))
            def assign(self,component):
                for key in ('padl','padr','padb','reset_pad','title','xlabel','ylabel','reset_label'):
                    getattr(component,key).link(self.children[key].value,set=True)
            def _reset_pad(self):
                c = self.children
                c['padl'].value.set(0.15)
                c['padr'].value.set(0.9)
                c['padb'].value.set(0.1)
        def __init__(self,master=None,cnf={},**kw):
            Tkinter.Frame.__init__(self,master,cnf,**kw)
            self.Decolation(self,name='decolation').pack()
        def assign(self,component):
            self.children['decolation'].assign(component)
    class Menu(gui.MenuFactory):
        def __init__(self,master=None,cnf={},**kw):
            desc = [['Component', ['Config', 'command']],
                    ['Children',  ['Oscilloscope', 'command'],
                                  ['Spectrum', 'command']]]
            gui.MenuFactory.__init__(self,master,desc,cnf,**kw)
        def assign(self,comp):
            self.children['component'].assign('config',self.master.popup_config)
        
class Oscilloscope(BasePlot):
    def __init__(self,master=None,name=None):
        BasePlot.__init__(self,master,name)
        self.xlabel.set('time')
        self.ylabel.set('voltage')
        self.xunit = Port(1e-3)
        self.yunit = Port(1e-3)
    class Config(BasePlot.Config):
        class Decolation(BasePlot.Config.Decolation):
            def __init__(self,master=None,cnf={},**kw):
                BasePlot.Config.Decolation.__init__(self,master,cnf,**kw)
                self.append(gui.Entry(self,name='xunit'),label='XUNIT')
                self.append(gui.Entry(self,name='yunit'),label='YUNIT')
            def assign(self,component):
                BasePlot.Config.Decolation.assign(self,component)
                for key in ('xunit','yunit'):
                    getattr(component,key).link(self.children[key].value,set=True)
    class Plot(BasePlot.Plot):
        def __init__(self,*args,**kw):
            BasePlot.Plot.__init__(self,*args,**kw)
            self.xunit = Port(None)
            self.yunit = Port(None)
        def assign(self,component):
            BasePlot.Plot.assign(self,component)
            for name in ('xunit','yunit'):
                getattr(component,name).link(getattr(self,name),set=True)

import weakref, scipy
if __name__ == '__main__':
    class MyComponent(gui.ComponentWithGUI):
        def __init__(self,master=None,name=None):
            gui.ComponentWithGUI.__init__(self,master,name)
            scope = Oscilloscope(self,name='scope') # メモリリークを起こしますのでメンバ変数として保持しないでください
            self.sigout = Port(array([])); self.sigout.link(scope.sigin)
            self.xrange = Port([0.,0.,0.]).bind(self._xrange)
            self.bplot  = Port(None).bind(self.calc)
            self.freq = 1.
        def calc(self):
            tim = scipy.arange(1000) / 100.
            omg = 2 * scipy.pi * self.freq * tim
            self.sigout.set(tim,scipy.sin(omg))
            self.freq = self.freq + .1
        def _xrange(self):
            try: self._xrange_called
            except AttributeError:
                self._xrange_called = True
                print self.xrange.get()
                self.xrange.set((2 * array(self.xrange.get())).tolist())
                del self._xrange_called
        class Plot(Tkinter.Frame):
            config = []
            def __init__(self,master=None,cnf={},**kw):
                Tkinter.Frame.__init__(self,master,cnf,**kw)
                gui.Layout.Embed(self,Oscilloscope,name='scope',text='Scope1').pack(side=Tkinter.LEFT)
                gui.Layout.Embed(self,Oscilloscope,name='scope2',text='Scope2').pack(side=Tkinter.LEFT)
            def assign(self,comp):
                self.children['scope'].assign(comp.children['scope'])
                w = self.children['scope2'].assign(Oscilloscope(comp)) # 生成を親コンポーネントに同期した無名のコンポーネントを生成する
                comp.sigout.link(w.comp().sigin)
        class Console(gui.Grid):
            def __init__(self,master=None,cnf={},**kw):
                gui.Grid.__init__(self,master,cnf,**kw)
                self.append(gui.MultipleEntries(self,name='xrange',column=3),label='Xrange')
                self.append(gui.Button(self,name='bplot',text='plot'))
            def assign(self,component):
                for name in ('xrange',):
                    getattr(component,name).link(self.children[name].value,set=True)
                for name in ('bplot',):
                    getattr(component,name).link(self.children[name].value)
        class Menu(gui.MenuFactory):
            def __init__(self,master=None,cnf={},**kw):
                desc = [['Component', ['Config', 'command']],
                        ['Children',  ['Oscilloscope', 'command'],
                                      ['Spectrum', 'command']]]
                gui.MenuFactory.__init__(self,master,desc,cnf,**kw)
                
    tk = Tkinter.Tk()
    a = MyComponent(core.Root())
    a1 = gui.Layout.Application(tk,a); a1.assign(a); a1.pack(); a1.master.title('master')
    a2 = gui.Layout.Application(Tkinter.Toplevel(tk),Oscilloscope(core.Root()),title='osc')
    a1.comp().sigout.link(a2.comp().sigin)
    Tkinter.mainloop()
    import gc
    a1 = weakref.ref(a1); gc.collect(); print 'a1:', a1
    a  = weakref.ref(a);  gc.collect(); print 'a :', a
    a2 = weakref.ref(a2); gc.collect(); print 'a2:', a2
    