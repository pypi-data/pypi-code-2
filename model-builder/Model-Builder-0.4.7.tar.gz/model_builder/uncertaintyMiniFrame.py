# -*- coding:iso8859-1 -*-
#-----------------------------------------------------------------------------
# Name:        uncertaintyMiniFrame.py
# Purpose:     Panel to specify parameters for the uncertainty analysis
#
# Author:      <Flavio Codeco Coelho>
#
# Created:     2003/02/04
# RCS-ID:      $Id: uncertaintyMiniFrame.py,v 1.3 2004/01/13 10:51:43 fccoelho Exp $
# Copyright:   (c) 2003 Flavio Codeco Coelho <fccoelho@fiocruz.br>
# Licence:     This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
#-----------------------------------------------------------------------------
#Boa:MiniFrame:uncertaintyMiniFrame
#import wxversion
#wxversion.select('2.6')
import wx
import wx.gizmos
from Numeric import *
from string import *
from Bayes import Melding as meld
import os

def create(parent):
    return uncertaintyMiniFrame(parent)

[wxID_UNCERTAINTYMINIFRAME, wxID_UNCERTAINTYMINIFRAMEDONEBUTTON,
 wxID_UNCERTAINTYMINIFRAMELIKLIST, wxID_UNCERTAINTYMINIFRAMEPRIORLIST,
 wxID_UNCERTAINTYMINIFRAMESELALL, wxID_UNCERTAINTYMINIFRAMESPINCTRL1,
 wxID_UNCERTAINTYMINIFRAMESTATICTEXT1, wxID_UNCERTAINTYMINIFRAMESTATICTEXT2,
 wxID_UNCERTAINTYMINIFRAMESTATICTEXT3, wxID_UNCERTAINTYMINIFRAMESTATICTEXT4,
 wxID_UNCERTAINTYMINIFRAMESTATICTEXT5, wxID_UNCERTAINTYMINIFRAMESTATUSPANEL,
 wxID_UNCERTAINTYMINIFRAMEVARLIST,
] = [wx.NewId() for _init_ctrls in range(13)]

