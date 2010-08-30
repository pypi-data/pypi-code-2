#-----------------------------------------------------------------------------
# Name:        Model.py
# Purpose:     concentrate model related functions in a single module
#
# Author:      Flavio Codeco Coelho
#
# Created:     2006/08/20
# RCS-ID:      $Id: Model.py $
# Copyright:   (c) 2004-2006 
# Licence:     GPL
# New field:   Whatever
#-----------------------------------------------------------------------------

from scipy import integrate
from numpy import *
from string import *

class Model:
    def __init__(self,equations,pars,inits, trange,):
        """
        Equations: a function with the equations
        inits: sequence of initial conditions
        trange: time range for the simulation
        """
        self.eqs = equations
        self.pars = pars
        self.Inits = inits
        self.Trange = arange(0,trange,0.1)
        self.compileParEqs()
        
    def compileParEqs(self):
        """
        compile equation and parameter expressions
        """
        #Equations
        eql = self.eqs.strip().split('\n')
        pl = self.pars.strip().split('\n')
        self.vnames = [v.split('=')[0] for v in eql if '=' in v]
        self.pnames = [p.split('=')[0] for p in pl if '=' in p]
        
        try:
            self.ceqs = [compile(i.split('=')[-1],'<equation>','eval') for i in eql]
        except SyntaxError:
            dlg = wx.MessageDialog(self, 'There is a syntax error in the equation Box.\nPlease fix it and try again.',
                      'Syntax Error', wx.OK | wx.ICON_INFORMATION)
            try:
                dlg.ShowModal()
            finally:
                dlg.Destroy()
        #Parameters
        if self.pars.strip() =="":
            self.cpars=[]
            return  
        if self.pnames:
            #in this case returns the compete expression, including the '='
            try:     
                self.cpars = [compile(i,'<parameter>','exec') for i in pl]
            except SyntaxError:
                dlg = wx.MessageDialog(self, 'There is a syntax error in the parameter Box.\nPlease fix it and try again.',
                          'Syntax Error', wx.OK | wx.ICON_INFORMATION)
                try:
                    dlg.ShowModal()
                finally:
                    dlg.Destroy()
        else:      
            try:     
                self.cpars = [compile(i,'<parameter>','eval') for i in pl]
            except SyntaxError:
                dlg = wx.MessageDialog(self, 'There is a syntax error in the parameter Box.\nPlease fix it and try again.',
                          'Syntax Error', wx.OK | wx.ICON_INFORMATION)
                try:
                    dlg.ShowModal()
                finally:
                    dlg.Destroy()
    
    def Run(self):
        """
        Do numeric integration
        """
        t_courseList = []
        t_courseList.append(integrate.odeint(self.Equations,self.Inits,self.Trange, 
        full_output=0, printmessg=0))
        return (t_courseList,self.Trange)
    
    def Equations(self,y,t):
        """
        This function defines the system of differential equations, evaluating
        each line of the equation text box as ydot[i]

        returns ydot
        """
        par = self.pars

    #---Create Parameter Array----------------------------------------------------------------------------
        pars = self.cpars#par.strip().split('\n')
        Npar = len(pars)
        if self.vnames:
            exec('%s=%s'%(','.join(self.vnames),list(y)))
        p = zeros((Npar),'d') #initialize p
        if pars: #only if there is at least one parameter
            for j in xrange(len(pars)):
                if self.pnames:
                    exec(pars[j])
                else:
                    p[j] = eval(pars[j]) #initialize parameter values
                        
    #---Create equation array----------------------------------------------------------------------------
        eqs = self.ceqs#strip(self.eqs).split('\n')
        Neq=len(eqs)
        ydot = zeros((Neq),'d') #initialize ydot
        for k in xrange(Neq):
            ydot[k] = eval(eqs[k]) #dy(k)/dt

        return ydot