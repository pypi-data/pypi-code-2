#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys,urllib2

class DOPEN():
    def __init__(self, *args, **kwds):
        self.categories = []
        self.extensions = []
        self.programs = []
        self.version = 2.0

        self.load()

    def load(self):
        """Load the extlib.ded file and find the categories and extensions"""
        try:
            f = open(os.path.join(os.path.dirname(__file__),"extlib.ded"),"r")
            for line in f.readlines():
                if not line.startswith("#") and not line.endswith("#"):
                    pass
                else:
                    line = line[1:-2]
                    cat = line.strip().split(" ")[0]
                    line = line[len(cat):]
                    catnum = len(self.categories)
                    self.categories.append(cat)
                    extsl = []
                    progl = []
                    for ext in line.strip().split(";"):
                        extsl.append(ext.strip().split("|")[0])
                        progl.append(ext.strip().split("|")[1])
                    self.extensions.append(extsl)
                    self.programs.append(progl)
            f.close()
        except:
            sys.exit(2)

    def save(self):
        savedata = "@DCM:TITLE|DOPEN\n@DCM:VERSION|" + str(self.version) + "\n"
        for c,category in enumerate(self.categories):
            savedata += "#" + category + " "
            i = 0
            while i < len(self.extensions[c]):
                savedata += self.extensions[c][i] + "|" + self.programs[c][i] + ";"
                i+=1
            savedata = savedata[:-1] + "#\n"
        #actualy save the data
        try:
            f = open(os.path.join(os.path.dirname(__file__),"extlib.ded"),"w")
            f.write(savedata)
            f.close()
        except:
            print "error while saving data"
            sys.exit(2)

    #Updating

    def update(self):
        """extlib = "https://www.dropbox.com/s/p7jew5klqg067kv/extlib_2.0.ded"
        u = urllib2.urlopen(extlib)
        localFile = open('extlib_2.0.ded', 'w')
        localFile.write(u.read())
        localFile.close()"""
        #load new file
        c,e,p = self.update_load()
        #Check categories
        c,e,p = self.cat_check(c,e,p)
        #Compare and Add
        self.compare(c,e,p)
        self.save()  

    def compare(self,c,e,p):
        for i,cat in enumerate(self.categories):
            for j,ext in enumerate(e[i]):
                if not ext in self.extensions[i]:
                    self.extensions[i].append(ext)
                    self.programs[i].append(p[i][j])

    def cat_check(self,categories,extensions,programs):
        if len(categories) < len(self.categories):
            print "Could not update, corrupt extlib.ded"
            c = raw_input("Use New or Old extlib file? (n/o)")
            if c == "n":
                print "replace old with new"
            else:
                print "delete new"
            #Change
            raise NotFoundError
        elif len(categories) == len(self.categories):
            #check for invalid categories
            for cat in self.categories:
                ok = False
                i = 1
                for ca in categories:
                    if ca == cat:
                        ok = True
                    if not ok and i == len(categories):
                        print "Invalid categories"
                        #Change
                        raise NotFoundError
                    i += 1
            #check for category matching
            for i,cat in enumerate(self.categories):
                if categories[i] != self.categories[i]:
                    self.rearrange(categories,extensions,programs)
        return categories,extensions,programs

    def update_load(self):
        categories = []
        extensions = []
        programs = []
        f = open('extlib_2.0.ded','r')
        for line in f.readlines():
            if not line.startswith("#") and not line.endswith("#"):
                if line.startswith("@DCM:VERSION"):
                    version = float(line.strip().split("|")[1])
                    if int(version) != int(self.version):
                        print "Could not update, wrong version file"
                        return
                    else:
                        pass
                else:
                    pass
            else:
                line = line[1:-2]
                cat = line.strip().split(" ")[0]
                line = line[len(cat):]
                catnum = len(self.categories)
                categories.append(cat)
                extsl = []
                progl = []
                for ext in line.strip().split(";"):
                    extsl.append(ext.strip().split("|")[0])
                    progl.append(ext.strip().split("|")[1])
                extensions.append(extsl)
                programs.append(progl)
        f.close()
        return categories,extensions,programs

    def rearrange(self,cat,ext,prog):
        for i,categ in enumerate(self.categories):
            for j,catag in enumerate(cat):
                if categ == catag and i != j:
                    #same category but on different place
                    cat[i],cat[j] = cat[j],cat[i]
                    ext[i],ext[j] = ext[j],ext[i]
                    prog[i],prog[j] = prog[j],prog[i]

    ###Extension Based

    def get_program(self,ext):
        """Get the program for a given extension"""
        try:
            p,c,e = self.get_values(ext)
            return p
        except NotFoundError:
            return

    def get_values(self,flext):
        """Get the values for a given extension (values = category,extension and program)"""
        k = 0
        l = -1
        j = -1
        for extt in self.extensions:
            i = 0
            for ext in extt:
                if ext == flext:
                    j = i
                    l = k
                i += 1
            k += 1
        if l == -1 or j == -1:
            raise NotFoundError(flext)
        else:
            p = self.programs[l][j]
            cat = l
            extt = j
            return [p,cat,extt]

    def set_program(self,ext,prog):
        """Set the program for a given extension"""
        try:
            p,c,e = self.get_values(ext)
        except NotFoundError:
            return
        else:
            self.programs[c][e] = prog
            self.save()

    ###File Based

    def get_extension(self,fl):
        """Get the extension of a file"""
        num = len(fl.strip().split(".")) - 1
        if num != 0:
            flext = fl.strip().split(".")[num]
        else:
            f = open(fl, 'r')
            txt = ""
            for line in f.readlines():
                if line.startswith("#!/"):
                    flext = line
            f.close()
        return flext

    def get_prog(self,fl):
        """Get the program for a given file"""
        flext = self.get_extension(fl)
        try:
            return self.get_program(flext)
        except NotFoundError:
            return

    def get_val(self,fl):
        """Get the values for a given file (values = category,extension and program"""
        try:
            return self.get_values(self.get_extension(fl))
        except NotFoundError:
            return

    def set_prog(self,fl,prog):
        """Set the program for a given fille"""
        self.set_program(self.get_extension(fl),prog)

class NotFoundError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value())