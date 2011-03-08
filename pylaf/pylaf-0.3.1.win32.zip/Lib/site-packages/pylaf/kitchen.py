# coding: utf-8

import weakref, platform, random, uuid, inspect, imp, os
import Tkinter, tkFileDialog
import ttk #@UnresolvedImport
import core, gui, mpl

if platform.system() == 'Darwin':
    BUTTON_R = '<Button-2>'
else:
    BUTTON_R = '<Button-3>'

def classname(obj): return repr(obj.__class__).split('.')[-1].split(' ')[0]

def invoke_kitchen():
    Kitchen(Tkinter.Toplevel()).pack()

gui.MenuFactory.DEFAULT_ITEMS.insert(0,['PyLAF', ['Kitchen','command']])
gui.MenuFactory.DEFAULT_ASSIGNS.append([('pylaf',),0,invoke_kitchen])

def iscontain(obj,cls):
    try: bases = inspect.getmro(obj.__class__) # オブジェクトのクラスツリーをタプルで返す
    except AttributeError:
        return False
    if bases.count(cls):
        return True
    else:
        return False

class Sample(gui.ComponentWithGUI):
    class Console(gui.Grid):
        def __init__(self,master=None,cnf={},**kw):
            gui.Grid.__init__(self,master,cnf,**kw)
            self.append(gui.Entry(self,name='entry1'),label='Entry1')
            self.append(gui.Entry(self,name='entry2'),label='Entry2')
            self.counter = 0
            self.thread()
        def thread(self):
            self.counter = self.counter + 1
            print 'alive', self.counter
            self.after(1000,self.thread)

class SimpleDialog(Tkinter.Toplevel): pass

class ComponentChooser(ttk.Frame):
    def __init__(self,master=None,**kw):
        ttk.Frame.__init__(self,master,**kw)
        self.klass = {}
        self.selection = None
        ttk.Button(self,text='Load Module',command=self.select_module).grid(row=0,column=0)
        ttk.Treeview(self,name='klass').grid(row=1,column=0)
        ttk.Button(self,text='Select',command=self.made_decision).grid(row=2,column=0)
        #
        self.update()
        self.select_package()
        #
        self.pack()
        self.grab_set()
        self.focus_set()
        self.wait_window(self)
    def select_package(self,dir=os.getcwd()):
        selection = []
        for name in os.listdir(dir):
            if name.endswith('.py'):
                selection.append(name)
        self.parse_selection(selection)
    def select_module(self):
        # askopenfilename, askopenfilenames, askdirectory
        selection = tkFileDialog.askopenfilenames(initialdir=os.getcwd(),filetypes=[('python modules','*.py')])
        selection = list(selection)
        self.parse_selection(selection)
    def parse_selection(self,selection):
        item   = selection[0]
        path   = item.split('/')
        pyname = path[-1]
        cwd    = item.replace(pyname,'')
        names = []
        for item in selection:
            path = item.split('/')
            pyname = path[-1]
            if pyname.endswith('.py'):
                names.append(pyname.replace('.py',''))
        self.load_modules(*names,cwd=cwd)
    def load_modules(self,*names,**kw):
        cwd = None
        if kw:
            if kw.has_key('cwd'):
                cwd = kw['cwd']
        for name in names: self.load_module(name,cwd=cwd)
    def load_module(self,name,cwd=None):
        klass = {}
        try:
            if cwd:
                m = imp.load_module(name,*imp.find_module(name,[cwd]))
            else:
                m  = imp.load_module(name,*imp.find_module(name))
            self.update_by_module(m)
        except SyntaxError: print 'Syntax Error'
        except ImportError: print 'Import Error'
        except AttributeError: print 'Attribute Error'
    def made_decision(self):
        tv = self.children['klass']
        id = tv.selection()
        if len(id):
            self.selection = self.klass[id[0]]
        self.destroy()
    def update(self,modules=None):
        if not modules:
            modules = globals()
        for key in modules:
            self.update_by_module(modules[key])
    def update_by_module(self,module):
        if inspect.isclass(module):
            if self.iscomponent(module):
                self.add_item(module)
        if inspect.ismodule(module):
            components = self.extract_components(module)
            for component in components:
                self.add_item(component)
    def extract_components(self,module):
        components = []
        items = inspect.getmembers(module,lambda x:inspect.isclass(x))
        for key,cls in items:
            if self.iscomponent(cls):
                components.append(cls)
        return components
    def iscomponent(self,klass):
        family = inspect.getmro(klass)
        for c in family:
            name = repr(c).split()[1]
            if name == 'pylaf.core.Component' or name == 'core.Component':
                return True
        return False
    def add_item(self,cls):
        for id in self.klass:
            if self.klass[id] == cls:
                return
        tv = self.children['klass']
        path = repr(cls).split()[1].split('.')
        parent = ''
        for child in path[:-1]:
            flag = False
            for id in tv.get_children(parent):
                if child == tv.item(id)['text']:
                    flag = True
            if flag:
                parent = id
            else:
                parent = tv.insert(parent,'end',text=child)
        id = tv.insert(parent,'end',text=path[-1])
        self.klass[id] = cls
        
