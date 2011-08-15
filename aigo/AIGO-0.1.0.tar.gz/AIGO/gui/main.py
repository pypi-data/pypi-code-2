"""
main.py

AIGO is a python library for
the Analysis and Inter-comparison of Gene Ontology functional annotations.
see (http://code.google.com/p/aigo).
        
Created by Michael Defoin-Platel on 21/02/2010.
Copyright (c) 2010. All rights reserved.

AIGO is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import wx
#import wx.lib.mixins.inspection


import matplotlib
#matplotlib.interactive( True )
matplotlib.use( 'WXAgg' )

from pylab import *

import sys
import os.path 

from AIGO import allAspect

from AIGO.Statistics              import registerStat
from AIGO.ReferenceSet            import RefSet
from AIGO.FunctionalAnnotation    import FuncAnnot
from AIGO.Plot                    import PlotFA, registerPlot
from AIGO.Randomize               import RandomizeFA
from AIGO.Report                  import ReportFA

from AIGO.go.OBO                  import readGOoboXML

from AIGO.utils.File              import createDir
from AIGO.utils.Execute           import batchExecute

from AIGO.gui                     import gui, popups, app, project, grid
from AIGO.gui.app                 import PNGtoBitmap

def createPlotFA(project):
    if not project.has_key('plotFA'):
        outDir="%s/Graph" % (project['directory'])
        createDir(outDir)
        project['plotFA']=PlotFA(xlabel="Functional Annotation", outDir=outDir, name=project['name'], organism=project['organism'], grid=True)


class eventStatus(dict):

    def clean(self):
        for k in self.all:
            self[k]=False

    def makeDirty(self, *args):
        for k in self.all:
            self[k]=True

    def notify(self, k):
        self[k]=True

    def __init__(self):
        self.all = ['All','Project','RefSet', 'GO', 'FA',
                    'CompareFA',
                    'CompareVennData','CompareFuncSimData',
                    'CompareVennPlot','CompareFuncSimPlot',
                    'CompareListData','CompareListDisplay',
                    'Analyse']
        self.makeDirty()

class CompareData(object):
    """
    A line in a Compare FA table
    """
    def __init__(self, **kwargs):
        self.attributeNames = kwargs.keys()
        self.__dict__.update(kwargs)

    def clone(self):
        "Return a deep copy of this object"
        d = {}
        for x in self.attributeNames:
            d[x] = getattr(self, x, None)

        return CompareData(**d)

def updateProject(myApp):
    if myApp.project.get('name', "")=="":
        myApp.frame.notebook.Enable(False)
        myApp.frame.notebook.notebook_Data.Enable(False)
    else:
        myApp.frame.notebook.Enable(True)
        myApp.frame.notebook.notebook_Data.Enable(True)
        myApp.status['Project']=myApp.project['name']
        
    if myApp.project.get('organism', "") == "":
        myApp.frame.notebook.Enable(False)
        myApp.frame.notebook.notebook_Data.Enable(False)
    else:
        myApp.status['Organism']=myApp.project['organism']

def updateRefSet(myApp):
    if myApp.project.has_key('refSet') and len(myApp.project['refSet']) > 0:
        myApp.frame.notebook.box_RefSet.SetValue(myApp.project['refSet'].fileName)
        myApp.frame.notebook.button_AddFA.Enable(True)
        myApp.status['GP']="%d" % len(myApp.project['refSet'])
    else:
        myApp.frame.notebook.button_AddFA.Enable(False)
        myApp.status['GP']="0"
        

def updateGeneOntology(myApp):
    if not myApp.project.has_key('GO'):
        myApp.frame.notebook.button_AddFA.Enable(False)
        myApp.status['GO']="empty"
    else:
        myApp.frame.notebook.box_GO.SetValue(myApp.project['GO'].fileName)
        myApp.status['GO']="loaded"

def updateFunctionalAnnotation(myApp):
    if len(myApp.project.get('allFA', []))==0:
        myApp.frame.notebook.list_FA.Enable(False)
        myApp.frame.notebook.button_RemoveFA.Enable(False)
        myApp.frame.notebook.button_LoadFA.Enable(False)
    else:
        myApp.frame.notebook.list_FA.DeleteAllItems()
        myApp.frame.notebook.list_FA.Enable(True)
        for FA in myApp.project['allFA']:
            myApp.frame.notebook.button_RemoveFA.Enable(True)
            if FA.isEmpty():
                myApp.frame.notebook.button_LoadFA.Enable(True)

            myApp.frame.notebook.list_FA.Append([FA.status, FA.name, os.path.split(FA.fileName)[1], FA.fileType])

        myApp.status['FA']="%s" % len(myApp.project['allFA'])

def updateAnalysis(myApp):
    loadedFA=myApp.project.getLoadedFA()
    
    myApp.frame.notebook.notebook_Analysis.Enable(False)
    if len(loadedFA) > 0 :
        myApp.frame.notebook.notebook_Analysis.Enable(True)

        #Statistics
        for aspect in allAspect:
            g=getattr(myApp.frame.notebook, 'grid_%s' % aspect)

            allStatistics=[statistics for statistics in myApp.workflow if myApp.viewStat]
            rowLabels=registerStat.getNames(allStatistics)
            colLabels=[FA.name for FA in loadedFA]

            g.UpdateData(aspect, loadedFA, allStatistics, colLabels, rowLabels)


def updateCompare_FA(myApp):
    loadedFA=myApp.project.getLoadedFA()

    for name in ["FA1", "FA2"]:
        lst=getattr(myApp.frame.notebook, 'combo_box_Compare_%s' % name)
        lst.Clear()
        lst.AppendItems([FA.name for FA in loadedFA])
        #Add an empty choice for the second FA
    lst.Append('')

def updateCompare_VennData(myApp):
    loadedFA=myApp.project.getLoadedFA()
    
    myApp.frame.notebook.notebook_Compare.Enable(False)
    if len (loadedFA) > 0:
        myApp.frame.notebook.notebook_Compare.Enable(True)

        if len(loadedFA) >= 2:

            if myApp.project['compareFA'].has_key('venn'):
                ch=myApp.popup.choice(myApp.frame, "Venn diagrams data exist, do you want to update ?")
            else:
                ch=myApp.popup.choice(myApp.frame, "At least two FAs have been loaded, do you want to compute Venn diagrams  ?")
            if ch.accepted==True:
                myApp.project['compareFA'].venn(loadedFA)


def updateCompare_FuncSimData(myApp):
    loadedFA=myApp.project.getLoadedFA()
    
    myApp.frame.notebook.notebook_Compare.Enable(False)
    if len (loadedFA) > 0:
        myApp.frame.notebook.notebook_Compare.Enable(True)

        if len(loadedFA) >= 2:

            if myApp.project['compareFA'].has_key('funcSim'):
                ch=myApp.popup.choice(myApp.frame, "Functional similarity data exist, do you want to update ?")
            else:
                ch=myApp.popup.choice(myApp.frame, "At least two FAs have been loaded, do you want to compute Functional Similarity  ?")
            if ch.accepted==True:
                myApp.project['compareFA'].funcSim(loadedFA)


        for name in ["FA1", "FA2"]:
            lst=getattr(myApp.frame.notebook, 'combo_box_Compare_%s' % name)
            lst.Clear()
            lst.AppendItems([FA.name for FA in loadedFA])
        #Add an empty choice for the second FA
        lst.Append('')


def updateCompare_VennPlot(myApp):
    loadedFA=myApp.project.getLoadedFA()

    if len (loadedFA) > 0 and len(loadedFA) <=3 and myApp.project['compareFA'].has_key('venn'):
        createPlotFA(myApp.project)                    
        allFigName=myApp.project['plotFA'].venn(myApp.project['compareFA'], loadedFA, fontsize=32)
        for aspect in allAspect:
            bmp=getattr(myApp.frame.notebook, 'bitmap_Venn_%s' % aspect)
            size=bmp.GetSize().Get()
            bmp.SetBitmap(PNGtoBitmap(allFigName[aspect], resize=size))
    else:
        for aspect in allAspect:
            bmp=getattr(myApp.frame.notebook, 'bitmap_Venn_%s' % aspect)
            size=bmp.GetSize().Get()
            bmp.SetBitmap(myApp.AIGOBmp)

def updateCompare_FuncSimPlot(myApp):

    if myApp.project['compareFA'].has_key('allFA') and len(myApp.project['compareFA']['allFA'])==2:
        name1,name2=myApp.project['compareFA']['allFA']
        FA1=myApp.project.getFA(name1)
        FA2=myApp.project.getFA(name2)

        createPlotFA(myApp.project)                    
        allFigName=myApp.project['plotFA'].funcSymSim(myApp.project['compareFA'], [FA1, FA2])
        for aspect in allAspect:
            bmp=getattr(myApp.frame.notebook, 'bitmap_FuncSim_%s' % aspect)
            size=bmp.GetSize().Get()
            bmp.SetBitmap(PNGtoBitmap(allFigName[aspect][(name1,name2)], resize=size))
    else:
        for aspect in allAspect:
            bmp=getattr(myApp.frame.notebook, 'bitmap_FuncSim_%s' % aspect)
            size=bmp.GetSize().Get()
            bmp.SetBitmap(myApp.AIGOBmp)
        

def updateCompare_ListData(myApp):
    loadedFA=myApp.project.getLoadedFA()

    names=()
    if myApp.project['compareFA'].has_key('allFA'):
        names=tuple(myApp.project['compareFA']['allFA'])

    if len(names)>0:

        if not myApp.project['compareFA'].has_key('data'):
            myApp.project['compareFA']['data']=dict()

        for aspect in allAspect:
            if aspect=="All_aspects_of_GO":
                continue

            if not myApp.project['compareFA']['data'].has_key(aspect):
                myApp.project['compareFA']['data'][aspect]=dict()

            if len(names)==1:
                FA1=myApp.project.getFA(names[0])
                l=list()
                for gp in FA1.GPtoGO[aspect]:
                    l.append(CompareData(gp=gp, nb1=len(FA1.GPtoGO[aspect][gp]), nb2="", funcSim=""))
                    
                myApp.project['compareFA']['data'][aspect][names]=l
                
            else:
                name1,name2=names
                FA1=myApp.project.getFA(name1)
                FA2=myApp.project.getFA(name2)
                
                l=list()
                for gp in myApp.project['compareFA']['funcSim'][aspect][(name1,name2)]:
                    d1,d2=myApp.project['compareFA']['funcSim'][aspect][(name1,name2)][gp]
                    l.append(CompareData(gp=gp, nb1=len(FA1.GPtoGO[aspect][gp]), nb2=len(FA2.GPtoGO[aspect][gp]), funcSim=(d1+d2)/2.))

                myApp.project['compareFA']['data'][aspect][names]=l

def updateCompare_ListDisplay(myApp):

    names=()
    if myApp.project['compareFA'].has_key('allFA') and myApp.project['compareFA'].has_key('data'):
        names=myApp.project['compareFA']['allFA']
        if not type(names)==tuple:
            names=tuple(names)
            
    for aspect in allAspect:
        if aspect=="All_aspects_of_GO":
            continue
        lst=getattr(myApp.frame.notebook, 'list_ctrl_Compare_%s' % aspect)

        if len(names) > 0:
            lst.SetObjects(myApp.project['compareFA']['data'][aspect][names])
        else:
            lst.SetObjects([])

                        
def updatePlot(myApp):
    loadedFA=myApp.project.getLoadedFA()

    myApp.frame.notebook.notebook_Plot.Enable(False)

    myApp.frame.notebook.combo_PlotStat.Clear()
    for statistics in registerStat.getAll():

        OK=False
        for FA in loadedFA:
            if FA.has_key(statistics):
                myApp.frame.notebook.notebook_Plot.Enable(True)
                OK=True
                break

        if OK:
            myApp.frame.notebook.combo_PlotStat.Append(registerStat.getName(statistics))
            lastType=myApp.frame.notebook.combo_PlotType.GetValue()
            myApp.frame.notebook.combo_PlotType.Clear()
            allTypes=registerPlot.getType(statistics)                
            myApp.frame.notebook.combo_PlotType.AppendItems(allTypes)
            if lastType in allTypes:
                myApp.frame.notebook.combo_PlotType.SetValue(lastType)
            else:
                myApp.frame.notebook.combo_PlotType.SetValue(allTypes[0])


#==============================================================================

class MyApp(app.AIGOApp):

    def OnInit(self):
        super(MyApp,self).OnInit(doSplash=False)

        self.project = project.Project()

        self.status = dict()

        self.event = eventStatus()
        
        self.updateStatus()

        #fileName="/home/dpm/projects/Matt/AIGO-1.0/example-data/Test/Matt.aigo"
        #self.project.load(fileName)
        #self.event.notify("All")
        #self.updateStatus()

        return True

    def updateStatus(self):

        #New project
        if self.event['Project'] or self.event['All']:
            updateProject(self)

        #Set of gene products
        if self.event['RefSet'] or self.event['All']:
            updateRefSet(self)       

        #Gene Ontology
        if self.event['GO'] or self.event['All']:
            updateGeneOntology(self)

        #Functional Annotation
        if self.event['FA'] or self.event['All']:
            updateFunctionalAnnotation(self)
        
        #Analysis
        if self.event['FA'] or self.event['Analyse'] or self.event['All']:
            updateAnalysis(self)
                     
        #Compare
        if self.event['FA'] or self.event['All']:
            updateCompare_FA(self)
            
        if self.event['CompareVennData'] or self.event['FA'] or self.event['All']:
            updateCompare_VennData(self)

        if self.event['CompareFuncSimData'] or self.event['FA'] or self.event['All']:
            updateCompare_FuncSimData(self)

        if self.event['CompareVennPlot'] or self.event['FA'] or self.event['All']:
            updateCompare_VennPlot(self)

        if self.event['CompareFuncSimPlot'] or self.event['FA'] or self.event['All']:
            updateCompare_FuncSimPlot(self)

        if self.event['CompareListData'] or self.event['FA'] or self.event['All']:
            updateCompare_ListData(self)
            
        if self.event['CompareListDisplay'] or self.event['FA'] or self.event['All']:
            updateCompare_ListDisplay(self)

        #Plot
        if self.event['FA'] or self.event['Analyse'] or self.event['All']:
            updatePlot(self)
                
        #-----------------------------------
        self.event.clean()
        self.changeStatus()

    def changeStatus(self):
        self.status['Status']=self.project.status
        
        for f,s in self.status.items():
            i=self.statusField.index(unicode(f))
            b=self.frame.statusbar.GetStatusText(i).split(':')[0]
            self.frame.statusbar.SetStatusText(':'.join([b,s]), i)

               
    #-----------------------------------------------------
    #                   EVENT  HANDLERS
    #-----------------------------------------------------

    #Menus
    def MenuNew(self, event):
        self.npFrame.Show(True)
        self.npFrame.SetFocus()

    def MenuOpen(self, event):
        fileName = ""
        
        dlg = wx.FileDialog(self.frame, message="Choose a project file")
          
        if dlg.ShowModal() == wx.ID_OK:
            
            # get the new filename from the dialog
            fileName = dlg.GetPath()
            dlg.Destroy()  # best to do this sooner than later
            
            if fileName:
                self.project.load(fileName)
                self.event.notify("All")
                self.updateStatus()


    def MenuSave(self, event):
        import os.path
        fileName=os.path.join(self.project['directory'], "%s.aigo" % self.project['name'])
        self.project.save(fileName)
        self.updateStatus()

    def MenuQuit(self, event):
        f=self.GetTopWindow()
        f.DestroyChildren()
        f.Destroy()

        self.Exit()
        

    def MenuAbout(self, event):
        description = """AIGO is a python library for the Analysis and Inter-comparison of Gene Ontology functional annotations."""
                
        licence = """AIGO is free software: you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation, either version 3 of the License, or
        (at your option) any later version.

        This program is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.
        
        You should have received a copy of the GNU General Public License
        along with this program.  If not, see <http://www.gnu.org/licenses/>."""


        info = wx.AboutDialogInfo()
        info.SetIcon(wx.Icon('%s/AIGO.png' % self.guiDir, wx.BITMAP_TYPE_PNG))
        info.SetName('AIGO')
        info.SetVersion('1.0')
        info.SetDescription(description)
        info.SetCopyright('(C) 2010 Michael Defoin-Platel')
        info.SetWebSite('http://code.google.com/p/aigo')
        info.SetLicence(licence)
        info.AddDeveloper('Michael Defoin-Platel')
        info.AddDeveloper('Matthew Hindle')
        info.AddDocWriter('Michael Defoin-Platel')
        info.AddArtist('Michael Defoin-Platel')
        info.AddTranslator('Michael Defoin-Platel')
        
        wx.AboutBox(info)

    #New project----------------------
    def OnNewProjectDirChoose(self, event):
        dirName = ""
        dlg = wx.DirDialog(self.npFrame, message="Choose a directory")
          
        if dlg.ShowModal() == wx.ID_OK:
            dirName = dlg.GetPath()
            dlg.Destroy()
            
            if dirName:
                self.npFrame.box_Directory.ChangeValue(dirName)

        self.npFrame.Show(True)
                
    def OnNewProjectOK(self, event):
        if self.npFrame.box_NewProject.IsEmpty():
            self.popup.error(self.frame, "can't create a project with an empty name")
        if self.npFrame.box_Directory.IsEmpty():
            self.popup.error(self.frame, "can't create a project with an empty directory")
        elif self.npFrame.box_Organism.IsEmpty():
            self.popup.error(self.frame, "can't create a project without a reference organism")
        else:
            name=self.npFrame.box_NewProject.GetValue()
            directory=self.npFrame.box_Directory.GetValue()
            organism=self.npFrame.box_Organism.GetValue()
            self.project = project.Project(name=name, directory=directory, organism=organism)
            self.npFrame.Show(False)
            self.event.notify("Project")
            self.updateStatus()

    def OnNewProjectCancel(self, event):
        self.npFrame.Show(False)
    
    #Gene Ontology----------------------
    def OnBrowseGO(self, event):
        fileName = ""
        
        dlg = wx.FileDialog(self.frame, message="Choose a obo file",
                            defaultDir=self.project.get('directory', ""))
          
        if dlg.ShowModal() == wx.ID_OK:
            
            # get the new filename from the dialog
            fileName = dlg.GetPath()
            dlg.Destroy()  # best to do this sooner than later
            
            if fileName:
                self.frame.notebook.box_GO.ChangeValue(fileName)

    def OnLoadGO(self, event):
        fileName=self.frame.notebook.box_GO.GetValue()
        #refType=self.frame.notebook.radio_btn_GO.GetStringSelection()
        force=self.frame.notebook.checkbox_GO.GetValue()
        GO=readGOoboXML(fileName=fileName, force=force)
        self.project.addGO(GO)
        self.event.notify("GO")
        self.updateStatus()

    #Reference set--------------------
    def OnBrowseRefSet(self, event):
        fileName = ""
        
        dlg = wx.FileDialog(self.frame, message="Choose a gene product file",
                            defaultDir=self.project.get('directory', ""))
          
        if dlg.ShowModal() == wx.ID_OK:
            
            # get the new filename from the dialog
            fileName = dlg.GetPath()
            dlg.Destroy()  # best to do this sooner than later
            
            if fileName:
                self.frame.notebook.box_RefSet.ChangeValue(fileName)

    def OnLoadRefSet(self, event):
        fileName=self.frame.notebook.box_RefSet.GetValue()
        refType=self.frame.notebook.radio_btn_RefSet.GetStringSelection()
        refSet=RefSet(organism=self.project['organism'], fileName=fileName, refType=refType)
        self.project.addRefSet(refSet)
        self.event.notify("RefSet")
        self.updateStatus()

    #Add Functional Annotation--------------------
    def OnAddFA(self, event):
        self.FAFrame.Show(True)
        self.FAFrame.SetFocus()

    def OnRemoveFA(self, event):
        first=self.frame.notebook.list_FA.GetFirstSelected()
        if first==-1:
            self.popup.error(self.frame, "first select the FA you want to remove")

        current=first
        while not current==-1:
            name=self.frame.notebook.list_FA.GetItem(current,1).GetText()
            self.project.removeFA(name)
            current=self.frame.notebook.list_FA.GetNextSelected(current)

        self.event.notify("FA")
        self.updateStatus()

    def OnLoadFA(self, event):
        for FA in self.project['allFA']:
            if FA.isEmpty():
                FA.read()

        self.event.notify("FA")
        self.updateStatus()

    def OnFAFileChoose(self, event):
        fileName = ""
        
        dlg = wx.FileDialog(self.FAFrame, message="Choose a Functional Annotation file",
                            defaultDir=self.project.get('directory', ""))
          
        if dlg.ShowModal() == wx.ID_OK:
            
            # get the new filename from the dialog
            fileName = dlg.GetPath()
            dlg.Destroy()  # best to do this sooner than later
            
            if fileName:
                self.FAFrame.box_File.ChangeValue(fileName)

                
    def OnFAOK(self, event):
        if self.FAFrame.box_FA.IsEmpty():
            self.popup.error(self.frame, "can't add a FA without a valid name")
        elif self.FAFrame.box_FA.GetValue() in [FA.name for FA in self.project['allFA']]:
            self.popup.error(self.frame, "FA name must be unique")
        elif self.FAFrame.box_File.IsEmpty():
            self.popup.error(self.frame, "can't add a FA without a file name")
        else:
            name=self.FAFrame.box_FA.GetValue()
            fileName=self.FAFrame.box_File.GetValue()
            fileType=self.FAFrame.combo_box_FileType.GetValue()
            
            FA = FuncAnnot(name, self.project['refSet'], self.project['GO'],
                           organism=self.project['organism'],
                           fileName=fileName, fileType=fileType)
            self.project.addFA(FA)
            self.FAFrame.Show(False)
            
            self.event.notify("FA")
            self.updateStatus()

    def OnFACancel(self, event):
        self.FAFrame.Show(False)

    #Statistics--------------------
    def OnStatCheck(self, event):
        cb=event.GetEventObject()
        statistics=cb.GetName()
        lb=getattr(self.frame.notebook, 'label_%s' % statistics)
        bmp=getattr(self.frame.notebook, 'bitmap_%s' % statistics)
        
        if cb.GetValue():
            colour='BLACK'
            self.viewStat[statistics]=True
        else:
            self.viewStat[statistics]=False
            colour='GREY'
        cb.SetForegroundColour(colour)
        lb.SetForegroundColour(colour)
        bmp.Show(cb.GetValue())

        self.event.notify("Analyse")
        self.updateStatus()


    def OnStatApply(self, event):
        for statistics in self.workflow:

            if not self.viewStat[statistics]:
                continue

            cb=getattr(self.frame.notebook, 'checkbox_%s' % statistics)
            if cb.GetValue() and self.project.applyStat(statistics):
                bmp=getattr(self.frame.notebook, 'bitmap_%s' % statistics)
                bmp.SetBitmap(self.checkBmp)

            self.event.notify("Analyse")
            self.updateStatus()

    def OnStatExport(self, event):
        
        if not self.project.has_key('exportFA'):
            outDir="%s/Export" % (self.project['directory'])
            createDir(outDir)
            self.project['exportFA']= ReportFA(outDir=outDir,name=self.project['name'], organism=self.project['organism'])
            
        try:
            self.project['exportFA'].saveStatistics(self.project['allFA'] , [statistics for statistics in self.workflow if self.viewStat])
            self.popup.msg(self.frame, "Congratulations, statistics have been successfully exported to %s" % self.project['exportFA'].outDir, "Operation")            
        except :
            self.popup.error(self.frame, "failed to export statistics to %s" % self.project['exportFA'].outDir)            

                
    #Plot--------------------
    def OnStatPlot(self, event):

        createPlotFA(self.project)

        nameStat=self.frame.notebook.combo_PlotStat.GetValue()
        statistics=registerStat.getStat(nameStat)

        if hasattr(self.project['plotFA'], statistics):
            f=getattr(self.project['plotFA'], statistics)
            figName=f([FA for FA in self.project['allFA'] if FA.has_key(statistics)])

            #size=self.frame.notebook.bitmap_Plot.GetSize().Get()
            #self.frame.notebook.bitmap_Plot.SetBitmap(PNGtoBitmap(figName, resize=size))
            self.frame.notebook.bitmap_Plot.SetBitmap(PNGtoBitmap(figName))
            self.frame.notebook.bitmap_Plot.CenterOnParent(wx.HORIZONTAL)

    #Compare--------------------
    def OnCompareStat(self, event):

        names=set()
        for name in ["FA1", "FA2"]:
            lst=getattr(self.frame.notebook, 'combo_box_Compare_%s' % name)
            n=lst.GetValue()
            if not n=='':
                names.add(n)
                
        names=tuple(sort(list(names)))

        self.project['compareFA']['allFA']=names

        for aspect in allAspect:
            if aspect=="All_aspects_of_GO":
                continue
            if not self.project['compareFA'].has_key('data'):
                self.event.notify("CompareListData")
            elif not self.project['compareFA']['data'].has_key(aspect):
                self.event.notify("CompareListData")
            elif not self.project['compareFA']['data'][aspect].has_key(names):
                self.event.notify("CompareListData")

        self.event.notify("CompareVennPlot")
        self.event.notify("CompareFuncSimPlot")
        self.event.notify("CompareListDisplay")
        self.updateStatus()


    def OnUpdateVenn(self, event):
        self.event.notify("CompareVennData")
        self.event.notify("CompareVennDisplay")
        self.updateStatus()
                    

    def OnUpdateFuncSim(self, event):
        self.event.notify("CompareFuncSimData")
        self.event.notify("CompareFuncSimDisplay")
        self.updateStatus()

    def OnCompareView(self, event):

        if len(self.project['compareFA']['allFA'])==0:
            self.popup.error(self.frame, "must first select at least one Functional Annotation")
            return
                
        cb=event.GetEventObject()
        aspect=cb.GetName()
        
        lst=getattr(self.frame.notebook, 'list_ctrl_Compare_%s' % aspect)
        
        current=lst.GetFirstSelected()

        if current==-1:
            self.popup.error(self.frame, "you must first select the annotation set you want to see")
            return

        createPlotFA(self.project)

        outDir="%s/Annotation" % (self.project['directory'])
        createDir(outDir)

        gp=lst.GetItem(current,0).GetText()

        if len(self.project['compareFA']['allFA'])==1:
            FA1=self.project.getFA(self.project['compareFA']['allFA'][0])
        
            figName="%s/%s_%s_%s.png" % (outDir, gp, FA1.name, self.project['name'])
            ttl="%s annotations of %s from %s " % (aspect.replace("_", " "), gp, FA1.name)
            self.project['GO'].plot_InducedGraph(FA1.GPtoGO[aspect][gp], figName=figName, ttl="")
        else:
            FA1=self.project.getFA(self.project['compareFA']['allFA'][0])
            FA2=self.project.getFA(self.project['compareFA']['allFA'][1])
            
            figName="%s/%s_%s_%s_%s.png" % (outDir, gp, FA1.name, FA2.name, self.project['name'])
            ttl="%s annotations of %s from %s (green) and %s (red)" % (aspect.replace("_", " "), gp, FA1.name, FA2.name)
            self.project['GO'].compare_InducedGraph(FA1.GPtoGO[aspect][gp],FA2.GPtoGO[aspect][gp], figName=figName, ttl="")


        self.project['compareFA']['figName']=figName
        
        size=self.ViewFrame.bitmap.GetSize().Get()
        self.ViewFrame.bitmap.SetBitmap(PNGtoBitmap(figName, resize=size))
        self.ViewFrame.bitmap.CenterOnParent(wx.BOTH)
        self.ViewFrame.Show(True)

    def OnResizeView(self, event):

        if self.project.has_key('compareFA') and self.project['compareFA'].has_key('figName'):
            figName=self.project['compareFA']['figName']
            size=self.ViewFrame.bitmap.GetSize().Get()
            self.ViewFrame.bitmap.SetBitmap(PNGtoBitmap(figName, resize=size))
            self.ViewFrame.bitmap.CenterOnParent(wx.BOTH)

        event.Skip()
        wx.CallAfter(self.ViewFrame.Layout)

def startGUI():
    import pdb
    try:
        myApp = MyApp(0)
        #wx.lib.inspection.InspectionTool().Show()
        myApp.MainLoop()
        
    except:         
        e, m, tb = sys.exc_info()
        pdb.post_mortem(tb)
        
if __name__ == '__main__':
    startGUI()
