import sys
import os.path
from datetime import datetime

class Table:
    count = 0
    def __init__(self, org, name = None, titles = None, plot = None):
        self.name = name
        self.titles = titles
        self.plot = plot
        self.lines = []
        self.org = org
        self.id = self.count
        self.count += 1
    
    def append(self, value):
        self.lines.append(value)
    
    def output(self):
        if self.plot:
            if self.name == None:
                name = "table%i" % self.id
            else:
                name = self.name
            
            try:
                os.makedirs(os.path.join(self.org.path, self.org.name + "_figures"))
            except OSError:
                pass
            
            plotfile = os.path.join(self.org.name + "_figures", self.org.name + "-" + name + ".png")
            
            if isinstance(self.plot, str):
                options = self.plot
            else:
                options = ""
            
            self.org.indent()
            self.org.write("#+PLOT: %s file:\"%s\"\n" % (options, plotfile))
        
        if self.titles != None:
            self.org.indent()
            self.org.write("|")
            for t in self.titles:
                self.org.write(" %s |" % t)
            self.org.write("\n")
        self.org.indent()
        self.org.write("|---\n")
        for l in self.lines:
            self.org.indent()
            self.org.write("|")
            for c in l:
                self.org.write(" %s |" % c)
            self.org.write("\n")
        
        if self.plot:
            self.org.indent()
            self.org.write("file:%s\n" % plotfile)
    
    def __call__(self):
        self.output()

class Orgreport:
    def __init__(self, filename = None, title = None, verbose = False, path = "", name = None, options = None, html = False):
        self.path = path
        if filename == None:
            if name == None:
                date = datetime.today().strftime("%Y%m%d-%H%M%S")
                self.name = os.path.basename(sys.argv[0]) + "-" + date
            else:
                self.name = name
            self.filename = os.path.join(self.path, self.name + ".org")
        else:
            (path, name) = os.path.split(filename)
            self.path = path
            self.name = os.path.splitext(name)[0]
            self.filename = filename
        self.title = title
        self.verbose = verbose
        
        try:
            os.makedirs(self.path)
        except OSError:
            pass
        
        self.file = open(self.filename, "w")        
        self.depth = 0
        self.stars = ""
        self.indentation = ""
        self.tables = {}
        
        if options != None:
            self.write("#+OPTIONS: %s\n" % options)
        if self.title != None:
            self.content(self.title + "\n")
    
    def write(self, l):
        self.file.write(l)
        if self.verbose:
            sys.stdout.write(l)
            sys.stdout.flush()
        
        return self
    
    def indent(self):
        self.write(self.indentation)
        
        return self
    
    def newline(self):
        self.write("\n")
        
        return self
    
    def para(self, title):
        if self.depth == 0:
            self.indentation = " "
        self.depth  += 1
        self.stars  += "*"
        self.indentation += " "
        
        self.write("%s %s\n" % (self.stars, title))
        
        return self
    
    def end(self):
        self.newline()
        self.depth -= 1
        if self.depth == -1:
            self.file.close()
            if self.html:
                os.system("emacs --batch --visit=%s --funcall org-export-as-html-batch" % self.filename)
            return None
        else:
            self.stars = self.stars[1:]
            self.indentation = self.indentation[1:]      
            return self
    
    def content(self, text):
        lines = text.split("\n")
        for l in lines:
            self.write("%s%s\n" % (self.indentation, l))
        self.newline()
        
        return self

    def table(self, **kwargs):
        return Table(self, **kwargs)
    
    def context(self, env = False, source = False):
        self.para("Context")
        self.content(" ".join(sys.argv))
        if env:
            self.para("Environment")
            for var in os.environ.keys():
                self.content("%s=%s" % (var,os.environ[var]))
            self.end()
        if source:
            self.para("Source")
            self.content("#+BEGIN_SRC python")
            self.content(open(sys.argv[0]).read())
            self.content("#+END_SRC")
            self.end()
        self.end()
        
        return self

if __name__ == "__main__":
    report = Orgreport("toto.org", "Test of orgreport", verbose = True)
    report.context()
    table2 = report.table(titles = ["Alpha", "Beta"])
    report.para("Toto")
    table2.append((1, 2))
    report.para("Tata")
    table2.append((3, 4))
    report.end()
    report.para("Bla")
    table2.append((5, 6))
    report.content("""Lorem ipsum
Bablabla
Et caetera""")
    report.para("Bli")
    table2.append((7, 8))
    report.content("""Encore du blabla""")
    report.end()
    report.end()
    report.para("Table")
    table1 = report.table(plot = True)
    table1.append((1.0, 2.0, 3.0))
    table1.append((1.1, 2.1, 3.1))
    table1.append((1.2, 2.2, 3.2))
    table1.append((1.3, 2.3, 3.3))
    table1.output()
    report.para("Table 2")
    table2.output()
    table2()
    report.end()