class ComponentTree(ttk.Treeview):
    class Menu(Tkinter.Menu):
        def __init__(self,master=None,cnf={},**kw):
            Tkinter.Menu.__init__(self,master,cnf,**kw)
            self.add_command(label='New Sibling',command=core.CallWrapper(master.newsibling))
            self.add_command(label='New Child',command=core.CallWrapper(master.newchild))
            self.add_command(label='Delete',command=core.CallWrapper(master.mydelete))
            self.add_separator()
            self.add_command(label='Set Export',command=core.CallWrapper(master.set_export))
            self.add_command(label='Reset Export',command=core.CallWrapper(master.reset_export))
    def __init__(self,master,**kw):
        ttk.Treeview.__init__(self,master,column=2,**kw)
        self.queue = []
        # ポップアップメニューの設定
        self.Menu(self,name='menu')
        self.bind(BUTTON_R, lambda e:self.children['menu'].tk_popup(e.x_root,e.y_root))
        #
        self.components = weakref.WeakValueDictionary()
        self.components[''] = core.Root()
        self.populate('',core.Root())
        #
        self.tag_configure('export',foreground='#0000FF')
        #
        self.loop()
    def set_export(self):
        id = self.myfocus()
        if not (id == '' or id == None):
            self.item(id,tag='export')
    def reset_export(self):
        id = self.myfocus()
        if not (id == '' or id == None):
            if self.item(id)['tags'].count('export'):
                tags = self.item(id)['tags']
                tags.remove('export')
                self.item(id,tags=tags)
    def loop(self):
        self.refresh()
        self.after(500,self.loop)
    def refresh(self):
        self.remove_item()
        self.populate('',core.Root())
        self.markup()
    def markup(self):
        for obj in self.queue:
            id = None
            for item in self.components:
                if obj == self.components[item]:
                    id = item
            if id:
                self.item(id,tag='export')
        self.queue = []
    def remove_item(self,item=None):
        # 幅方向優先削除
        # 削除候補の検索
        remove = []
        for key in self.get_children(item):
            if not self.components.has_key(key):
                remove.append(key)
        # 削除作業
        for key in remove:
            self.delete(key)
        # 深さ方向の処理
        for child in self.get_children(item):
            self.remove_item(child)
    def myfocus(self):
        item = self.selection()
        if    len(item) == 0: return ''
        elif  len(item) == 1: return item[0]
        else: return
    #def update(self):
    #    self.delete(*self.get_children())
    #    self.populate('',core.Root())
    def populate(self,node,component):
        parent = str(node)
        for key in component.children:
            c = component.children[key]
            children = self.get_children(parent)
            flag = False
            for child in children: # もし追加したいコンポーネントがあってもchildrenの中にすでに存在すれば追加しないでparentだけ更新する
                if c == self.components[child]:
                    flag = True
                    id = child
            if not flag:
                id = self.insert(parent,'end',text=classname(c),values=[key])
                self.components[id] = c
            self.populate(id,c)
    def newsibling(self):
        key = self.myfocus()
        if key == None: return
        key    = self.parent(key)
        parent = self.components[key]
        cc = ComponentChooser(Tkinter.Toplevel(self))
        cc.master.destroy()
        if cc.selection:
            self.queue.append(cc.selection(parent))
    def newchild(self):
        key = self.myfocus()
        if key == None: return
        parent = self.components[key]
        cc = ComponentChooser(Tkinter.Toplevel(self))
        cc.master.destroy()
        if cc.selection:
            self.queue.append(cc.selection(parent))
    def mydelete(self):
        key = self.myfocus()
        if key == None: return
        component = self.components[key]
        component.destroy()
        self.delete(key)

