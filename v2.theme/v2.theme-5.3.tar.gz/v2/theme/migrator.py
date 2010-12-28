"""XML migration script by David Jonas
This script migrates XML files into Plone Objects according to V2 Migration Structure"""

import libxml2
import urllib2
import AccessControl
import transaction
import time
import sys
from DateTime import DateTime
from plone.i18n.normalizer import idnormalizer
from Testing.makerequest import makerequest
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_inner
try:
    from collective.contentleadimage.config import IMAGE_FIELD_NAME
    from collective.contentleadimage.config import IMAGE_CAPTION_FIELD_NAME
    from collective.contentleadimage.interfaces import ILeadImageable
    import collective.contentleadimage
    LEADIMAGE_EXISTS = True
except ImportException:
    LEADIMAGE_EXISTS = False
    



class PersonItem:
    """ Class to store a person from the xml file"""
    def __init__(self):
        self.firstname = ""
        self.middlename = ""
        self.lastname = ""
        self.intro = ""
        self.body = ""
        self.tags = ""
        self.nickname = ""
        self.nationality = ""
        self.image = ""
        self.caption = ""
        self.person_class = ""
        self.links = []
    
    
    def firstName(self):
        if self.firstname != "":
            return self.firstname
        elif self.nickname != "":
            return self.nickname
        elif self.lastname != "":
            self.firstname = self.lastname;
            self.lastname = ""
            return self.firstname
        elif self.middlename != "":
            self.firstname = self.middlename;
            self.middlename = ""
            return self.firstname
        else:
            return ""
            
    
    def fullName(self):
        return self.firstname + " " + self.middlename + " " + self.lastname
    
    def description(self):
        nationality = ""
        
        if self.nationality != "":
            nationality = " (%s)"%(self.nationality,)
            
        #Prepare person_class for display
        #This means replacing every two spaces by one space, then comma separating, then adding a " and " in the last item
        person_class_list = self.person_class.replace("  ", " ").split(" ")
        person_class_list_last = person_class_list[len(person_class_list)-1]
        person_class = self.person_class.replace("  ", " ").replace(" ", ", ").replace(", " + person_class_list_last, " and " + person_class_list_last)
        
        if self.person_class != "":
            if self.person_class[:1] == "a" or self.person_class[:1] == "e" or self.person_class[:1] == "i" or self.person_class[:1] == "o" or self.person_class[:1] == "u":
                return self.fullName() + nationality + " is an " + person_class + "."
            else:
                return self.fullName() + nationality + " is a " + person_class + "."
        else:
            if nationality == "":
                return ""
            else:
                return self.fullName() + nationality + "."
        
    def Body(self):
        links = ""
        if len(self.links) > 0:
            links = "<br /><br /><b>Links:</b><br />"
            for link in self.links:
                links = links + "<br />" + "<a href=\"" + link + "\">" + link + "</a>"
        return self.intro + self.body + links



class ImageItem:
    """Class to store an Image from the xml file"""
    def __init__(self):
        self.title = ""
        self.subtitle = ""
        self.uri = ""
        self.tags = ""
        self.domains = ""
        
        
class WorkItem:
    """Class to store a Work from the xml file"""
    def __init__(self):
        self.title = ""
        self.subtitle = ""
        self.body = ""
        self.tags = ""
        self.image = ""
        self.caption = ""
        self.link = ""
        self.year = ""
        self.description = ""
        
    def Title(self):
        if self.year != "":
            return self.title + " (%s)"%self.year
        else:
            return self.title
        
    def Body(self):
        if self.link == "":
            return self.body
        else:
            return self.body + "<br /><a href=\"" + self.link + "\">" + self.link + "</a>"
        

class EventItem:
    """Class to store an Event from the xml file"""
    def __init__(self):
        self.title = ""
        self.subtitle = ""
        self.body = ""
        self.tags = ""
        self.image = ""
        self.caption = ""
        self.location = ""
        self.startDate = ""
        self.endDate = ""
        self.description = ""
        self.link = ""
        self.event_class = ""
        
    def Description(self):
        if self.subtitle != "":
            return self.subtitle
        elif self.event_class != "":
            return self.event_class
        else:
            return ""

 
