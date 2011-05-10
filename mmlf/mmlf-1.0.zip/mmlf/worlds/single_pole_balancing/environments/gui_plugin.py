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

##!/usr/bin/env python
##
## 2008-04, Daniel Bessler
#
#from math import sqrt
#
#import gtk, gobject
#import cairo
#
#from mmlf.framework.interaction_server.world_interface import World
#
#from mmlf.framework.gui.plugin import MLFEnvironmentPlugin
#from mmlf.framework.gui.gui_manager import guiManager
#
#class GuiPlugin(MLFEnvironmentPlugin):
#    def __init__(self):
#        MLFEnvironmentPlugin.__init__(self)
#
#        self.pluginWidget = None
#
#        self.pluginID = "Singlepolebalancing plugin"
#        self.description = "Plugin visualizing the Singlepolebalancing Environment"
#
#        self.cartPosition = 0.0 # initiall position
#        self.poleAngularPosition = 0.0 # initiall position
#        self.positionFactor = 25 # scale factor for the positions
#
#        self.cartWidth = 80
#        self.cartHeight = 40
#        self.poleLength = 70
#        self.lineSpace = 20
#
#        self.timeoutID = 0
#
#    def load(self):
#        self.pluginWidget = gtk.DrawingArea()
#        self.pluginWidget.set_size_request(20*self.positionFactor + self.cartWidth,
#             self.cartHeight + self.poleLength + self.lineSpace + 10)
#        self.pluginWidget.connect("expose-event", self.widgetExposeCB, None)
#
#        self.timeoutID = gobject.timeout_add(20, self.timeout, None)
#
#    def widgetExposeCB(self, widget, event, Data=None):
#        env = World.world.environment
#
#        cr = widget.window.cairo_create()
#
#        # clip the drawing context to avoid unneeded redrawing
#        cr.rectangle(event.area.x, event.area.y, event.area.width, event.area.height)
#        cr.clip()
#
#        # draw white background
#        cr.set_source_rgb(1, 1, 1)
#        cr.paint()
#
#        cr.set_source_rgb(0, 0, 0)
#        cr.set_line_width(2.5)
#
#        # draw axis
#        cr.save()
#        cr.move_to(self.lineSpace/2, widget.allocation.height -self.lineSpace/2)
#        cr.line_to(widget.allocation.width - self.lineSpace/2, widget.allocation.height -self.lineSpace/2)
#        cr.stroke()
#
#        cr.set_line_width(1.5)
#        # left arrow
#        cr.move_to(self.lineSpace, widget.allocation.height - self.lineSpace)
#        cr.rel_line_to(-self.lineSpace/2, self.lineSpace/2)
#        cr.rel_line_to(self.lineSpace/2, self.lineSpace/2)
#        # right arrow
#        cr.move_to(widget.allocation.width - self.lineSpace, widget.allocation.height - self.lineSpace)
#        cr.rel_line_to(self.lineSpace/2, self.lineSpace/2)
#        cr.rel_line_to(-self.lineSpace/2, self.lineSpace/2)
#
#        cr.move_to(widget.allocation.width/2, widget.allocation.height-2)
#        cr.rel_line_to(0, 4-self.lineSpace/2)
#        cr.stroke()
#
#        # finish marks
#        cr.save()
#        def drawFinishMark (cr, factor):
#            cr.set_source_rgb(1, 0.4, 0.4)
#            cr.rel_line_to(0, self.lineSpace/2)
#            cr.rel_line_to(factor*self.lineSpace/2, -self.lineSpace/2)
#            cr.rel_line_to(-factor*self.lineSpace/2, 0)
#            cr.fill_preserve()
#            cr.set_source_rgb(0, 0, 0)
#        maxCartPosition = env.normalSimulation.configDict["MAXCARTPOSITION"]
#        cr.move_to(widget.allocation.width/2 + self.positionFactor*maxCartPosition, widget.allocation.height -self.lineSpace/2)
#        drawFinishMark(cr, 1.0)
#        cr.stroke()
#        cr.move_to(widget.allocation.width/2 - self.positionFactor*maxCartPosition, widget.allocation.height -self.lineSpace/2)
#        drawFinishMark(cr, -1.0)
#        cr.stroke()
#        cr.restore()
#
#        # draw the box
#        cr.save()
#        cr.rectangle(widget.allocation.width/2 + self.positionFactor*self.cartPosition - self.cartWidth/2,
#            widget.allocation.height - self.lineSpace - self.cartHeight,
#            self.cartWidth, self.cartHeight)
#        cr.stroke()
#        cr.move_to(widget.allocation.width/2 + self.positionFactor*self.cartPosition, widget.allocation.height -self.lineSpace/2)
#        cr.rel_line_to(-self.lineSpace/2, -self.lineSpace/2)
#        cr.rel_line_to(self.lineSpace, 0)
#        cr.rel_line_to(-self.lineSpace/2, self.lineSpace/2)
#        cr.set_source_rgb(0.4, 0.4, 0.4)
#        cr.fill()
#        cr.set_source_rgb(0, 0, 0)
#        cr.stroke()
#        cr.restore()
#
#        # draw the pole angle
#        cr.save()
#        boxPosition = (widget.allocation.width/2 + self.positionFactor*self.cartPosition,
#            widget.allocation.height - self.lineSpace - self.cartHeight)
#        anglePositionX = boxPosition[0] + self.positionFactor*self.poleAngularPosition
#        anglePositionY = boxPosition[1] - abs((self.poleLength * self.poleLength)/
#            sqrt(pow(self.positionFactor*self.poleAngularPosition, 2) + pow(self.poleLength, 2)))
#        cr.move_to(boxPosition[0], boxPosition[1])
#        cr.line_to(anglePositionX, anglePositionY)
#        cr.stroke()
#        cr.restore()
#
#        return True
#
#    def timeout(self, Data=None):
#        env = World.world.environment
#        cartPosition = env.normalSimulation.currentState["cartPosition"]
#        poleAngularPosition = env.normalSimulation.currentState["poleAngularPosition"]
#
#        # update positions
#        if (cartPosition != self.cartPosition):
#            self.pluginWidget.queue_draw()
#        if (poleAngularPosition != self.poleAngularPosition):
#            self.pluginWidget.queue_draw()
#        self.cartPosition = cartPosition
#        self.poleAngularPosition = poleAngularPosition
#
#        return True
#
#    def unload(self):
#        gobject.source_remove(self.timeoutID)
#        self.pluginWidget.destroy()
#
#    def mapWidgets(self):
#        guiManager.mlf_gui.widgetContainer.addWidget(self.pluginWidget, "Singlepolebalancing plugin", self.pluginID, None)
#
#    def getWidget(self, widgetID):
#        return self.pluginWidget
#
#GuiPluginClass = GuiPlugin