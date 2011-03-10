
from watchvideo.qt.QtGui import QDockWidget

class SearchWidget(QDockWidget):
    
    def addAction(self, action):
        self.action = action
        
    def closeEvent(self, event):
        self.action.setChecked(False)
        QDockWidget.closeEvent(self, event)
