
import wx
import wx.glcanvas 

import pomsets_app.gui.canvas as CanvasModule

class Canvas(wx.glcanvas.GLCanvas, CanvasModule.Canvas):


    def __init__(self, parent, *args, **kwds):

        attribList = (
            wx.glcanvas.WX_GL_DOUBLEBUFFER,
            wx.glcanvas.WX_GL_RGBA, 0
        )
        wx.glcanvas.GLCanvas.__init__(
            self, parent, -1, attribList = attribList,
            *args, **kwds)

        CanvasModule.Canvas.__init__(self, *args, **kwds)
        return


    def Render(self, dc):
        if self._frameIsInProcessOfShowing:
            return

        """
        copied from zgl_graphdrawer.wx_canvas.Canvas
        """

        self.SetCurrent()

        self.displayFunc()

        self.SwapBuffers()
        return


    def forceRedraw(self):
        """
        copied from zgl_graphdrawer.wx_canvas.Canvas
        """
        dc = wx.PaintDC(self)
        self.Render(dc)
        return

    def initializeEventHandlers(self, contextManager=None):
        self.contextManager(contextManager)

        for key, default in [
            ('mouse event handler', EventModule.MouseEventHandler),
            ('key event handler', EventModule.KeyEventHandler),
            ('canvas event handler', EventModule.CanvasEventHandler),
            ]:

            classObject = contextManager.app().getResourceValue(
                "%s class" % key, default=default)

            eventHandler = classObject(self)
            eventHandler.bindEvents()
            self.PushEventHandler(eventHandler)

            # TODO:
            # remove this once the event handler mechanism works
            contextManager.app().setResourceValue(
                key, eventHandler)

            pass

        return


    def initializeTimer(self):
        """
        copied from zgl_graphdrawer.wx_canvas.Canvas
        """

        self.TIMER_ID = 100  # pick a number

        # message will be sent to the parent
        self.timer = wx.Timer(self.GetParent(), self.TIMER_ID)  
        self.timer.Start(100)  # x100 milliseconds

        # TODO:
        # figure out how to have multiple listeners for the time event
        # currently only the CanvasEventHandler is handling it

        return

    def drawMetaInfo(self):
        
        CanvasModule.Canvas.drawMetaInfo(self)

        # draw breadcrumbs
        x = 30
        y = self.height - 45
        glColor3f(1.0, 1.0, 1.0)
        zglUtils.drawBitmapText(
            self.breadCrumbs(),
            x, y)
        
        return

    def drawFPS(self, x, y):
        if hasattr(self, "last_t"):
            self.fps = 1.0/float(time.time()-self.last_t)
            glColor3f(1.0, 1.0, 1.0)

            zglUtils.drawBitmapText(
                "FPS: %f" % (self.fps), 
                x, y,
                font=GLUT_BITMAP_HELVETICA_10)
        self.last_t = time.time()

        return


    # END class Canvas
    pass