class uncertaintyMiniFrame(wx.MiniFrame):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.MiniFrame.__init__(self, id=wxID_UNCERTAINTYMINIFRAME,
              name='uncertaintyMiniFrame', parent=prnt, pos=wx.Point(181, 159),
              size=wx.Size(683, 445), style=wx.DEFAULT_FRAME_STYLE,
              title='Bayesian Melding Uncertainty Analysis')
        self.SetClientSize(wx.Size(683, 445))
        self.SetAutoLayout(True)
        self.SetToolTipString('Melding parameters')
        self.Bind(wx.EVT_CLOSE, self.OnUncertaintyMiniFrameClose)

        self.staticText1 = wx.StaticText(id=wxID_UNCERTAINTYMINIFRAMESTATICTEXT1,
              label='Choose state variable(s) to be analyzed:',
              name='staticText1', parent=self, pos=wx.Point(24, 16),
              size=wx.Size(226, 16), style=0)

        self.staticText2 = wx.StaticText(id=wxID_UNCERTAINTYMINIFRAMESTATICTEXT2,
              label='Variables:', name='staticText2', parent=self,
              pos=wx.Point(24, 40), size=wx.Size(56, 16), style=0)

        self.varList = wx.CheckListBox(choices=['Y[0]', 'Y[1]'],
              id=wxID_UNCERTAINTYMINIFRAMEVARLIST, name='varList', parent=self,
              pos=wx.Point(24, 56), size=wx.Size(104, 40), style=wx.VSCROLL,
              validator=wx.DefaultValidator)
        self.varList.SetToolTipString('The checked variables will be retained in memory for analysis.')
        self.varList.SetThemeEnabled(True)
        self.varList.Bind(wx.EVT_CHECKLISTBOX, self.OnVarListChecklistbox,
              id=wxID_UNCERTAINTYMINIFRAMEVARLIST)
        self.varList.Bind(wx.EVT_LISTBOX, self.OnVarListListbox,
              id=wxID_UNCERTAINTYMINIFRAMEVARLIST)

        self.staticText4 = wx.StaticText(id=wxID_UNCERTAINTYMINIFRAMESTATICTEXT4,
              label='Number of runs (k):', name='staticText4', parent=self,
              pos=wx.Point(300, 16), size=wx.Size(106, 16), style=0)

        self.spinCtrl1 = wx.SpinCtrl(id=wxID_UNCERTAINTYMINIFRAMESPINCTRL1,
              initial=5, max=100000, min=2, name='spinCtrl1', parent=self,
              pos=wx.Point(416, 16), size=wx.Size(95, 22),
              style=wx.SP_ARROW_KEYS)
        self.spinCtrl1.SetToolTipString('Number of times model should be run.')
        self.spinCtrl1.SetRange(2, 100000)
        self.spinCtrl1.SetThemeEnabled(True)

        self.Donebutton = wx.Button(id=wxID_UNCERTAINTYMINIFRAMEDONEBUTTON,
              label='Done', name='Donebutton', parent=self, pos=wx.Point(576,
              400), size=wx.Size(80, 32), style=0)
        self.Donebutton.SetToolTipString('Hit here when done')
        self.Donebutton.SetThemeEnabled(True)
        self.Donebutton.Bind(wx.EVT_BUTTON, self.OnDonebuttonButton,
              id=wxID_UNCERTAINTYMINIFRAMEDONEBUTTON)

        self.priorList = wx.TextCtrl(id=wxID_UNCERTAINTYMINIFRAMEPRIORLIST,
              name='priorList', parent=self, pos=wx.Point(176, 56),
              size=wx.Size(224, 144), style=wx.VSCROLL | wx.TE_MULTILINE,
              value='uniform (0,2)')

        self.likList = wx.TextCtrl(id=wxID_UNCERTAINTYMINIFRAMELIKLIST,
              name='likList', parent=self, pos=wx.Point(176, 242),
              size=wx.Size(224, 144), style=wx.VSCROLL | wx.TE_MULTILINE,
              value='normal (1,1)')
        self.likList.SetToolTipString('List of likelihood functions for each state variable')

        self.staticText3 = wx.StaticText(id=wxID_UNCERTAINTYMINIFRAMESTATICTEXT3,
              label='Prior distributions:', name='staticText3', parent=self,
              pos=wx.Point(184, 40), size=wx.Size(99, 16), style=0)

        self.staticText5 = wx.StaticText(id=wxID_UNCERTAINTYMINIFRAMESTATICTEXT5,
              label='Likelihood functions:', name='staticText5', parent=self,
              pos=wx.Point(184, 224), size=wx.Size(114, 16), style=0)

        self.statusPanel = wx.TextCtrl(id=wxID_UNCERTAINTYMINIFRAMESTATUSPANEL,
              name='Statuspanel', parent=self, pos=wx.Point(424, 56),
              size=wx.Size(216, 328),
              style=wx.HSCROLL | wx.VSCROLL | wx.TE_MULTILINE,
              value='Status Report:')

        self.selAll = wx.Button(id=wxID_UNCERTAINTYMINIFRAMESELALL,
              label='Select All', name='selAll', parent=self, pos=wx.Point(24,
              112), size=wx.Size(88, 32), style=0)
        self.selAll.SetThemeEnabled(True)
        self.selAll.SetToolTipString('Press this button to select all variables in the above list.')
        self.selAll.Bind(wx.EVT_BUTTON, self.OnSelAllButton,
              id=wxID_UNCERTAINTYMINIFRAMESELALL)

    def __init__(self, parent):
        self._init_ctrls(parent)
        self.uncertainPars = None
        self.dataloaded = 0

    def createVarList(self, items):
        """
        Re-creates varList checkListBox from items received from the main frame
        """
        self.varList = wx.CheckListBox(choices=items,
            id=wxID_UNCERTAINTYMINIFRAMEVARLIST, name='varList', parent=self,
            pos= wx.Point(24, 56), size= wx.Size(142, 54), style=0,
            validator=wx.DefaultValidator)
        self.varList.SetToolTipString('the checked variables will have to be assigned prior distribution on the right, and likelihoods if available.\n'+'Total items: '+str(self.varList.GetCount()))

    def updatePriorList(self, n):
        """
        Updates the box of prior distributions with a list of uniform priors
        based on the number of state variables elected.
        """
        value = 'uniform(0,10)\n'*(n-1)
        value = value+'uniform(0,10)'
        self.priorList.SetValue(value)


    def saveSpecs(self):
        """
        Saves the specs of the last analysis ran.
        """
        fname = os.path.split(self.fileName)[1]
        fname = fname[:-4]+'_unc.spec'
        checkedvars = [self.varList.IsChecked(i) for i in range(self.varList.GetCount())]
        pr = self.priorList.GetValue()
        lk = self.likList.GetValue()
        nr = self.spinCtrl1.GetValue()
        uncSpecs = {'vars':checkedvars, 'priors':pr, 'liks':lk,'nruns':nr}
        f = open(fname,'w')
        pickle.dump(uncSpecs,f)
        f.close()

    def loadSpecs(self, fname):
        """
        Load specs from last uncertainty analysis ran from file fname.
        """
        f = open(fname,'r')
        uncSpecs = pickle.load(f)
        f.close()
        for i in range(len(uncSpecs['vars'])):
            if uncSpecs['vars'][i] == 1:
                self.varList.Check(i)

        self.priorList.SetValue(uncSpecs['priors'])
        self.likList.SetValue(uncSpecs['liks'])
        self.spinCtrl1.SetValue(uncSpecs['nruns'])

    def OnDonebuttonButton(self, event):
        """
        When clicked this button checks the information about the Bayesian melding analysis, saves it and open a dialog box for specification of a data file
        (containing the data to calculate the likelihoods).
        returns a dictionary (uncertainPars) with the data entered.
        """
        self.saveSpecs()