class WidgetTree(ttk.Treeview):
    class Menu(Tkinter.Menu):
        def __init__(self,master=None,cnf={},**kw):
            Tkinter.Menu.__init__(self,master,cnf,**kw)
            self.add_command(label='New Toplevel as Application',command=core.CallWrapper(master.newtoplevel))
            self.add_command(label='New Sibling as Embed',command=core.CallWrapper(master.newsibling))
            self.add_command(label='New Child as Embed',command=core.CallWrapper(master.newchild))
            self.add_command(label='Delete',command=core.CallWrapper(master.mydelete))
            self.add_separator()
            self.add_command(label='Refresh',command=core.CallWrapper(master.refresh))
    def __init__(self,master,**kw):
        ttk.Treeview.__init__(self,master,column=2,**kw)
        tk = self
        while tk.master: tk = tk.master
        self.widgets = weakref.WeakValueDictionary()
        self.widgets[''] = tk
        self.populate('',tk)
        # ポップアップメニューの設定
        self.Menu(self,name='menu')
        self.bind(BUTTON_R, lambda e:self.children['menu'].tk_popup(e.x_root,e.y_root))
        self.loop()
    def loop(self):
        self.refresh()
        self.after(500,self.loop)
    def populate(self,node,widget):
        parent = str(node)
        for key in widget.children:
            # Kitchenを表示しない
            #flag = False
            #for mykey in component.children[key].children:
            #    if classname(component.children[key].children[mykey]) == 'Kitchen':
            #        flag = True
            #        break
            #if flag: return
            #
            c = widget.children[key]
            children = self.get_children(parent)
            flag = False
            for child in children: # もし追加したいコンポーネントがあってもchildrenの中にすでに存在すれば追加しないでparentだけ更新する
                if c == self.widgets[child]:
                    flag = True
                    id = child
            if not flag:
                id = self.insert(parent,'end',text=classname(c),values=[key])
                self.widgets[id] = c
            self.populate(id,c)
    def refresh(self):
        tk = self
        while tk.master: tk = tk.master
        self.remove_item()
        self.populate('',tk)
    def remove_item(self,item=None):
        # 幅方向優先削除
        # 削除候補の検索
        remove = []
        for key in self.get_children(item):
            if not self.widgets.has_key(key):
                remove.append(key)
        # 削除作業
        for key in remove:
            self.delete(key)
        # 深さ方向の処理
        for child in self.get_children(item):
            self.remove_item(child)
    def myfocus(self):
        item = self.selection()
        if    len(item) == 0: return ''
        elif  len(item) == 1: return item[0]
        else: return
    def newtoplevel(self):
        component = self.master.focus()
        if component == None: return
        key    = ''
        parent = self.widgets[key]
        top    = Tkinter.Toplevel(parent)
        gui.Layout.Application(top,component)
        item   = self.insert(key,'end',text=classname(top),values=[repr(id(top))])
        self.widgets[item] = top
        self.populate(item,top)
    def newsibling(self): pass
    def newchild(self): pass
    def mydelete(self): pass

