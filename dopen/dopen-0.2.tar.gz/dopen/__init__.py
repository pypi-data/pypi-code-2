#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys

class DOPEN():
    def __init__(self, *args, **kwds):
        self.categories = []
        self.extensions = []
        self.programs = []

        self.load()

    def load(self):
        """Load the extlib.ded file and find the categories and extensions"""
        try:
            f = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"extlib.ded"),"r")
            for line in f.readlines():
                if not line.startswith("#") and not line.endswith("#"):
                    if line.startswith("@DCM:VERSION"):
                        self.version = line.strip().split("|")[1]
                    else:
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

    def get_program(self,ext):
        """Get the program for a given extension"""
        try:
            p,c,e = self.get_values(ext)
            return p
        except NotFoundError:
            return

    def get_val(self,fl):
        """Get the values for a given file (values = category,extension and program"""
        try:
            return self.get_values(self.get_extension(fl))
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

    def set_prog(self,fl,prog):
        """Set the program for a given fille"""
        self.set_program(self.get_extension(fl),prog)

class NotFoundError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value())