# coding: utf-8

import inspect, types, platform, numpy, scipy
import Tkinter
import ttk #@UnresolvedImport
import vtk #@UnresolvedImport
from vtk.tk.vtkTkRenderWidget import vtkTkRenderWidget #@UnresolvedImport
from vtk.util import numpy_support #@UnresolvedImport
from vtk.util.numpy_support import numpy_to_vtk #@UnresolvedImport
from core import Component, Port, isPort
from gui  import Console, Panel, Standard

BUTTON_L = '<Button-1>'
if platform.system() == 'Darwin':
    BUTTON_R = '<Button-2>'
else:
    BUTTON_R = '<Button-3>'

def classname(obj):
    cname = repr(obj.__class__).split('.')[-1].split(' ')[0]
    if cname == '<type': cname = 'None'
    return cname
    
class RenderWidget(vtkTkRenderWidget):
    def __init__(self,*args,**kw):
        vtkTkRenderWidget.__init__(self,*args,**kw)
        self.dataset = {}
        self.volume  = {}
        self.actor   = {}
        render = vtk.vtkRenderer()
        render.SetBackground(1,1,1)
        self.GetRenderWindow().AddRenderer(render)
    def AddDataSet(self,dataset,name=None):
        if name == None: name = repr(id(dataset))
        self.dataset[name] = dataset
    def AddVolume(self,volume,name=None):
        if name == None: name = repr(id(volume))
        self.GetRenderWindow().GetRenderers().GetFirstRenderer().AddVolume(volume)
        self.volume[name] = volume
    def AddActor(self,actor,name=None):
        if name == None: name = repr(id(actor))
        self.GetRenderWindow().GetRenderers().GetFirstRenderer().AddActor(actor)
        self.actor[name] = actor
    def Render(self):
        for key in self.dataset: self.dataset[key]._sigin()
        self.GetRenderWindow().Render()
    def ResetCamera(self):
        self.GetRenderWindow().GetRenderers().GetFirstRenderer().ResetCamera()
        
class PortView(ttk.Treeview):
    def __init__(self,master=None,**kw):
        ttk.Treeview.__init__(self,master,**kw)
        self.ports = {}
        self.loop()
    def loop(self):
        self.populate()
        self.after(500,self.loop)
    def populate(self,parent=''):
        try: self.component
        except AttributeError: return
        ports = inspect.getmembers(self.component,isPort)
        my = [k for k in self.ports]
        other = [o for k,o in ports]
        for port in my:
            if not other.count(port):
                self.delete(self.ports[port][0])
        for name, port in ports:
            cname = classname(port.subject.value)
            if not self.ports.has_key(port):
                label = '%s(%s)' % (name,cname)
                id = self.insert(parent,'end',text=label)
                self.ports[port] = (id,name,cname)
            id, name, mycname = self.ports[port]
            if not mycname == cname:
                self.item(id,text='%s(%s)' % (name,cname))
                self.ports[port] = (id,name,cname)
    def config(self,component=None,**kw):
        if not component == None: self.component = component
        ttk.Treeview.config(self,**kw)
        

class ModelView(ttk.Treeview):
    class Menu(Tkinter.Menu):
        def __init__(self,master=None,cnf={},**kw):
            Tkinter.Menu.__init__(self,master,cnf,**kw)
            self.add_command(label='Property',command=master.popup_property)
    def __init__(self,master=None,name=None,**kw):
        ttk.Treeview.__init__(self,master,name=name)
        self.Menu(self,name='menu')
        self.bind(BUTTON_R, self.popup_menu)
        self.config(**kw)
        self.loop()
    def popup_menu(self,e):
        # TODO: ここにコンテキストメニューの制御コードを入れる
        return self.children['menu'].tk_popup(e.x_root,e.y_root)
    def myselection(self):
        item = self.selection()
        if    len(item) == 0: return ''
        elif  len(item) == 1: return item[0]
        else: return
    def popup_property(self):
        tag = self.myselection()
        if tag == None: return
        model = self.get_instance(tag)
        if model == None: return
        if self.number_available_ports(model) == 0: return
        Console(Tkinter.Toplevel(self),model,Standard,sync=False)
    def get_instance(self,tag):
        if tag == '': return # トップレベルならば None を返す
        parent_tag = self.parent(tag)
        if parent_tag == '': return self.get_dataset(tag)
        dataset      = self.get_dataset(parent_tag)
        target_cname = self.item(tag)['text']
        for name in dataset.children:
            model = dataset.children[name]
            if target_cname == classname(model): break
        return model
    def get_dataset(self,tag): # 対応するデータセットを取得する
        name = self.parse(self.item(tag)['text'])[0]
        return self.RenderWidget.dataset[name]
    def number_available_ports(self,instance):
        counter = 0
        members = inspect.getmembers(instance,isPort)
        for key,port in members:
            value = port.subject.value
            if (
                type(value) == types.NoneType or
                type(value) == types.InstanceType or
                type(value) == numpy.ndarray
                ): continue
            counter += 1
        return counter
    def loop(self):
        self.populate()
        self.after(500,self.loop)
    def parse(self,text):
        name,cname = text.split('(')
        cname = cname[:-1]
        return name, cname
    def populate(self):
        try: self.RenderWidget
        except AttributeError: return
        ROOT, datasets = '', self.RenderWidget.dataset
        source = [k for k in datasets]
        existing = {}
        for id in self.get_children(ROOT):
            name, cname = self.parse(self.item(id)['text'])
            existing[name] = (id,cname)
        for name in source:
            dataset = datasets[name]
            cname   = classname(dataset)
            if not existing.has_key(name):
                label    = '%s(%s)' % (name,cname)
                id       = self.insert(ROOT,'end',text=label)
                existing[name] = (id,cname)
            id, excname = existing[name]
            if not excname == cname:
                self.item(id,text='%s(%s)' % (name,cname))
            self.populate_actor(id)
    def populate_actor(self,parent):
        name, cname = self.parse(self.item(parent)['text'])
        dataset     = self.RenderWidget.dataset[name]
        existing    = {}
        for id in self.get_children(parent):
            cname = self.item(id)['text']
            existing[cname] = id
        for name in dataset.children:
            model = dataset.children[name]
            cname = classname(model)
            if not existing.has_key(cname):
                id = self.insert(parent,'end',text=cname)
    def config(self,RenderWidget=None,**kw):
        if not RenderWidget == None: self.RenderWidget = RenderWidget
        ttk.Treeview.config(self,**kw)

