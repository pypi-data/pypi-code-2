'''
Created on Jul 28, 2010

@author: dwmclary
'''
import sys, string

class CodeGenerator:
    
    def begin(self, tab="\t"):
        self.code = []
        self.tab = tab
        self.level = 0
        
    def end(self):
        return string.join(self.code, "")
    
    def write(self, string):
        self.code.append(self.tab * self.level + string)
    
    def indent(self):
        self.level += 1
        
    def dedent(self):
        if self.level > 0:
            self.level -= 1