# TODO: Introduce more checks to avoid stupid errors!!!
#---check if the number of checked variables is the same as the number of priors available---------------------------------------------------------------
        self.statusPanel.AppendText('\nChecking selected variables...\n')
        nvars = self.varList.GetCount() # Get the totalnumber of variables in varlist
        sel = [self.varList.IsChecked(i) for i in range(nvars)] # returns a list with ones for selected variables and zeros for not selected.
        if 1 not in sel: # if no variable has been selected, warn the user
            dlg = wx.MessageDialog(self, 'Select at least one variable from the list.',
              'Caption', wx.OK | wx.ICON_INFORMATION)
            try:
                dlg.ShowModal()
            finally:
                dlg.Destroy()
        self.statusPanel.AppendText('Done!\n\n')

#---Check if the number of priors entered corresponds to the number of variable selected----------------------------------------------------------------------------
        self.statusPanel.AppendText('Checking number of prior distributions...\n')
        npriors = int(self.priorList.GetNumberOfLines()) # Number of priors available
        while strip(self.priorList.GetLineText(npriors-1)) == '': # avoid getting empty lines at the end of the eq. box
            npriors = npriors-1
            if npriors == 1:
                break

        s = sum(array(sel))
        if s != npriors:
            dlg = wx.MessageDialog(self, 'The number of priors specified must be the same as the number of variables selected.',
              'Mismatched  number of variables and priors', wx.OK | wx.ICON_INFORMATION)
            try:
                dlg.ShowModal()
            finally:
                dlg.Destroy()
        self.statusPanel.AppendText('Done!\n\n')

        self.statusPanel.AppendText('Checking Number of likelihoods...\n')
        nlhoods = int(self.likList.GetNumberOfLines()) # Number of Likelihoods available
        while strip(self.likList.GetLineText(nlhoods-1)) == '': # avoid getting empty lines at the end of the eq. box
            nlhoods = nlhoods-1
            if nlhoods <= 1:
                break
        self.statusPanel.AppendText('Done!\n\n')
        if not self.likList.GetLineText(0) =='': #read datafile
            self.statusPanel.AppendText('Reading data from file...\n')
            dlg = wx.FileDialog(self, "Open data file", ".", "", "*.txt", wx.OPEN)
            try:
                if dlg.ShowModal() == wx.ID_OK:
                    filename = dlg.GetPath()
                    f = open(filename)
                    data = f.readlines()
                    f.close()
                    self.dataloaded = 1
                    self.statusPanel.AppendText('Done!\n\n')
            finally:
                dlg.Destroy()

            if len(data) != nlhoods: #check data size
                dlg = wx.MessageDialog(self, 'Number of datasets (lines) on the chosen file do not correspond to the number of likelihoods specified. Please open the correct file.',
                  'Wrong data file size!', wx.OK | wx.ICON_INFORMATION)
                try:
                    dlg.ShowModal()
                finally:
                    dlg.Destroy()


            else:
                datafloat=[None]
                for i in range(len(data)):
                    try:
                        data[i] = data[i][0:data[i].find("\\")] #remove newline characters
                    finally:
                        data[i] = data[i].split(' ') # Split strings into lists
                        datafloat[i] = [float(j) for j in data[i]] #Turns the list elements into   floats
                data = datafloat