class CanvasItem:
    STATE_NORMAL, STATE_HIGHLIGHT = range(2)
    def __init__(self,canvas,cid,x,y,**kw):
        self.tag     = tag = str(uuid.uuid4())
        self.canvas  = weakref.ref(canvas)
        self.cid     = cid
        self.x       = x
        self.y       = y
        self.state   = CanvasItem.STATE_NORMAL
        self.outline = canvas.create_rectangle(x-50,y-20,x+50,y+20,width=2,fill='#FFFFF0',tag=tag)
        self.label   = canvas.create_text(x,y,text=self.format(cid),tag=tag)
        canvas.tag_bind(tag,'<Button-1>', self.buttonpress1)
        canvas.tag_bind(tag,'<ButtonRelease-1>', self.buttonrelease1)
        canvas.tag_bind(tag,'<Button1-Motion>', self.buttonmotion1)
    def locate(self):
        x0, y0, x1, y1 = self.canvas().bbox(self.outline)
        return (x0 + x1) / 2., (y0 + y1) / 2.
    def iscontain(self,item):
        return self.outline == item or self.label == item
    def highlight(self):
        if self.state == CanvasItem.STATE_HIGHLIGHT: return
        self.state = CanvasItem.STATE_HIGHLIGHT
        self.canvas().itemconfig(self.outline,width=3)
    def lift(self):
        self.canvas().lift(self.outline)
        self.canvas().lift(self.label)
    def normal(self):
        if self.state == CanvasItem.STATE_NORMAL: return
        self.state = CanvasItem.STATE_NORMAL
        self.canvas().itemconfig(self.outline,width=2)
    def mode_wire(self):
        self.canvas().mode_wire(self)
        self.highlight()
    def buttonpress1(self,e):
        self.x0, self.y0 = e.x, e.y
        self.aid = self.canvas().after(1500,self.mode_wire)
    def buttonrelease1(self,e):
        if   self.canvas().is_wire():
            self.canvas().link()
            self.canvas().mode_move()
        elif self.canvas().is_move():
            self.canvas().after_cancel(self.aid)
    def buttonmotion1(self,e):
        self.lift()
        self.canvas().after_cancel(self.aid)
        if   self.canvas().is_move(): self.move(e)
        elif self.canvas().is_wire(): self.canvas().dragging_wire(e)
    def move(self,e):
        canvas = self.canvas()
        x1, y1 = e.x, e.y
        dx, dy = x1 - self.x0, y1 - self.y0
        canvas.move(self.outline, dx, dy)
        canvas.move(self.label,   dx, dy)
        self.x, self.y = self.x + dx, self.y + dy
        self.x0, self.y0 = x1, y1
        canvas.move_wire(self,dx,dy)
    def format(self,cid):
        if cid == '':
            cname  = 'Root'
            name   = ''
        else:
            canvas = self.canvas()
            cname  = classname(canvas.components()[cid])
            name   = canvas.components()[cid]._name
        return '%s\n%s' % (name,cname)
    def delete(self):
        self.canvas().delete(self.tag)

