# coding: utf-8

import Tkinter, gc
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
matplotlib.use('Agg',warn=False)
#matplotlib.rcParams['figure.facecolor'] = 'white'
#matplotlib.rcParams['figure.edgecolor'] = 'white'
#matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['font.size']   = 9.0

class Frame(Tkinter.Frame):
    '''
    軽量プロットウィジェット
    tkaggバックエンドでのメモリ解放に関する不具合を修正したプロッタ
    '''
    def __init__(self,master=None,figsize=(5,4),dpi=75,cnf={},**kw):
        Tkinter.Frame.__init__(self,master,cnf,**kw)
        self.figure = figure = Figure(figsize=figsize,dpi=dpi)
        # === make canvas object ===
        old = list(master.winfo_toplevel()._tclCommands) # tclコマンドを控える
        self.canvas = canvas = FigureCanvasTkAgg(figure,master=self) # ここでscroll_event_windowsとfilter_destroyがrootに追加される
        self._root_tclCommands = [] # destroy時に追加分だけ破棄するためのidを保持する
        for com in master.winfo_toplevel()._tclCommands:
            if old.count(com): continue
            self._root_tclCommands.append(com)
        # ===
        canvas.get_tk_widget().pack()
    def destroy_figure_canvas_axes(self):
        # rootにバインドされているイベントを削除する
        root = self.canvas._tkcanvas.winfo_toplevel()
        for name in self._root_tclCommands: root.deletecommand(name)
        # figureオブジェクトを削除する
        self.figure.clear() # 生成されているaxesオブジェクトをクリアする
        self.canvas.figure = None # FigureCanvasTkAggからの参照を削除する
        self.figure.figurePatch = None # Rectangleオブジェクトを削除して逆参照をクリアする
        self.figure.patch = None # Rectangleオブジェクトを削除して逆参照をクリアする
        self.figure = None # MPLFrameからの参照をクリアする
        # canvasオブジェクトを削除する
        self.canvas._tkcanvas.destroy(); self.canvas._tkcanvas = None # canvasからtkcanvasを破棄する
        for cid in range(self.canvas.callbacks._cid): self.canvas.mpl_disconnect(cid+1) # コールバックを削除する
        matplotlib.backend_bases.LocationEvent.lastevent = None # <- これはまだ必要かどうかわからない。クリックしたら解放されなくなるバグの修正
        self.canvas = None # MPLFrameからの参照をクリアする
        gc.collect()
    def destroy(self):
        self.destroy_figure_canvas_axes()
        Tkinter.Frame.destroy(self)

# class BasePlot(Frame):
# class Rectlinear(BasePlot): PROJECTION='rectlinear'
# class Polar(BasePlot): PROJECTION='polar'
class BasePlot(Frame):
    def __init__(self,master=None,figsize=(5,4),dpi=75,align=111,projection='rectilinear',cnf={},**kw):
        Frame.__init__(self,master,figsize,dpi,cnf,**kw)
        self.ax = self.figure.add_subplot(align,projection=projection) # １つの矩形プロットを追加する
    def resize(self,figsize=(5,4),dpi=75,align=111,projection='rectilinear'):
        self.destroy_figure_canvas_axes()
        self.figure = figure = Figure(figsize=figsize,dpi=dpi)
        self.canvas = canvas = FigureCanvasTkAgg(figure,master=self)
        #self.cid = self.canvas.mpl_connect('button_press_event',self._rclicked)
        canvas.get_tk_widget().pack()
        self.ax = self.figure.add_subplot(align,projection=projection)
    def _clear_lines(self): # axes.clear
        while len(self.ax.lines): # 残っているすべてのラインについて
            line = self.ax.lines[-1] # 最終ラインへの参照
            self.ax.lines.remove(line) # ラインの削除
            line._lineFunc = None # Line2Dの循環参照を解放する
            #line = weakref.ref(line); print line # オブジェクトが削除されたか確認するデバッグコード
            # === 削除しないで！ ===
            # ラインの解放にトラブルが発生したら以下のコードを試してみる
            # たとえば、スミスチャートの実装時などに問題がでるかも
            #for key,item in self.ax.xaxis.callbacks.callbacks['units'].items(): # コールバックを解除する
            #    if item == line.recache:
            #        del self.ax.xaxis.callbacks.callbacks['units'][key]
            #for key,item in self.ax.yaxis.callbacks.callbacks['units'].items(): # コールバックを解除する
            #    if item == line.recache:
            #        del self.ax.yaxis.callbacks.callbacks['units'][key]
            # ===================
        self.ax.ignore_existing_data_limits = True # dataLimをアップデートする
        self.ax._get_lines.set_color_cycle() # カラーサイクルを初期状態に戻す
    def _clear_patch(self):
        while len(self.ax.patches): # きちんとパッチが解放されることを確認した
            patch = self.ax.patches[-1]
            self.ax.patches.remove(patch)
    def clear(self):
        self._clear_lines()
        self._clear_patch()
#    def savefig(self):
#        fname = tkFileDialog.asksaveasfilename(title='Enter Filename')
#        self.ax.figure.savefig(fname)
#    def load(self):
#        from numpy import genfromtxt
#        fname = tkFileDialog.askopenfilename(title='Enter Filename')
#        data = genfromtxt(fname,delimiter=',').transpose()
#        self.sig_in.set(data)
    def destroy(self):
        self.ax = None
        Frame.destroy(self)
        
# ３次元についてはVTKを利用するかも
class ThreeD(Frame):
    def __init__(self,master=None,figsize=(5,4),dpi=75,align=111,cnf={},**kw):
        Frame.__init__(self,master,figsize,dpi,cnf,**kw)
        self.ax = self.figure.add_subplot(align,projection='rectilinear') # １つの矩形プロットを追加する
    def plot(self): pass
    def scatter(self): pass
    def wireframe(self): pass
    def surface(self): pass
    def destroy(self):
        self.ax = None
        Frame.destroy(self)