#---initializing lists and dictionaries to receive form data----------------------------------------------------------------------------
        priors = []
        lhoods = []
        dist = []
        params = []
        distl = []
        paramsl = []
        k = self.spinCtrl1.GetValue() #number of runs
        for i in range(npriors):
            st = strip(self.priorList.GetLineText(i)) #get prior defining strings
            dist.append(strip(st[:find(st,'(')])) #parse distribution name
            params.append(eval(st[find(st,'('):])) # parse parameters string and eval it to a tuple
        priors = (dist,params) #name of the dist and parameters
        print dist[i]
#---generating priors----------------------------------------------------------------------------
        self.statusPanel.AppendText('generating priors...\n')
        priords = [meld.genprior(dist[i],params[i],k) for i in range(npriors)] #list of arrays
        self.statusPanel.AppendText('done!\n\n')
#-------------------------------------------------------------------------------
#---check if there are likelihoods available----------------------------------------------------------------------------
        if not self.likList.GetLineText(0) == '':
            for j in range(nlhoods):
                stl = strip(self.likList.GetLineText(j))#get likelihood defining strings
                distl.append(strip(stl[:find(stl,'(')]))#parse distribution name
                paramsl.append(eval(stl[find(stl,'('):]))# parse parameters string and eval it to a tuple
            lhoods = (distl,paramsl) #name of the dist and parameters

#---calculating likelihoods----------------------------------------------------------------------------
            self.statuspanel.AppendText('calculating likelihoods...\n')
            lik = []
            for l in range (nlhoods):
                dat = data[l]
                lik.append(meld.Likeli(dat, distl[l],paramsl[l])) #calculates likelihoods f
        else:
            lik=[]



        self.statusPanel.AppendText('done!\n\n')
        self.uncertainPars = (priors, priords, lhoods, lik)
        self.statusPanel.AppendText('press the start button on the main panel.\n')
        self.Donebutton.Disable()

    def OnSelAllButton(self, event):
        """
        When this button is clicked, it checks all items on the list.
        """
        n = self.varList.GetCount()
        for i in range(n):
            self.varList.Check(i)
        sel = sum(array([self.varList.IsChecked(i) for i in range(n)]))
        self.updatePriorList(sel)

    def OnVarListChecklistbox(self, event):
        """
        Every time an item is checked in the variable list box,
        it calls for an update of prior list box.
        """
        n = self.varList.GetCount()
        sel = sum(array([self.varList.IsChecked(i) for i in range(n)]))
        self.updatePriorList(sel)

    def OnUncertaintyMiniFrameClose(self, event):
        event.Skip()

    def OnVarListListbox(self, event):
        event.Skip()