class VtkView(Component):
    class Plot(Panel):
        def __init__(self,master=None,cnf={},**kw):
            Panel.__init__(self,master,cnf,**kw)
            renderWidget = RenderWidget(self,name='renderwidget')
            renderWidget.grid(sticky=Tkinter.E+Tkinter.W+Tkinter.S+Tkinter.N)
            Tkinter.Button(self,text='ResetCamera',command=self.resetcamera).grid(sticky=Tkinter.W+Tkinter.E)
            self.grid_columnconfigure(0,weight=1)
            self.grid_rowconfigure(0,weight=1)
            self.grid_rowconfigure(1,weight=0)
        def render(self):
            self.RenderWidget().Render()
        def resetcamera(self):
            self.RenderWidget().ResetCamera()
        def RenderWidget(self):
            return self.children['renderwidget']
        def AddPort(self,name):
            if [k for k,v in inspect.getmembers(self)].count(name): return
            g, c = Port(None).bind(self.render), Port(None)
            setattr(self,name,g)
            setattr(self.component(),name,c)
            c.link(g)
    class Control(Panel):
        def __init__(self,master=None,cnf={},**kw):
            Panel.__init__(self,master,cnf,**kw)
            PortView(self,name='port').grid()
            ModelView(self,name='model').grid()
        def assign(self,component):
            Panel.assign(self,component)
            self.children['port'].config(component=component)
            self.children['model'].config(RenderWidget=self.sibling('plot').RenderWidget())
            
class RayCastVolume(vtk.vtkVolume):
    def _label(self):
        print self.label.get()
    def __init__(self,**kw):
        self.label = Port('Unnamed').bind(self._label)
        mapper = vtk.vtkVolumeRayCastMapper()
        mapper.SetVolumeRayCastFunction(vtk.vtkVolumeRayCastCompositeFunction())
        #
        alphaChannelFunc = vtk.vtkPiecewiseFunction()
        alphaChannelFunc.AddPoint(  0, 0.0)
        #alphaChannelFunc.AddPoint(127, 0.4)
        alphaChannelFunc.AddPoint(255, 0.4)
        #
        colorFunc = vtk.vtkColorTransferFunction()
        colorFunc.AddRGBPoint(  0,0.,0.,1.)
        colorFunc.AddRGBPoint(127,0.,1.,0.)
        colorFunc.AddRGBPoint(255,1.,0.,0.)
        #
        property = vtk.vtkVolumeProperty()
        property.SetColor(colorFunc)
        property.SetScalarOpacity(alphaChannelFunc)
        #
        self.SetMapper(mapper)
        self.SetProperty(property)
        self.config(**kw)
    def config(self,**kw):
        if kw == None: return
        if kw.has_key('Input'):
            input = kw['Input']
            input.children[repr(id(self))] = self
            self.GetMapper().SetInput(kw['Input'])
        
class OutlineActor(vtk.vtkActor):
    def __init__(self,**kw):
        self.filter = filter = vtk.vtkOutlineFilter()
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(filter.GetOutputPort())
        self.SetMapper(mapper)
        self.config(**kw)
    def config(self,**kw):
        if kw == None: return
        if kw.has_key('Color'): self.GetProperty().SetColor(kw['Color'])
        if kw.has_key('Input'):
            input = kw['Input']
            input.children[repr(id(self))] = self
            self.filter.SetInput(input)
            
