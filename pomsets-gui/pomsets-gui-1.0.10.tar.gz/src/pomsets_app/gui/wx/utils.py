import logging
import os
import uuid

import wx
import wx.xrc

import pomsets.definition as DefinitionModule

import pomsets_app.utils as AppUtilsModule

def manageHadoopConfiguration(contextManager, window):

    automaton = contextManager.automaton()
    
    resourcePath = contextManager.resourcePath()
    res =  wx.xrc.XmlResource(
        os.path.join(resourcePath, 'xrc', 'hadoop frame.xrc'))

    import pomsets_app.gui.widget.hadoop as WidgetModule
    dialog = WidgetModule.ConfigDialog(res, window)

    configuration = automaton.hadoopConfigurations().get('localhost', None)

    shouldCreateNewConfig = False
    if configuration is None:
        configuration = {'hostname':'localhost'}
        shouldCreateNewConfig = True

    # first get the existing values from the automaton
    # populate the dialog
    hadoopHomeTextCtrl = dialog.getWidget('hadoopHomeTextCtrl')
    defaultHadoopHome = configuration.get('home', '')
    
    hadoopHomeTextCtrl.SetValue(defaultHadoopHome)
    
    relativeToHadoopHomeCheckBox = dialog.getWidget('relativeToHadoopHomeCheckBox')
    isRelativeToHadoopHome = configuration.get(
        'streaming jar is relative to home', True)
    relativeToHadoopHomeCheckBox.SetValue(isRelativeToHadoopHome)
    
    streamingJarTextCtrl = dialog.getWidget('streamingJarTextCtrl')
    defaultStreamingJar = ''
    if isRelativeToHadoopHome:
        defaultStreamingJar = os.path.join(
            'contrib', 'streaming',
            'hadoop-0.20.1-streaming.jar')
    else:
        defaultStreamingJar = os.path.join(
            defaultHadoopHome, 'contrib', 'streaming',
            'hadoop-0.20.1-streaming.jar')
        
    streamingJarTextCtrl.SetValue(
        configuration.get('streaming jar', defaultStreamingJar))
    
    try:
        if dialog.ShowModal() == wx.ID_OK:

            configuration['home'] = hadoopHomeTextCtrl.GetValue()
            
            # TODO:
            # handle the checkbox for whether the path
            # is relative to hadoop home
            # if it is, then prepend hadoop home
            isRelativeToHadoopHome = relativeToHadoopHomeCheckBox.GetValue()
            configuration['streaming jar is relative to home'] = isRelativeToHadoopHome
            configuration['streaming jar'] = streamingJarTextCtrl.GetValue()
            
            if shouldCreateNewConfig:
                logging.debug("need to implement when no configuration found")
                print "need to implement when no configuration found"
                automaton.addHadoopConfiguration(configuration)

            # save out to file
            configData = AppUtilsModule.createNewConfigDataObject()
            automaton.addConfigToSave(configData)
            AppUtilsModule.saveConfig(configData)
            pass
        pass
    except Exception, e:
        logging.error("errored on managing Hadoop configuration >> %s" % e)
        raise
    finally:
        dialog.Destroy()
    
    return

def manageEc2Credentials(contextManager, window):

    automaton = contextManager.automaton()

    resourcePath = contextManager.resourcePath()
    res =  wx.xrc.XmlResource(
        os.path.join(resourcePath, 'xrc', 'euca2ools frame.xrc'))


    import pomsets_app.gui.widget.eucalyptus as WidgetModule
    dialog = WidgetModule.ConfigDialog(res, window)

    # first get the existing values from the automaton
    # and populate the dialog
    # valueKeyPair
    # valueIdentityFile (need a file browser)
    # valueImageId
    keyPairTextCtrl = dialog.getWidget('ValueKeyPair')
    identityFileTextCtrl = dialog.getWidget('ValueIdentityFile')
    textCtrlURL = dialog.getWidget('textCtrlURL')
    textCtrlAccessKey = dialog.getWidget('textCtrlAccessKey')
    textCtrlSecretKey = dialog.getWidget('textCtrlSecretKey')

    shouldCreateNew = False
    try:
        controllerValues = automaton.getCloudControllerCredentialsForAPI('euca2ools')
        keyPairTextCtrl.SetValue(controllerValues.get('user key pair', ''))
        identityFileTextCtrl.SetPath(controllerValues.get('identity file', ''))
        textCtrlURL.SetValue(controllerValues.get('url', ''))
        textCtrlAccessKey.SetValue(controllerValues.get('access key', ''))
        textCtrlSecretKey.SetValue(controllerValues.get('secret key', ''))

    except KeyError, e:
        # that means there hasnt been any defined
        shouldCreateNew = True
        pass

    try:
        if dialog.ShowModal() == wx.ID_OK:

            if shouldCreateNew:
                controllerValues = {}

            controllerValues['user key pair'] = keyPairTextCtrl.GetValue()
            controllerValues['identity file'] = identityFileTextCtrl.GetPath()

            controllerValues['url'] = textCtrlURL.GetValue()
            controllerValues['access key'] = textCtrlAccessKey.GetValue()
            controllerValues['secret key'] = textCtrlSecretKey.GetValue()

            if shouldCreateNew:
                automaton.addCloudControllerCredential(
                    'Eucalyptus', 'euca2ools', **controllerValues)
                pass

            # save out to file
            configData = AppUtilsModule.createNewConfigDataObject()
            automaton.addConfigToSave(configData)
            AppUtilsModule.saveConfig(configData)
            
            pass
        pass
    except Exception, e:
        logging.error("errored on managing EC2 credentials >> %s" % e)
        raise
    finally:
        dialog.Destroy()

    return