class CanvasLine:
    def __init__(self,canvas,terminals):
        self.terminals = terminals
        self.canvas    = weakref.ref(canvas)
        self.bx, self.by = terminals[0].locate()
        self.ex, self.ey = terminals[1].locate()
        self.draw()
        canvas.tag_bind(self.lid,'<ButtonPress-1>', self.buttonpress1)
        canvas.tag_bind(self.lid,'<Enter>', self.enter)
        canvas.tag_bind(self.lid,'<Leave>', self.leave)
    def buttonpress1(self,e):
        components = self.canvas().components()
        terminals = (components[self.terminals[0].cid],components[self.terminals[1].cid])
        self.canvas().popup_linker(terminals)
    def enter(self,e):
        components = self.canvas().components()
        self.canvas().itemconfig(self.lid,width=2)
        terminals = (components[self.terminals[0].cid],components[self.terminals[1].cid])
        self.canvas().show_links(terminals)
    def leave(self,e):
        self.canvas().itemconfig(self.lid,width=1)
        self.canvas().hide_links()
    def eq(self,terminals):
        t1, t2 = terminals
        myt1, myt2 = self.terminals
        return (t1 == myt1 and t2 == myt2) or (t1 == myt2 and t2 == myt1)
    def move(self):
        bx, by = self.terminals[0].locate()
        ex, ey = self.terminals[1].locate()
        if self.bx == bx and self.by == by and self.ex == ex and self.ey == ey: return
        self.bx, self.by, self.ex, self.ey = bx, by, ex, ey
        self.delete()
        self.draw()
    def draw(self):
        self.lid = self.canvas().create_line(self.bx, self.by, self.ex, self.ey)
        self.canvas().lower(self.lid)
    def delete(self):
        self.canvas().delete(self.lid)
    
class ComponentLabel(Tkinter.Label):
    def __init__(self,master,component=None,cnf={},**kw):
        Tkinter.Label.__init__(self,master,cnf,**kw)
        if component:
            self.insert(component)
        else:
            self.delete()
    def delete(self):
        self.configure(text=' \n ')
    def insert(self,component):
        self.configure(text='%s\n%s' % (component._name,classname(component)))

class LinkViewer(Tkinter.Listbox):
    def __init__(self,master,withlabel=False,cnf={},**kw):
        frame = Tkinter.Frame(master)
        self.withlabel = withlabel
        if withlabel:
            lentry = ComponentLabel(frame)
            rentry = ComponentLabel(frame)
            self.lentry = weakref.ref(lentry)
            self.rentry = weakref.ref(rentry)
        Tkinter.Listbox.__init__(self,frame,cnf,**kw)
        if kw:
            if kw.has_key('name'):
                del kw['name']
        right = Tkinter.Listbox(frame,cnf,**kw)
        #
        self.frame = weakref.ref(frame)
        self.right = weakref.ref(right)
    def activate(self,terminals):
        pairs = self.pairs(terminals)
        lpairs = [pair[0] for pair in pairs]
        rpairs = [pair[1] for pair in pairs]
        self.delete(0,Tkinter.END)
        self.insert(Tkinter.END,*lpairs)
        self.right().delete(0,Tkinter.END)
        self.right().insert(Tkinter.END,*rpairs)
        if self.withlabel:
            self.lentry().insert(terminals[0])
            self.rentry().insert(terminals[1])
    def deactivate(self):
        self.delete(0,Tkinter.END)
        self.right().delete(0,Tkinter.END)
        if self.withlabel:
            self.lentry().delete()
            self.rentry().delete()
    def pairs(self,terminals):
        pairs = []
        # terminalに含まれるストレージのリストを生成
        storages = {}
        for terminal in terminals:
            m = inspect.getmembers(terminal,lambda x:iscontain(x,core.Port))
            for name, port in m:
                if not storages.has_key(port.subject):
                    storages[port.subject] = [(terminal,name)]
                else:
                    storages[port.subject].append((terminal,name))
        # 監視ポートがただひとつならばラインデータベースから削除
        removable = []
        for sid in storages:
            portlist = storages[sid]
            if len(portlist) == 1:
                removable.append(sid)
        for sid in removable:
            del storages[sid]
        # pairを生成する
        for sid in storages:
            links = self.pairing(terminals,storages[sid])
            for item in links:
                pairs.append(item)
        return pairs
    def pairing(self,terminals,ports):
        def select(component,ports):
            result = []
            for c, name in ports:
                if c == component:
                    result.append(name)
            return result
        portsa = select(terminals[0],ports)
        portsb = select(terminals[1],ports)
        links = []
        for namea in portsa:
            for nameb in portsb:
                links.append((namea,nameb))
        return links
    def grid(self,**kw):
        self.frame().grid(**kw)
        self.layout()
    def pack(self,**kw):
        self.frame().pack(**kw)
        self.layout()
    def layout(self):
        if self.withlabel:
            self.lentry().grid(row=0,column=0)
            self.rentry().grid(row=0,column=1)
        Tkinter.Listbox.grid(self,row=1,column=0)
        self.right().grid(row=1,column=1)
    def lselection(self):
        selection = self.curselection()
        if not len(selection): return
        return self.get(0,Tkinter.END)[int(selection[0])]
    def rselection(self):
        selection = self.right().curselection()
        if not len(selection): return
        return self.right().get(0,Tkinter.END)[int(selection[0])]

