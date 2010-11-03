"""
A file datasource working on yaml format.
"""

import os

from metamodel.basemodel import SubscribableModel
from metamodel.properties import Property,File

from metamodel.yamlserializer import LoadModel, SaveModel
from metamodel.datasources import DataSource, DataSourceRoot
from metamodel.instancereg import InstanceRegistry

class FileDataSource(DataSource):
    file = File(["caf","xcaf"])

    def setProperty(self, name, value):
        try:
            prevfile = self.file
        except:
            prevfile = None
        SubscribableModel.setProperty(self, name, value)
        if name == "file" and not prevfile == value:
           if self.file and os.path.exists(self.file):
               self.load_file(value)

    def load_file(self, filename):
        f = open(filename)
        data = f.read()
        f.close()
        self.purgeChildren()
        dsroot = LoadModel(data, "DataSourceRoot", self)[0]
        InstanceRegistry.replace_listener(dsroot, self)
        objects = dsroot.getChildren()
        for obj in objects:
            # use parent addChild so we don't get double add into datasource
            self.addChild(obj)
        dsroot.invalidate()

    def save(self,filename=None):
        if not filename:
           filename = self.file
        data = SaveModel(self, 
                         datasource=self,
                         inst_mapping={self:"DataSourceRoot"})
        f = open(filename,"w")
        f.write(data)
        f.close()

    builtby = ["DataSource"]
    builts = ["SubscribableModel"]