class UIntScalarStructuredPoints(vtk.vtkStructuredPoints):
    def __init__(self,**kw):
        self.children  = {}
        self.buffer    = buffer = numpy.zeros((0,0,0),dtype=numpy.uint8)
        self.sigin     = Port(buffer)
        self.olddataid = id(buffer)
        self.range     = (0.,1.)
        self.rmin      = Port(self.range[0])
        self.rmax      = Port(self.range[1])
        self.reset()
        self.config(**kw)
    def _sigin(self):
        newdata = self.sigin.get()
        if newdata == None: return
        if not self.olddataid == id(newdata): self.reset()
        buffer = self.update(newdata)
        # スケーリング
        #min, max = self.range
        min, max = self.rmin.get(), self.rmax.get()
        scipy.clip(buffer,min,max,out=buffer)
        self.buffer[:,:,:] = (255 * ((buffer + min)/max)).astype(self.buffer.dtype)
    def reset(self):
        data           = self.sigin.get()
        self.olddataid = id(data)
        z, y, x        = data.shape
        self.buffer   = numpy.zeros((z, y, x),dtype=self.buffer.dtype)
        nparray        = numpy_support.numpy_to_vtk(self.buffer.reshape(z * y * x))
        self.SetDimensions(x,y,z)
        self.SetScalarTypeToUnsignedShort()
        self.GetPointData().SetScalars(nparray)
    def config(self,**kw):
        if kw == None: return
        if kw.has_key('Spacing'): self.SetSpacing(kw['Spacing'])
        if kw.has_key('Range'):
            self.range = tuple(kw['Range'])
            self.rmin.set(self.range[0])
            self.rmax.set(self.range[1])
    # カスタマイズ
    def update(self,data):
        return data.copy()
        
class StructuredPoints(vtk.vtkStructuredPoints):
    def __init__(self,**kw):
        self.children   = {}
        self.vectorData = numpy.zeros((0,0,0,3),dtype=numpy.float64)
        self.scalarData = numpy.zeros((0,0,0),dtype=numpy.float64)
        self.olddataid  = id(self.vectorData)
        self.sigin      = Port(self.vectorData)#.bind(self._sigin)
        self.reset()
        self.config(**kw)
    def _sigin(self):
        newdata = self.sigin.get()
        if newdata == None: return
        if not self.olddataid == id(newdata): self.reset()
        self.update_vectors(self.vectorData,newdata)
        self.update_scalars()
        z, y, x, c = self.vectorData.shape
        self.GetPointData().SetVectors(numpy_support.numpy_to_vtk(self.vectorData.reshape(z * y * x, c)))
        self.GetPointData().SetScalars(numpy_support.numpy_to_vtk(self.scalarData.reshape(z * y * x)))
    def update_scalars(self):
        c = self.vectorData.shape[3]
        self.scalarData[:,:,:] = self.vectorData[:,:,:,0] ** 2
        for l in range(1,c):
            self.scalarData[:,:,:] += (self.vectorData[:,:,:,l] ** 2)
        self.scalarData[:,:,:] = numpy.sqrt(self.scalarData)
    def reset(self):
        data            = self.sigin.get()
        self.olddataid  = id(data)
        z, y, x, c      = self.shape(data)
        self.vectorData = numpy.zeros((z, y, x, c), dtype=numpy.float64)
        self.scalarData = numpy.zeros((z, y, x),    dtype=numpy.float64)
        self.SetDimensions(x, y, z)
        self.SetNumberOfScalarComponents(c)
    def config(self,**kw):
        if kw == None: return
        if kw.has_key('Spacing'): self.SetSpacing(kw['Spacing'])
    # カスタマイズ項目
    def update_vectors(self,vector,data):
        vector[:,:,:,:] = data
    def shape(self,data): return data.shape
        
class HedgeHog(vtk.vtkActor):
    def __init__(self,**kw):
        hedgehog    = vtk.vtkHedgeHog()
        lookuptable = vtk.vtkLookupTable()
        mapper      = vtk.vtkPolyDataMapper()
        mapper.SetLookupTable(lookuptable)
        mapper.SetInputConnection(hedgehog.GetOutputPort())
        mapper.ScalarVisibilityOn()
        #hhogMapper.SetScalarRange(0.,.01)
        #
        self.SetMapper(mapper)
        self.hedgehog = hedgehog
        self.config(**kw)
    def config(self,**kw):
        if kw == None: return
        if kw.has_key('ScaleFactor'): self.hedgehog.SetScaleFactor(kw['ScaleFactor'])
        if kw.has_key('ScalarRange'): self.GetMapper().SetScalarRange(kw['ScalarRange'])
        if kw.has_key('Input'):
            input = kw['Input']
            input.children[repr(id(self))] = self
            self.hedgehog.SetInput(input)
        #self.SetScalarRange(dataset.GetScalarRange())
        