class Linker(Tkinter.Frame):
    class PortPicker(Tkinter.Listbox):
        def __init__(self,master,entry,component,cnf={},**kw):
            Tkinter.Listbox.__init__(self,master,cnf,**kw)
            m = inspect.getmembers(component,lambda x:iscontain(x,core.Port))
            entry.delete(0,Tkinter.END)
            self.insert(Tkinter.END, *[name for name, port in m])
            self.bind('<ButtonRelease-1>',self.selection)
            self.entry = weakref.ref(entry)
        def selection(self,e):
            curselection = self.curselection()
            if not len(curselection): return
            name = Tkinter.Listbox.get(self,0,Tkinter.END)[int(curselection[0])]
            entry = self.entry()
            entry.delete(0,Tkinter.END)
            entry.insert(0,name)
    def __init__(self,master,terminals,cnf={},**kw):
        Tkinter.Frame.__init__(self,master,cnf,**kw)
        self.master.title('Linker: PyLAF Kitchen')
        a, b = terminals
        ComponentLabel(self,a).grid(row=0,column=0)
        pickera = Tkinter.Entry(self); pickera.grid(row=1,column=0)
        Linker.PortPicker(self,pickera,a).grid(row=2,column=0)
        cframe = Tkinter.Frame(self,name='cframe'); cframe.grid(row=1,column=1)
        Tkinter.Button(cframe,text='unlink',command=self.unlinka).grid(row=0,column=0)
        Tkinter.Button(cframe,text='<',command=self.alinkb).grid(row=0,column=1)
        Tkinter.Button(cframe,text='>',command=self.blinka).grid(row=0,column=2)
        Tkinter.Button(cframe,text='unlink',command=self.unlinkb).grid(row=0,column=3)
        linkviewer = LinkViewer(self); linkviewer.grid(row=2,column=1)
        ComponentLabel(self,b).grid(row=0,column=2)
        pickerb = Tkinter.Entry(self); pickerb.grid(row=1,column=2)
        Linker.PortPicker(self,pickerb,b).grid(row=2,column=2)
        #
        linkviewer.activate(terminals)
        #
        self.a = weakref.ref(a)
        self.b = weakref.ref(b)
        self.pickera = weakref.ref(pickera)
        self.pickerb = weakref.ref(pickerb)
        self.linkviewer = weakref.ref(linkviewer)
    def alinkb(self):
        pa = self.pickera().get()
        pb = self.pickerb().get()
        try:
            getattr(self.a(),pa).link(getattr(self.b(),pb))
            self.master.destroy()
        except AttributeError: pass
    def blinka(self):
        pa = self.pickera().get()
        pb = self.pickerb().get()
        try:
            getattr(self.b(),pb).link(getattr(self.a(),pa))
            self.master.destroy()
        except AttributeError: pass
    def unlinka(self):
        name = self.linkviewer().lselection()
        if name:
            getattr(self.a(),name).unlink()
        self.linkviewer().deactivate()
        self.linkviewer().activate((self.a(),self.b()))
    def unlinkb(self):
        name = self.linkviewer().rselection()
        if name:
            getattr(self.b(),name).unlink()
        self.linkviewer().deactivate()
        self.linkviewer().activate((self.a(),self.b()))
    def components(self):
        return self.master.master.components()