class OrganizationItem:
    """Class to store an Organization from the xml file"""
    def __init__(self):
        self.title = ""
        self.subtitle = ""
        self.body = ""
        self.tags = ""
        self.image = ""
        self.caption = ""
        self.link = ""
        self.organization_class = ""
        
    def Body(self):
        if self.link == "":
            return self.body
        else:
            return self.body + "<br /><a href=\"" + self.link + "\">" + self.link + "</a>"
        
    def description(self):         
        #Prepare organization_class for display
        #This means replacing every two spaces by one space, then comma separating, then adding a " and " in the last item
        organization_class_list = self.organization_class.replace("  ", " ").split(" ")
        organization_class_list_last = organization_class_list[len(organization_class_list)-1]
        organization_class = self.organization_class.replace("  ", " ").replace(" ", ", ").replace(", " + organization_class_list_last, " and " + organization_class_list_last)
        
        if self.organization_class != "":
            if self.organization_class[:1] == "a" or self.organization_class[:1] == "e" or self.organization_class[:1] == "i" or self.organization_class[:1] == "o" or self.organization_class[:1] == "u":
                return self.title + " is an " + organization_class.replace("_", " ") + ". " + self.subtitle
            else:
                return self.title + " is a " + organization_class.replace("_", " ") + ". " + self.subtitle
        else:
            return self.subtitle + "."
        
    
class PageItem:
    """Class to store a Page from the xml file"""
    def __init__(self):
        self.title = ""
        self.link = ""
        self.body = ""
        self.tags = ""
        self.image = ""
        self.caption = ""
        self.description = ""
        
    def Body(self):
        if self.link == "":
            return self.body
        else:
            return self.body + "<br /><a href=\"" + self.link + "\">" + self.link + "</a>"