def editParameter(contextManager, window, parameterToEdit):
    
    automaton = contextManager.automaton()

    resourcePath = contextManager.resourcePath()
    res =  wx.xrc.XmlResource(
        os.path.join(resourcePath, 'xrc', 'edit parameter dialog.xrc'))

    import pomsets_app.gui.widget.definition as WidgetModule
    dialog = WidgetModule.EditDefinitionParameterDialog(res, window)

    try:
        dialog.populate()
        dialog.setObjectToEdit(parameterToEdit)
        if dialog.ShowModal() == wx.ID_OK:

            # TODO:
            # modify the definition and save it
            logging.debug("should edit parameter")
            pass
        pass
    except Exception, e:
        logging.error("errored on editing parameter %s" % e)
        raise
    finally:
        dialog.Destroy()
        
        
    return


def createDefinition(contextManager, window):
    
    # autogenerate the name of the definition
    id = uuid.uuid4().hex
    name = '_'.join(['definition', id[:3]])
    definition = DefinitionModule.createShellProcessDefinition(
        name=name, inputParameters={}
    )
    definition.id(id)

    import pomsets.context as ContextModule
    context = ContextModule.Context()
    context.pomset(definition)
    context.isModified(False)
    contextManager.transientLibrary().addPomsetContext(context)

    return context

    
    
def editDefinition(contextManager, window, definitionToEdit):
    
    automaton = contextManager.automaton()

    resourcePath = contextManager.resourcePath()
    res =  wx.xrc.XmlResource(
        os.path.join(resourcePath, 'xrc', 'edit definition dialog.xrc'))

    import pomsets_app.gui.widget.definition as WidgetModule
    dialog = WidgetModule.EditAtomicDefinitionDialog(res, window)
    dialog.contextManager = contextManager
    
    try:
        dialog.populate()
        # dialog.setObjectToEdit(definitionToEdit)
        contextToEdit = contextManager.getContextForDefinition(definitionToEdit)
        dialog.setObjectToEdit(contextToEdit)
    
        if dialog.ShowModal() == wx.ID_OK:

            # TODO:
            # modify the definition and save it
            logging.debug("should edit definition")
            pass
        pass
    except Exception, e:
        logging.error("errored on editing definition >> %s" % e)
        raise
    finally:
        dialog.Destroy()
        
        
    return


"""
def editDefinitionList(contextManager, window):
    
    
    # TODO:
    # either need to display a dialog box
    # and ask the user to create an active pomset
    # or don't allow the user to call this in the first place
    # which can be done by disabling the menu
    
    automaton = contextManager.automaton()

    resourcePath = contextManager.resourcePath()
    res =  wx.xrc.XmlResource(
        os.path.join(resourcePath, 'xrc', 'definition list dialog.xrc'))

    dialog = WidgetModule.DefinitionListDialog(res, window)
    dialog.contextManager = contextManager
    
    try:
        dialog.populateListBox()
        if dialog.ShowModal() == wx.ID_OK:

            # TODO:
            # modify the definition and save it
            logging.debug("should edit definitions list")
            pass
        pass
    except Exception, e:
        logging.error("errored on editing definitions list" % e)
        raise
    finally:
        dialog.Destroy()
        
        
    return
"""



def addNode(contextManager, definition, name, position):

    node = contextManager.createNewNode(
        name=name, definitionToReference=definition)

    # TODO:
    # move elsewhere, so that we do not need to import 
    # the event module here
    import pomsets_app.gui.event as EventModule

    # post the event to update the GUI
    guiEvent = EventModule.NodeCreatedEvent(
        object=node,
        position=position,
        contextManager=contextManager)
    contextManager.postEvent(guiEvent)
    return