class CollaborationMap(Tkinter.Canvas):
    MODE_MOVE, MODE_WIRE = range(2)
    def __init__(self,master,cnf={},**kw):
        Tkinter.Canvas.__init__(self,master,cnf,**kw)
        self.items = weakref.WeakValueDictionary()
        self.lines = []
        self.mode  = CollaborationMap.MODE_MOVE
        self.bitem = None
        self.eitem = None
        self.loop()
    def loop(self):
        self.refresh()
        self.after(500,self.loop)
    def components(self): return self.master.components()
    def show_links(self,terminals): self.master.show_links(terminals)
    def hide_links(self): self.master.hide_links()
    def popup_linker(self,terminals):
        Linker(Tkinter.Toplevel(self),terminals).pack()
    def mode_wire(self,sender):
        self.mode = CollaborationMap.MODE_WIRE
        for cid in self.items:
            if self.items[cid] == sender:
                self.bitem = cid
    def mode_move(self):
        self.mode = CollaborationMap.MODE_MOVE
        for cid in self.items:
            self.items[cid].normal()
        self.bitem, self.eitem = None, None
    def is_wire(self): return self.mode == CollaborationMap.MODE_WIRE
    def is_move(self): return self.mode == CollaborationMap.MODE_MOVE
    def dragging_wire(self,e):
        id = self.find_closest(e.x,e.y)[0]
        for cid in self.items:
            item = self.items[cid]
            if item.iscontain(id):
                if cid == self.bitem:
                    self.eitem = None
                    continue
                else:
                    self.eitem = cid
                    item.highlight()
            else:
                if not cid == self.bitem:
                    item.normal()
    def link(self):
        if self.bitem == None or self.eitem == None: return
        components = self.components()
        b, e = components[self.bitem], components[self.eitem]
        #b.entry4.link(e.entry4)
        Linker(Tkinter.Toplevel(self),(b,e)).pack()
    def move_wire(self,item,dx,dy):
        for line in self.lines:
            line.move()
    def refresh(self):
        components = self.components()
        # remove obsolete items
        items = self.items.keys()
        for cid in components:
            if items.count(cid):
                items.remove(cid)
        for cid in items:
            self.items[cid].delete()
        # append new items
        items = []
        for cid in components:
            if not self.items.has_key(cid):
                item = CanvasItem(self,cid,200*random.random()+100,200*random.random()+50)
                self.items[cid] = item
        #
        #
        #
        # ストレージの全リストとそれを監視しているポートを２つ以上保持しているコンポーネントとポート名のデータベースの生成
        storages = {} # コンポーネントやストレージへの参照を含むのでメンバとして保持しちゃだめ
        for cid in components:
            c = components[cid]
            m = inspect.getmembers(c,lambda x:iscontain(x,core.Port))
            for name, port in m:
                if not storages.has_key(port.subject):
                    storages[port.subject] = [(c,name)]
                else:
                    storages[port.subject].append((c,name))
        #
        removable = []
        for sid in storages:
            portlist = storages[sid]
            # 監視ポートがただひとつならばラインデータベースから削除
            if len(portlist) == 1:
                removable.append(sid)
        for sid in removable:
            del storages[sid]
        #
        removable = []
        for sid in storages:
            portlist = storages[sid]
            # 単一の監視コンポーネントの複数のポートから参照されている場合も削除
            # !!! 現状ではラインの表現方法を決めてないが、将来はこれにも対応すること !!!
            component = portlist[0]
            if portlist.count(component) == len(portlist):
                removable.append(sid)
        for sid in removable:
            del storages[sid]
        # 関連したコンポーネント対のリストを生成（順不同は同一とみなす）
        def pairs(o,clist):
            tmpclist = list(clist)
            last     = tmpclist.pop(0) # 先頭の要素を取り出し
            for c in tmpclist:
                flag = False
                for item in o:
                    if (item[0] == c and item[1] == last) or\
                       (item[0] == last and item[1] == c):
                        flag = True
                if not flag:
                    o.append((last,c))
            if len(tmpclist):
                pairs(o,tmpclist)
        links = []
        for sid in storages:
            plist = storages[sid]
            clist = [p[0] for p in plist]
            pairs(links,clist)
        cids = {}
        for cid in components:
            cids[components[cid]] = cid
        linksbycid = []
        for pair in links:
            linksbycid.append((cids[pair[0]],cids[pair[1]]))
        # ラインの削除
        removable = []
        for line in self.lines:
            flag = False
            for pair in linksbycid:
                if line.eq(pair):
                    flag = True
            if not flag:
                removable.append(line)
        for line in removable:
            self.lines.remove(line)
            line.delete()
        # ラインの描画
        for pair in linksbycid:
            pair = (self.items[pair[0]],self.items[pair[1]])
            flag = False
            for line in self.lines: # すでに描画してあるペアか検査して
                if line.eq(pair):
                    flag = True
            if not flag: # まだ描画していなければ描画する
                self.lines.append(CanvasLine(self,pair))