class XMLMigrator:
    """ Gets an XML file, parses it and creates the content in the chosen plone instance """
 
    def __init__(self, portal, xmlFilePath, typeToCreate, folder):
        """Constructor that gets access to both the parsed file and the chosen portal"""
        print("INITIALIZING CONTENT MIGRATOR")
        #check if portal exists
        self.portal = portal
        
        #Parse the XML file
        self.xmlDoc = libxml2.parseFile(xmlFilePath)
        
        #Set the migration mode
        self.typeToCreate = typeToCreate
        
        #Save the path to the folder to migrate to
        self.folderPath = folder.split("/")
        
        #Initialize the counters for the log
        self.errors = 0 #Number of errors - failed to create an item
        self.created = 0 #Number of sucessfully created items
        self.skipped = 0 #Number of items skipped because another item with the same id already exists on that folder.
    
    def cleanUp(self):
        self.xmlDoc.freeDoc()
        return
    
    def getContainer(self):
        #if there is no folder info, fail.
        if len(self.folderPath) == 0:
            print("Folder check failed")
            return None
        
        #Set the container to the root object of the portal
        container = self.portal
        
        #Navigate the folders creating them if necessary
        for folder in self.folderPath:
            if hasattr(container, folder):
                container = container[folder]
            else:
                print ("== Chosen folder " + folder + " does not exist. Creating new folder ==")
                container.invokeFactory(type_name="Folder", id=folder, title="migration of type: " + self.typeToCreate)
                container = container[folder]
            
        return container

    def getOrCreateFolder(self, container, folderId, publish):
        #Get a folder if it exists or create it if it doesn't
        if folderId != "":
            try:
                if hasattr(container, folderId):
                        container = container[folderId]
                else:
                    print ("== Creating new folder ==")
                    container.invokeFactory(type_name="Folder", id=folderId, title=folderId)
                    container = container[folderId]
                    
                    #publish the folder if needed
                    if publish:
                        container.portal_workflow.doActionFor(container, "publish", comment="content automatically published by migrationScript")
                    
                return container
            except:
                print("Folder %s could not be created: %s"%(folderId, sys.exc_info()[1]))
                return None
        else:
            return None
            

    def addLeadImage(self, item, image):
        #set the lead image if necessary and if lead image product is installed
        if LEADIMAGE_EXISTS and image != "":
            #download and create the image
            try:
                imageFile = urllib2.urlopen(image)
                imageData = imageFile.read()
                urlSplit = image.split("/")
                filename = urlSplit[len(urlSplit)-1]
                
                #add the image as leadImage
                if ILeadImageable.providedBy(item):
                    field = aq_inner(item).getField(IMAGE_FIELD_NAME)
                    field.set(item, imageData, filename=filename)
                else:
                    print("Item type does not accept leadImage")
                
                #release the image file
                imageFile.close()
                return
            except:
                print "LeadImage URL not available. LeadImage not created because: (" + image + ")", sys.exc_info()[1]
                return
            
    def addLeadImageCaption(self, item, caption):
        #set the caption if necessary and if lead image product is installed
        if LEADIMAGE_EXISTS and caption != "":
            #add the caption
            try:
                if ILeadImageable.providedBy(item):
                    field = aq_inner(item).getField(IMAGE_CAPTION_FIELD_NAME) 
                    field.set(item, caption)
                else:
                    print("Item type does not accept leadImage therefore captions will be ignored")
            except:
                print "Error adding leadImage caption: ", sys.exc_info()[1]
        return


    def createPerson(self, person):
        transaction.begin()
        
        container = self.getContainer()
        dirtyId = person.firstname + " " + person.middlename + " "  + person.lastname
        counter = 1
        result = False
        
        if person.description() == "" or person.image == "" or person.Body() == "":
            container = self.getOrCreateFolder(container, "toReview", False)

        try:
            id = idnormalizer.normalize(unicode(dirtyId, "utf-8"))
            
            while hasattr(container, id) and id != "":
                print ("Object " + id + " already exists.")
                counter = counter+1
                dirtyId = person.firstname + " " + person.middlename + " "  + person.lastname + str(counter)
                id = idnormalizer.normalize(unicode(dirtyId, "utf-8"))
                print ("creating " + id + " instead")
            
            if counter > 1:
                container = self.getContainer()
                container = self.getOrCreateFolder(container, "toReview", False)
            
            #Check if Person exists
            if not hasattr(container, id):
                container.invokeFactory(type_name="Person", id=id, firstName=person.firstName(), middleName=person.middlename, lastName=person.lastname, description=person.description())
                
                #get the person after creating
                item = container[id]
                
                #set the body
                item.setText(person.Body())
                
                #Add leadImage to the person if possible
                self.addLeadImage(item, person.image)
                
                #Add caption to the person's leadImage if possible
                self.addLeadImageCaption(item, person.caption)
                
                #Add tags to Keywords/Categories
                item.setSubject(person.tags.split(","))
                
                #publish the person
                if person.description() != "" and person.image != "" and person.Body() != "" and counter == 1:
                    item.portal_workflow.doActionFor(item, "publish", comment="Content automatically published by migrationScript")
                
                # Commit transaction
                transaction.commit()
                # Perform ZEO client synchronization (if runnning in clustered mode)
                #app._p_jar.sync()
                
                result = True
                self.created = self.created + 1
                #print("== person created ==")
        except:
            self.errors = self.errors + 1
            print "Unexpected error on createPerson (" + dirtyId + "):", sys.exc_info()[1]
            transaction.abort()
            return result
            #raise
          
    
        if not result:
            transaction.abort()
            self.skipped = self.skipped + 1
            print("Skipped item: " + dirtyId)
        return result


    def createWork(self, work):
        transaction.begin()
        container = self.getContainer()
        dirtyId = work.Title()
        counter = 1
        result = False

        if work.subtitle == "" or work.image == "" or work.Body() == "":
            container = self.getOrCreateFolder(container, "toReview", False)

        try:
            id = idnormalizer.normalize(unicode(dirtyId, "utf-8"))
            
            while hasattr(container, id) and id != "":
                print ("Object " + id + " already exists.")
                counter = counter+1
                dirtyId = work.Title() + str(counter)
                id = idnormalizer.normalize(unicode(dirtyId, "utf-8"))
                print ("creating " + id + " instead")
            
            if counter > 1:
                container = self.getContainer()
                container = self.getOrCreateFolder(container, "toReview", False)
            
            #Check if Work exists
            if not hasattr(container, id):
                container.invokeFactory(type_name="Work", id=id, title=work.Title(), description=work.subtitle)
                
                #get the work after creating
                item = container[id]
                
                #set the body
                item.setText(work.Body())
                
                #Add leadImage to the work if possible
                self.addLeadImage(item, work.image)
                
                #Add caption to the work's leadImage if possible
                self.addLeadImageCaption(item, work.caption)
                
                #Add tags to Keywords/Categories
                item.setSubject(work.tags.split(","))
                
                #publish the work
                if work.subtitle != "" and work.image != "" and work.Body() != "" and counter == 1:
                    item.portal_workflow.doActionFor(item, "publish", comment="Content automatically published by migrationScript")
                
                # Commit transaction
                transaction.commit()
                # Perform ZEO client synchronization (if runnning in clustered mode)
                #app._p_jar.sync()
                
                result = True
                self.created = self.created + 1
                #print("== work created ==")
        except:
            self.errors = self.errors + 1
            print "Unexpected error on createWork (" +dirtyId+ "):", sys.exc_info()[1]
            transaction.abort()
            return result
            #raise
          
    
        if not result:
            self.skipped = self.skipped + 1
            print("Skipped item: " + dirtyId)
        return result


    def createOrganization(self, organization):
        transaction.begin()
        container = self.getContainer()
        dirtyId = organization.title
        counter = 1
        result = False
        
        if organization.description() == "" or organization.image == "" or organization.body == "":
            container = self.getOrCreateFolder(container, "toReview", False)

        try:
            id = idnormalizer.normalize(unicode(dirtyId, "utf-8"))
            
            while hasattr(container, id) and id != "":
                print ("Object " + id + " already exists.")
                counter = counter+1
                dirtyId = organization.title + str(counter)
                id = idnormalizer.normalize(unicode(dirtyId, "utf-8"))
                print ("creating " + id + " instead")
            
            if counter > 1:
                container = self.getContainer()
                container = self.getOrCreateFolder(container, "toReview", False)
            
            #Check if Organization exists
            if not hasattr(container, id):
                container.invokeFactory(type_name="Organization", id=id, title=organization.title, description=organization.description())
                
                #get the Organization after creating
                item = container[id]
                
                #set the body
                item.setText(organization.body)
                
                #Add leadImage to the organization if possible
                self.addLeadImage(item, organization.image)
                
                 #Add caption to the organization's leadImage if possible
                self.addLeadImageCaption(item, organization.caption)
                
                #Add tags to Keywords/Categories
                item.setSubject(organization.tags.split(","))
                
                #publish
                if organization.description() != "" and organization.image != "" and organization.body != "" and counter == 1:
                    item.portal_workflow.doActionFor(item, "publish", comment="Content automatically published by migrationScript")
                
                # Commit transaction
                transaction.commit()
                # Perform ZEO client synchronization (if runnning in clustered mode)
                #app._p_jar.sync()
                
                result = True
                self.created = self.created + 1
                #print("== Organization created ==")
        except:
            self.errors = self.errors + 1
            print "Unexpected error on createOrganization (" +dirtyId+ "):", sys.exc_info()[1]
            transaction.abort()
            return result
            #raise
          
    
        if not result:
            self.skipped = self.skipped + 1
            print("Skipped item: " + dirtyId)
        return result


    def createPage(self, page):
        transaction.begin()
        container = self.getContainer()
        dirtyId = page.title
        counter = 1
        result = False
        
        if page.description == "" or page.image == "" or page.Body() == "":
            container = self.getOrCreateFolder(container, "toReview", False)

        try:
            id = idnormalizer.normalize(unicode(dirtyId, "utf-8"))
            
            while hasattr(container, id) and id != "":
                print ("Object " + id + " already exists.")
                counter = counter+1
                dirtyId = page.title + str(counter)
                id = idnormalizer.normalize(unicode(dirtyId, "utf-8"))
                print ("creating " + id + " instead")
            
            if counter > 1:
                container = self.getContainer()
                container = self.getOrCreateFolder(container, "toReview", False)
            
            #Check if Page exists
            if not hasattr(container, id):
                container.invokeFactory(type_name="Document", id=id, title=page.title, description=page.description)
                
                #get the Organization after creating
                item = container[id]
                
                #set the body
                item.setText(page.Body())
                
                #Add leadImage to the organization if possible
                self.addLeadImage(item, page.image)
                
                 #Add caption to the organization's leadImage if possible
                self.addLeadImageCaption(item, page.caption)
                
                #Add tags to Keywords/Categories
                item.setSubject(page.tags.split(","))
                
                #publish
                if page.description != "" and page.image != "" and page.Body() != "" and counter == 1:
                    item.portal_workflow.doActionFor(item, "publish", comment="Content automatically published by migrationScript")
                
                # Commit transaction
                transaction.commit()
                # Perform ZEO client synchronization (if runnning in clustered mode) Not doing this because now its running as a External Metod instead
                #app._p_jar.sync()
                
                result = True
                self.created = self.created + 1
                #print("== Page created ==")
        except:
            self.errors = self.errors + 1
            print "Unexpected error on createPage (" +dirtyId+ "):", sys.exc_info()[1]
            transaction.abort()
            return result
            #raise
          
    
        if not result:
            self.skipped = self.skipped + 1
            print("Skipped item: " + dirtyId)
        return result
    
    def createEvent(self, event):
        transaction.begin()
        container = self.getContainer()
        dirtyId = event.title
        result = False
        counter = 1
        
        if event.Description() == "" or event.image == "" or event.body == "":
            container = self.getOrCreateFolder(container, "toReview", False)

        try:
            id = idnormalizer.normalize(unicode(dirtyId, "utf-8"))
            
            while hasattr(container, id) and id != "":
                print ("Object " + id + " already exists.")
                counter = counter+1
                dirtyId = event.title + str(counter)
                id = idnormalizer.normalize(unicode(dirtyId, "utf-8")) 
                print ("creating " + id + " instead")
                if(counter > 4):
                    break
            
            if counter > 1:
                container = self.getContainer()
                container = self.getOrCreateFolder(container, "toReview", False)
                
            #Check if Event exists
            if not hasattr(container, id):
                if event.endDate == "":
                    event.endDate = event.startDate;
                
                container.invokeFactory(type_name="Event", id=id, title=event.title, description=event.Description(), startDate=DateTime(event.startDate), endDate=DateTime(event.endDate))
                
                #get the Event after creating
                item = container[id]
                
                #set the body
                item.setText(event.body)
                
                #Add leadImage to the event if possible
                self.addLeadImage(item, event.image)
                
                 #Add caption to the event's leadImage if possible
                self.addLeadImageCaption(item, event.caption)
                
                #Add tags to Keywords/Categories
                item.setSubject(event.tags.split(","))
                
                #Add location
                if event.location != "":
                    item.location = event.location
                
                #publish
                if event.Description() != "" and event.image != "" and event.body != "" and counter == 1:
                    item.portal_workflow.doActionFor(item, "publish", comment="Content automatically published by migrationScript")
                
                # Commit transaction
                transaction.commit()
                # Perform ZEO client synchronization (if runnning in clustered mode)
                #app._p_jar.sync()
                
                result = True
                self.created = self.created + 1
                #print("== Event created ==")
        except:
            self.errors = self.errors + 1
            print "Unexpected error on createEvent: (" +dirtyId+ ")", sys.exc_info()[1]
            transaction.abort()
            return result
            #raise
          
    
        if not result:
            self.skipped = self.skipped + 1
            print("Skipped item: " + dirtyId)
        return result


    def createImage(self, image):
        transaction.begin()
        #Get the base folder
        container = self.getContainer()
        storage = container
        #decide where to store it
        pathToStorage = []
        years = []
        events = []
        #read the domains and separate in years and events
        if image.domains != "":
            for folderName in image.domains:
                if(folderName.isdigit()):
                    years.append(folderName)
                elif folderName != "":
                    events.append(folderName)
                    
        #from the years select the smallest or set to undated
        if len(years) > 1:
            smallest = 9999
            for year in years:
                if int(year) < smallest:
                    smallest = int(year)
            pathToStorage.append(str(smallest))
        elif len(years) == 0:
            pathToStorage.append("undated")
        else:
            pathToStorage.append(years[0])
        
        #now add the event folders, if there is none then set to uncategorized
        if len(events) == 0:
            pathToStorage.append("uncategorized")
        else:
            for event in events:
                pathToStorage.append(event)
        
        
        #Set/create the inner folder
        for folderId in pathToStorage:
            container = self.getOrCreateFolder(container, folderId, False)
        
        #Check item limit NOT WORKING
        ids=container.objectIds()
        if len(ids) >= 5000:
            #there are too many items on this folder create a new one
            pathToStorage[len(pathToStorage)-1] = pathToStorage[len(pathToStorage)-1] + "-2"
            #reset the container
            container = self.getContainer()
            #And do it all over again
            for folderId in pathToStorage:
                container = self.getOrCreateFolder(container, folderId, True)
        
        dirtyId = image.title
        result = False
        
        if image.uri == "":
            print("Image has no URI, Skipping")
            self.skipped = self.skipped + 1
            print("Skipped item: " + dirtyId)
            return result

        try:
            id = idnormalizer.normalize(unicode(dirtyId, "utf-8"))
            
            if id == "":
                pathComponents = image.uri.split("/")
                filename = pathComponents[len(pathComponents)-1]
                id = filename[:-4]
            
            #Check if image exists
            if not hasattr(container, id):
                container.invokeFactory(type_name="Image", id=id, title=image.title)
               
                try: 
                    item = container[id]
                    imageFile = urllib2.urlopen(image.uri)
                    imageData = imageFile.read()
                    item.edit(file=imageData)
                    imageFile.close()
                    
                    #Add tags to Keywords/Categories
                    item.setSubject(image.tags.split(","))
                    
                except urllib2.HTTPError:
                    print("Image URL not available, Skipping")
                    self.skipped = self.skipped + 1
                    print("Skipped item: " + dirtyId)
                    return result
                    
                # Commit transaction again
                transaction.commit()
                # Perform ZEO client synchronization (if runnning in clustered mode)
                #app._p_jar.sync()
                
                result = True
                self.created = self.created + 1
                #print("== image created ==")
        except:
            self.errors = self.errors + 1
            print "Unexpected error on createImage (" +dirtyId+ "): ", sys.exc_info()[1]
            transaction.abort()
            return result
        
        if not result:
            self.skipped = self.skipped + 1
            print("Skipped item: " + dirtyId)
        return result

    def migrateToPerson(self):
        root = self.xmlDoc.children
        for field in root.children:
            if field.name == "node":
                #print("== Parsing Person: ==")
                currentPerson = PersonItem()
                for personField in field.children:
                    if personField.name == 'firstname':
                        currentPerson.firstname = personField.content
                        #print("    first name: " + currentPerson.firstname)
                    elif personField.name == 'middlename':
                        currentPerson.middlename = personField.content
                        #print("    middle name: " + currentPerson.middlename)
                    elif personField.name == 'lastname':
                        currentPerson.lastname = personField.content
                        #print("    last name: " + currentPerson.lastname)
                    elif personField.name == 'tags':
                        currentPerson.tags = personField.content + ", migratedV1"
                        #print("    tags: " + currentPerson.tags)
                    elif personField.name == 'intro':
                        currentPerson.intro = personField.content
                        #print("    intro: " + currentPerson.intro)
                    elif personField.name == 'body':
                        currentPerson.body = personField.content
                        #print("    body: " + currentPerson.body)
                    elif personField.name == 'nickname':
                        currentPerson.nickname = personField.content
                        #print("    nickname: " + currentPerson.nickname)
                    elif personField.name == 'location':
                        currentPerson.nationality = personField.content
                        #print("    nationality: " + currentPerson.nationality)
                    elif personField.name == 'image':
                        currentPerson.image = personField.content
                        #print("    image: " + currentPerson.image)
                    elif personField.name == 'caption':
                        currentPerson.caption = personField.content
                        #print("    caption: " + currentPerson.caption)
                    elif personField.name == 'link':
                        currentPerson.links.append(personField.content)
                        #print("    link: " + currentPerson.links[len(currentPerson.links) - 1])
                    elif personField.name == 'extra':
                        if personField.prop("field") == "mmv2:person_classes":
                            currentPerson.person_class = personField.content.replace("/", " ").strip()
                            #print("    person_class: " + currentPerson.person_class)

                        
                #currentPerson is now populated with the data from the XML now we create a Person in plone
                self.createPerson(currentPerson)
        return


    def migrateToImage(self):
        root = self.xmlDoc.children
        for field in root.children:
            if field.name == "node":
                #print("== Parsing Image: ==")
                currentImage = ImageItem()
                for imageField in field.children:
                    if imageField.name == 'link':
                        currentImage.uri = imageField.content
                        #print("    link: " + currentImage.uri)
                    elif imageField.name == 'tags':
                        currentImage.tags = imageField.content + ", migratedV1"
                        #print("    tags: " + currentImage.tags)
                    elif imageField.name == 'extra':
                        if imageField.prop("field") == "mmv2:imagedigital_title":
                            currentImage.title = imageField.content
                            #print("    title: " + currentImage.title)
                        if imageField.prop("field") == "mmv2:imagedigital_smalltitle":
                            currentImage.subtitle = imageField.content
                            #print("    subtitle: " + currentImage.subtitle)
                        if imageField.prop("field") == "mmv2:imagedigital_domains":
                            currentImage.domains = imageField.content.strip("/").split("//")
                            #for d in currentImage.domains:
                                #print("    domains: " + d)
                        
                #currentImage is now populated with the data from the XML now we create an Image in plone
                self.createImage(currentImage)
        return


    def migrateToWork(self):
        root = self.xmlDoc.children
        for field in root.children:
            if field.name == "node":
                #print("== Parsing Work: ==")
                currentWork = WorkItem()
                for workField in field.children:
                    if workField.name == 'title':
                        currentWork.title = workField.content
                        #print("    title: " + currentWork.title)
                    elif workField.name == 'subtitle':
                        currentWork.subtitle = workField.content
                        #print("    subtitle: " + currentWork.subtitle)
                    elif workField.name == 'tags':
                        currentWork.tags = workField.content + ", migratedV1"
                        #print("    tags: " + currentWork.tags)
                    elif workField.name == 'body':
                        currentWork.body = workField.content
                        #print("    body: " + currentWork.body)
                    elif workField.name == 'image':
                        currentWork.image = workField.content
                        #print("    image: " + currentWork.image)
                    elif workField.name == 'caption':
                        currentWork.caption = workField.content
                        #print("    caption: " + currentWork.caption)
                    elif workField.name == 'start':
                        currentWork.year = workField.content[:4]
                        #print("    year: " + currentWork.year)
                    elif workField.name == 'description':
                        currentWork.description = workField.content
                        #print("    description: " + currentWork.description)
                        
                #currentWork is now populated with the data from the XML now we create a Work in plone
                self.createWork(currentWork)
        return

    def migrateToOrganization(self):
        root = self.xmlDoc.children
        for field in root.children:
            if field.name == "node":
                #print("== Parsing Organization: ==")
                currentOrganization = OrganizationItem()
                for organizationField in field.children:
                    if organizationField.name == 'tags':
                        currentOrganization.tags = organizationField.content + ", migratedV1"
                        #print("    tags: " + currentOrganization.tags)
                    elif organizationField.name == 'title':
                        currentOrganization.title = organizationField.content
                        #print("    title: " + currentOrganization.title)
                    elif organizationField.name == 'subtitle':
                        currentOrganization.subtitle = organizationField.content
                        #print("    subtitle: " + currentOrganization.subtitle)
                    elif organizationField.name == 'link':
                        currentOrganization.link = organizationField.content
                        #print("    link: " + currentOrganization.link)
                    elif organizationField.name == 'body':
                        currentOrganization.body = organizationField.content
                        #print("    body: " + currentOrganization.body)
                    elif organizationField.name == 'image':
                        currentOrganization.image = organizationField.content
                        #print("    image: " + currentOrganization.image)
                    elif organizationField.name == 'caption':
                        currentOrganization.caption = organizationField.content
                        #print("    caption: " + currentOrganization.caption)
                    elif organizationField.name == 'extra':
                        if organizationField.prop("field") == "mmv2:organisation_classes":
                            currentOrganization.organization_class = organizationField.content.replace("/", " ").strip()
                            #print("    organization_class: " + currentOrganization.organization_class)

                        
                #currentOrganization is now populated with the data from the XML now we create a Organization in plone
                self.createOrganization(currentOrganization)
        return


    def migrateToEvent(self):
        root = self.xmlDoc.children
        for field in root.children:
            if field.name == "node":
                #print("== Parsing Event: ==")
                currentEvent = EventItem()
                for eventField in field.children:
                    if eventField.name == 'tags':
                        currentEvent.tags = eventField.content + ", migratedV1"
                        #print("    tags: " + currentEvent.tags)
                    elif eventField.name == 'title':
                        currentEvent.title = eventField.content
                        #print("    title: " + currentEvent.title)
                    elif eventField.name == 'subtitle':
                        currentEvent.subtitle = eventField.content
                        #print("    subtitle: " + currentEvent.subtitle)
                    elif eventField.name == 'link':
                        currentEvent.link = eventField.content
                        #print("    link: " + currentEvent.link)
                    elif eventField.name == 'body':
                        currentEvent.body = eventField.content
                        #print("    body: " + currentEvent.body)
                    elif eventField.name == 'image':
                        currentEvent.image = eventField.content
                        #print("    image: " + currentEvent.image)
                    elif eventField.name == 'caption':
                        currentEvent.caption = eventField.content
                        #print("    caption: " + currentEvent.caption)
                    elif eventField.name == 'date':
                        currentEvent.startDate = eventField.content
                        #print("    Start Date: " + currentEvent.startDate)
                    elif eventField.name == 'enddate':
                        currentEvent.endDate = eventField.content
                        #print("    End Date: " + currentEvent.endDate)
                    elif eventField.name == 'location':
                        currentEvent.location = eventField.content
                        #print("    location: " + currentEvent.location)
                    elif eventField.name == 'extra':
                        if eventField.prop("field") == "mmv2:event_classes":
                            currentEvent.event_class = eventField.content.replace("/", " ").replace("_", " ").strip()   

                        
                #currentEvent is now populated with the data from the XML now we create a Event in plone
                self.createEvent(currentEvent)
        return

    def migrateToPage(self):
        root = self.xmlDoc.children
        for field in root.children:
            if field.name == "node":
                #print("== Parsing Page: ==")
                currentPage = PageItem()
                for pageField in field.children:
                    if pageField.name == 'title':
                        currentPage.title = pageField.content
                        #print("    title: " + currentPage.title)
                    elif pageField.name == 'tags':
                        currentPage.tags = pageField.content + ", migratedV1"
                        #print("    tags: " + currentPage.tags)
                    elif pageField.name == 'body':
                        currentPage.body = pageField.content
                        #print("    body: " + currentPage.body)
                    elif pageField.name == 'image':
                        currentPage.image = pageField.content
                        #print("    image: " + currentPage.image)
                    elif pageField.name == 'caption':
                        currentPage.caption = pageField.content
                        #print("    caption: " + currentPage.caption)
                    elif pageField.name == 'description':
                        currentPage.description = pageField.content
                        #print("    description: " + currentPage.description)
                    elif pageField.name == 'link':
                        currentPage.link = pageField.content
                        #print("    link: " + currentPage.link)
                        
                #currentPage is now populated with the data from the XML now we create a Page (Document) in plone
                self.createPage(currentPage)
        return

    def startMigration(self):
        if self.portal is not None:
            if self.typeToCreate == "Person":
                self.migrateToPerson()
            elif self.typeToCreate == "Image":
                self.migrateToImage()
            elif self.typeToCreate == "Work":
                self.migrateToWork()
            elif self.typeToCreate == "Organization":
                self.migrateToOrganization()
            elif self.typeToCreate == "Page":
                self.migrateToPage()
            elif self.typeToCreate == "Event":
                self.migrateToEvent()
            else:
                print("TYPE NOT RECOGNIZED!! ==>> " + self.typeToCreate)
            
            self.cleanUp()
        else:
            print ("Portal is NONE!!!")
            self.cleanUp()
        return