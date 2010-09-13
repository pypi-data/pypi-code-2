
#-----------------------------------------------------------------------------
# Name:        lhsframe.py
# Purpose:     Implementation of the uncertainty panel
#
# Author:      Flavio Codeco Coelho
#
# Created:     2006/08/31
# RCS-ID:      $Id: lhsframe.py $
# Copyright:   (c) 2004
# Licence:     gpl
# New field:   Whatever
#-----------------------------------------------------------------------------
#import wxversion

import wx
import os,cPickle
from Bayes import lhs, Melding as meld
from lhsframe_glade import wxFrame
from numpy import *
from pylab import load

class LHS(wxFrame):
    def __init__(self,*args,**kwargs):
        wxFrame.__init__(self,None)
        self.parsAppended = (0,0)
        self.phi = ['a','b','c'] #to be overridden at runtime
        self.theta = [] #to be overridden at runtime
        self.fileName = ''#to be overridden at runtime
        self.specs = {}
        self.priors = [[],[]]#list of distribution names and their parameters
        self.priords = []
        self.lhoods = []
        self.Done = False
        self.distCB.AppendItems(lhs.valid_dists)
        #binding events
        self.button_2.Bind(wx.EVT_BUTTON,self.onOkButton)
        self.setBtn.Bind(wx.EVT_BUTTON,self.onSetButton)
        self.button_3.Bind(wx.EVT_BUTTON,self.onCancelButton)
        self.anaChoice.Bind(wx.EVT_CHOICE,self.onAnaChoice)
        self.alpha = 0.5

    #event handlers
    def onOkButton(self,event):
        """
        Handles the Ok button
        """
        self.specs['samples'] = int(self.sampleSpin.GetValue())
        self.parnames = [k for k,v in self.specs.items() if k not in ['samples','alpha']]

        if self.anaChoice.GetStringSelection() == 'Uncertainty':
            self.alpha = int(self.alphaSlider.GetValue())/100.
            self.specs['alpha'] = self.alpha
            #check if all variables are present in the dictionary.
            if len(self.parnames) != len(self.phi)+len(self.theta):
                dlg = wx.MessageDialog(self, 'You have not defined distribution for All the parameters and variables!',
              'Incomplete Settings', wx.OK | wx.ICON_INFORMATION)
                try:
                    dlg.ShowModal()
                finally:
                    dlg.Destroy()
                    return
        elif self.anaChoice.GetStringSelection() == 'Sensitivity':
            #check if all variables are present in the dictionary.
            if len(self.parnames) != len(self.theta):
                dlg = wx.MessageDialog(self, 'You have not defined distribution for All the parameters!',
              'Incomplete Settings', wx.OK | wx.ICON_INFORMATION)
                try:
                    dlg.ShowModal()
                finally:
                    dlg.Destroy()
                    return
        if self.likTC.GetValue() != '':
            if self.readData(): #if read data fails
                return
        self.genPriorList(self.anaChoice.GetStringSelection())
        self.priords = []
        #check mode of sampling to run
        if self.radio_box_1.GetLabel() == "Random":#Random sampling
            self.priords = lhs.lhs(self.parnames,self.priors[0],self.priors[1],int(self.specs['samples']))
        else:#LHS sampling
            if self.radio_box_2.GetStringSelection() == "User-specified":
                #print"doing 1"
                self.priords = lhs.lhs(self.parnames,self.priors[0],self.priors[1],int(self.specs['samples']),noCorrRestr=False,matCorr=self.getCorrMatrix())
            elif self.radio_box_2.GetStringSelection() == "Random":
                #print"doing 2"
                self.priords = lhs.lhs(self.parnames,self.priors[0],self.priors[1],int(self.specs['samples']),noCorrRestr=False)
            else:
                #print"doing 3"
                self.priords = lhs.lhs(self.parnames,self.priors[0],self.priors[1],int(self.specs['samples']))
        self.saveSpecs()
        self.Done = True
        dlg = wx.MessageDialog(self, 'Now press the "Start" button on the main window!',
          'Start your Simulation', wx.OK | wx.ICON_INFORMATION)
        try:
            dlg.ShowModal()
        finally:
            dlg.Destroy()


        self.Lower()

    def onSetButton(self,event):
        """
        Handles the set parameter button
        """
        if not self.distParsTC.GetValue():
            dlg = wx.MessageDialog(self, 'You have to enter parameters for the distribution selected',
              'No Distribution Parameters', wx.OK | wx.ICON_INFORMATION)
            try:
                dlg.ShowModal()
            finally:
                dlg.Destroy()
            return
        self.specs[self.parsCB.GetStringSelection()] = {'dist':self.distCB.GetStringSelection(),'pars':self.distParsTC.GetValue()}
        line = '%s: %s(%s)\n'%(self.parsCB.GetStringSelection(),self.distCB.GetStringSelection(),self.distParsTC.GetValue())
        self.logTC.AppendText(line)
        self.frame_1_statusbar.SetStatusText('%s set'%self.parsCB.GetStringSelection(),0)

    def genPriorList(self, anatype='Uncertainty'):
        """
        Generates the list of priors in the order expected by the melding
        """
        self.priors = [[],[]]
        npar  = len(self.theta)
        neq = len(self.phi)
        for i in xrange(npar):
            self.priors[0].append(self.specs[self.theta[i]]['dist'])
            self.priors[1].append(tuple([float(n) for n in self.specs[self.theta[i]]['pars'].strip().split(' ')]))
        if anatype == 'Uncertainty':
            for i in xrange(neq):
                self.priors[0].append(self.specs[self.phi[i]]['dist'])
                self.priors[1].append(tuple([float(n) for n in self.specs[self.phi[i]]['pars'].strip().split(' ')]))


    def onCancelButton(self,event):
        """
        Cancel Uncertainty analysis
        """
        self.Done = False
        self.Close()

    def onAnaChoice(self,event):
        """
        Handles change in analysis type
        """
        pars = self.phi
        if self.anaChoice.GetStringSelection() == 'Uncertainty':
            self.likTC.Enable(True)
            self.label_8.Enable(True)
            self.alphalabel.Enable(True)
            self.alphaSlider.Enable(True)
            if not self.parsAppended[0]:
                self.parsCB.AppendItems(pars)
                self.parsAppended = (1,len(pars))
                #print self.parsCB.GetCount()
        else:
            self.likTC.Enable(False)
            self.label_8.Enable(False)
            self.alphalabel.Enable(False)
            self.alphaSlider.Enable(False)
            if self.parsAppended[0]:
                for i in pars:
                    self.parsCB.Delete(self.parsCB.GetCount()-1)
                self.parsCB.SetValue('')
                self.parsAppended = (0,0)
        #print self.anaChoice.GetSelection(),self.anaChoice.GetStringSelection()

    def readData(self):
        """
        Read from data file and build data vectors for likelihoods
        Data file must be a csv with as many columns as data vectors.
        Header should be distribution types.
        """
        os.chdir(os.path.split(self.fileName)[0])
        valid_dists = ['normal','exponential','bernoulli','lognormal','poisson']
        self.lhoods = []
        try:
            fname = self.likTC.GetValue().strip()
            data = load(fname,skiprows=1,delimiter=',')
            f = open(fname)
            likdists = [i.strip() for i in f.readline().split(',')]
            f.close()
        except:
            dlg = wx.MessageDialog(self, 'Could not open File.\nPlease check file name, and press Ok to try again',
              'Invalid File', wx.OK | wx.ICON_INFORMATION)
            try:
                dlg.ShowModal()
            finally:
                dlg.Destroy()
            return 1
        # Check distribution types
        for i in likdists:
            if i not in valid_dists:
                dlg = wx.MessageDialog(self, '"%s" is not a valid model for the data.\nPlease fix your data file, and press Ok to try again'%i,
              'Invalid Model', wx.OK | wx.ICON_INFORMATION)
                try:
                    dlg.ShowModal()
                finally:
                    dlg.Destroy()
                return 1
        #Calculate likelihoods
        n = 0
        for d in transpose(data):
            m = min(d)
            M = max(d)
            dlg = wx.TextEntryDialog(self, 'Enter the limits of the Likelihood function for vector #%s\nseparated by spaces.\nData limits:[%s,%s] '%(n+1,m,M),
                                     'Enter Limits','')
            try:
                if dlg.ShowModal() == wx.ID_OK:
                    answer = dlg.GetValue()
                    if answer == '':
                        dlg = wx.MessageDialog(self, 'You have not entered limits\nAssuming data range.', 'No Limits Entered', wx.OK | wx.ICON_INFORMATION)
                        try:
                            dlg.ShowModal()
                        finally:
                            dlg.Destroy()
                    else:
                        limits = [float(j) for j in answer.strip().split(' ')]
            finally:
                dlg.Destroy()
            self.lhoods.append(meld.Likeli(d,likdists[n],limits))
            n+=1
        return 0

    def saveSpecs(self):
        """
        Saves the current uncertainty specs.
        """
        os.chdir(os.path.split(self.fileName)[0])
        fname = os.path.split(self.fileName)[1]
        fname = fname[:-4]+'_unc.spec'
        f = open(fname,'w')
        cPickle.dump(self.specs,f)
        f.close()

    def loadSpecs(self, fname):
        """
        Load specs from last uncertainty analysis ran from file fname.
        """
        os.chdir(os.path.split(self.fileName)[0])
        f = open(fname,'r')
        self.specs = cPickle.load(f)
        for k,v in self.specs.items():
            if k == 'samples':
                self.sampleSpin.SetValue(int(v))
                continue
            elif k == 'alpha':
                self.alpha = float(v)
                continue
            line = '%s: %s(%s)\n'%(k,v['dist'],v['pars'])
            self.logTC.AppendText(line)
        f.close()
        self.frame_1_statusbar.SetStatusText('Parameter specifications loaded, press OK to continue.')

    def getCorrMatrix(self):
        """
        create a Numeric array with the contents of the spreadsheet
        """
        if self.anaChoice.GetStringSelection() == 'Uncertainty':
            dim = len(self.theta)+len(self.phi)
        else:
            dim = len(self.theta)
        data = zeros((dim,dim),float)
        for i in xrange(dim):
            for j in xrange(dim):
                data[i,j] = float(self.grid_1.GetCellValue(i,j))
        #print data, data.shape, data[0,0]
        return data

if __name__ == '__main__':
    app = wx.PySimpleApp()
    LHS(None).Show()
    app.MainLoop()