class Kitchen(Tkinter.Frame):
    def __init__(self,master,cnf={},**kw):
        Tkinter.Frame.__init__(self,master,cnf,**kw)
        self.master.title('PyLAF Kitchen')
        tab = ttk.Notebook(self,name='tabpane'); tab.grid(row=1,column=0)
        tab.add(ComponentTree(self,name='componenttree'),text='Components')
        tab.add(WidgetTree(self,name='widgettree'),text='Widgets')
        CollaborationMap(self,name='collaborationmap',width=640,height=400).grid(row=0,column=0,columnspan=2)
        linkviewer = LinkViewer(self,withlabel=True); linkviewer.grid(row=1,column=1)
        self.linkviewer = weakref.ref(linkviewer)
    def focus(self):
        item = self.children['componenttree'].myfocus()
        if item == None or item == '': return
        return self.children['componenttree'].components[item]
    def components(self):
        return self.children['componenttree'].components
    def show_links(self,terminals):
        self.linkviewer().activate(terminals)
    def hide_links(self):
        self.linkviewer().deactivate()

if __name__ == '__main__':
    import gui
    class MyComponent(gui.ComponentWithGUI):
        class Console(gui.Grid):
            def __init__(self,master=None,cnf={},**kw):
                gui.Grid.__init__(self,master,cnf,**kw)
                self.append(gui.Entry(self,name='entry1'),label='Entry1')
        class Menu(gui.MenuFactory):
            DESC = [['PyLAF', ['Kitchen', 'command']],]
            def __init__(self,master=None,cnf={},**kw):
                gui.MenuFactory.__init__(self,master,self.DESC,cnf,**kw)
            def assign(self,comp):
                self.children['pylaf'].assign('kitchen',self.invoke_kitchen)
            def invoke_kitchen(self):
                tk = self
                while tk.master: tk = tk.master
                Kitchen(Tkinter.Toplevel(tk)).pack()
        def __init__(self,master=None,name=None):
            gui.ComponentWithGUI.__init__(self,master,name)
            self.entry1 = core.Port(0.)
            self.entry2 = core.Port(0.)
            self.entry3 = core.Port(0.)
            self.entry4 = core.Port(0.)
    
    tk = Tkinter.Tk()
    basic = gui.Layout.Application(tk,MyComponent(core.Root()),title='basic sample')
    c = basic.comp()
    my   = MyComponent(core.Root(),name='component')
    my1  = MyComponent(c,name='component1')
    my2  = MyComponent(c,name='component2')
    my11 = MyComponent(c.children['component1'],name='component11')
    my.entry1.link(my1.entry1)
    my.entry2.link(my1.entry2)
    my.entry1.link(my2.entry1)
    del my, my1, my2, my11
    Tkinter.mainloop()
    