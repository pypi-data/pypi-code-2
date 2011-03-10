
from watchvideo.qt.QtGui import QTreeWidgetItem

class TreeWidgetItem(QTreeWidgetItem):
    def __init__(self, strings, item, parent=None):
        super(TreeWidgetItem, self).__init__(parent, strings)
        self.item = item
        
    def getDownload(self):
        return self.item
        
    #If this is a search item
    def getMedium(self):
        return self.item
        
    def getOriginalUrl(self):
        return self.item.url
        
