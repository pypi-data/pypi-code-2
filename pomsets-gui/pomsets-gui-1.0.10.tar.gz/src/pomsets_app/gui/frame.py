import os

import pomsets_app.controller.automaton as AutomatonModule


class Frame(object):

    def app(self, value=None):
        if value is not None:
            self._app = value
        return self._app


    def displayPomset(self, pomsetContext, pomsetReferencePath=None):
        
        canvas = self.canvas

        contextManager = self.app().contextManager()

        if pomsetContext is None:
            contextManager.currentDisplayedPomsetInfo((None, None, False))
            canvas.breadCrumbs('No active pomset to display')
            canvas.OnRefresh()
            return

        # after this point
        # it is assumed that pomsetContext is not None
        if pomsetReferencePath is None:
            pomsetReferencePath = [pomsetContext.reference()]
        pomsetReference = pomsetContext.reference()

        contextManager.currentDisplayedPomsetInfo(
            (pomsetContext, pomsetReferencePath, True))

        # display the actual pomset in the canvas
        canvas.displayPomset(pomsetReferencePath)

        self.setBreadCrumbs(pomsetContext, pomsetReferencePath)
        
        self.updateMenuBarActions()
        return


    def selectActivePomset(self, pomset):
        
        # currently a placeholder
        # need to figure out the pomset currently being displayed
        # and select that in the GUI
        if self._updateActivePomsetTreeCtrlSelection:
            print "should update selection"

        
        # set the breadcrumbs for the pomset to be displayed
        contextManager = self.app().contextManager()
        activeContext = contextManager.activePomsetContext()

        return


    def setBreadCrumbs(self, pomsetContext, contextPath=None):
        if contextPath is None:
            contextPath = [pomsetContext.reference()]

        canvas = self.canvas
        canvas.breadCrumbs(' > '.join([x.name() for x in contextPath]))
        
        return

    # END class Frame
    pass