def selectDefinitionAndAddNode(contextManager, window, event):
    
    # display a dialog box to query the user for info
    #import pomsets_app.gui.widget.definition as WidgetModule
    #dialog = WidgetModule.SelectDefinitionDialog(
    #    window,
    #    WidgetModule.ID_DIALOG_SELECTDEFINITION, 
    #    "Select a definition")
    resourcePath = contextManager.resourcePath()
    res =  wx.xrc.XmlResource(
        os.path.join(resourcePath, 'xrc', 'select definition.xrc'))
    import pomsets_app.gui.widget.definition as WidgetModule
    dialog = WidgetModule.SelectDefinitionDialog(res, window)

    # self.event is the event originating from the contextual menu
    # dialog.event = self.event
    dialog.contextManager = contextManager
    
    try:
        dialog.populate()
        if dialog.ShowModal() == wx.ID_OK:
            definition = dialog.selectedDefinition
            name = dialog.nodeName
            
            # need to create a new point object
            # because somehow the values get corrupted
            position = wx.Point(event.GetEventObject().event.GetX(),
                                event.GetEventObject().event.GetY())

            addNode(contextManager, definition, name, position)
        pass
    except Exception, e:
        logging.error("errored on selecting a definition >> %s" % e)
        raise
    finally:
        dialog.Destroy()
    
    return


def selectPathToSavePomsetDefinition(contextManager, window, title=None):

    dialog = wx.FileDialog(window,
                           title or "",
                           os.getcwd(), "", "*.pomset", 
                           wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)

    try:
        if dialog.ShowModal() == wx.ID_OK:
            path=dialog.GetPath()
            #contextManager.savePomsetAs(
            #    path=path
            #)
            return path
        pass
    except Exception, e:
        # TODO: 
        # should show an error dialog box here

        logging.error("errored on saving pomset >> %s" % e)
        raise e
    finally:
        dialog.Destroy()

    # reaches here if the user cancelled operation
    return


def selectPathToLoadPomsetDefinition(contextManager, window, title=None):
    
    # pull up the GUI to query the user for the pomset pickle to load
    # once the information is retrieved
    # should construct a command 
    # display a dialog box to query the user for info
    dialog = wx.FileDialog(window,
                           title or "",
                           os.getcwd(), "", "*.pomset", wx.OPEN)
    
    try:
        if dialog.ShowModal() == wx.ID_OK:
            path=dialog.GetPath()
            
            return path
        pass
    except Exception, e:
        logging.error("errored on loading pomset >> %s" % e)
        raise
    finally:
        dialog.Destroy()
        
    # we reach here if the user cancelled the operation
    return



def editReferenceDefinition(contextManager, window, 
                            definitionToEdit, parameterId=None):
    
    automaton = contextManager.automaton()

    resourcePath = contextManager.resourcePath()
    res =  wx.xrc.XmlResource(
        os.path.join(resourcePath, 'xrc', 'edit task dialog.xrc'))

    import pomsets_app.gui.widget.definition as WidgetModule
    dialog = WidgetModule.EditReferenceDefinitionDialog(res, window)
    dialog.contextManager = contextManager
    
    try:
        dialog.setObjectToEdit(definitionToEdit)
        if parameterId is not None:
            dialog.selectParameter(parameterId)
            dialog.populateParameterValues()
            
        if dialog.ShowModal() == wx.ID_OK:

            # TODO:
            # modify the definition and save it
            logging.debug("should edit definition")
            pass
        pass
    except Exception, e:
        logging.error("errored on editing definition >> %s" % e)
        raise
    finally:
        dialog.Destroy()
        
        
    return


def showAboutDialog(contextManager):

    frame = contextManager.app().GetTopWindow()

    # First we create and fill the info object
    from wx.lib.wordwrap import wordwrap

    info = wx.AboutDialogInfo()
    info.Name = "pomsets"
    info.Version = "0.1.0"
    info.Copyright = u"\u00A9 2010 michael j pan"
    info.Description = wordwrap(
        "pomsets is a workflow management program for your cloud.",
        250, wx.ClientDC(frame))
    info.WebSite = ("http://pomsets.org", "pomsets home page")
    info.Developers = [ "michael j pan" ]

    licenseText = "See http://pomsets.org/License for licensing options."
    info.License = wordwrap(licenseText, 250, wx.ClientDC(frame))

    # Then we call wx.AboutBox giving it that info object
    wx.AboutBox(info)
    
    return
