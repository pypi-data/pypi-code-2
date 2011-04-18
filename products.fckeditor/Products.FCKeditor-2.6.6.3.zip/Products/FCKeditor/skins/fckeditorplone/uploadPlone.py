## Script (Python) "connectorPlone.py"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters= Type='',CurrentPath=''


from Products.PythonScripts.standard import html_quote
from Products.CMFCore.utils import getToolByName
from Products.FCKeditor.utils import fckCreateValidZopeId, decodeQueryString, encodeString, getFCKBrowserRoot


request = context.REQUEST
RESPONSE =  request.RESPONSE
dicoRequest = request.form
# XXXX we dont want to overload all fckeditor javascripts
# so direct upload form is not clean (params transmittted through POST + GET)
queryString = decodeQueryString(request.QUERY_STRING)
message_error=""
sCurrentFolder =""
browser_root = getFCKBrowserRoot(context)
portal_url = browser_root.absolute_url()
server_url = request.SERVER_URL
portal_path = portal_url.replace(server_url,'')

# 1. Config

# Path to user files relative to the document root.
# change it to force upload path
ConfigUserFilesPath=""

# get fck Plone params
field_name = ""

if dicoRequest.has_key('field_name'):
   field_name = dicoRequest ['field_name']
elif queryString.has_key('field_name') :
   field_name = queryString['field_name']
   
 
macro="rich"
if field_name :
    try:
        field = context.schema[field_name]
    except:
        # some plone products (ex : PloneBoard) are using wysiwyg support without AT field
        field = None
    if field :    
        widget = field.widget
        macro = widget.macro   
if macro == 'fckwidget':  
   fckParams = widget.getBrowserValues(context)
else:
   fckParams=context.getFck_params()


# Allowed and denied extensions dictionaries

ConfigAllowedExtensions = {
  "File": None,
  "Image": ("jpg","gif","jpeg","png"),
  "Flash": ("swf","fla"),
  "Media":("flv","avi","mpg","mpeg","mp1","mp2","mp3",
           "mp4","wma","wmv","wav","mid","midi","rmi","rm","ram","rmvb","mov","qt")
  }

ConfigDeniedExtensions =  {
  "File":("py","pt","cpt","dtml","php","asp","aspx","ascx","jsp","cfm","cfc","pl",
          "bat","exe","com","dll","vbs","js","reg"),
  "Image":None,
  "Flash":None,
  "Media":None
  }

# set link by UID for AT content Types 
linkbyuid=test(fckParams['allow_link_byuid'],1,0)

# check if upload allowed for Links Image and internal links

allow_file_upload = test(fckParams['allow_server_browsing'],test(fckParams['allow_file_upload'],1,0),0)
allow_image_upload = test(fckParams['allow_server_browsing'],test(fckParams['allow_image_upload'],1,0),0)
allow_flash_upload = test(fckParams['allow_server_browsing'],test(fckParams['allow_flash_upload'],1,0),0)

# check for portal_types when uploading internal links, images and files

file_portal_type = test(fckParams['file_portal_type'],fckParams['file_portal_type'],'File')
image_portal_type = test(fckParams['image_portal_type'],fckParams['image_portal_type'],'Image')
flash_portal_type = test(fckParams['flash_portal_type'],fckParams['flash_portal_type'],'File')


# PloneArticle based meta_types
pa_meta_types = fckParams['pa_meta_types']

# RichDocumented based portal types
rd_portal_types = fckParams.get('rd_portal_types', ['RichDocument','RichPage'])

# find Plone Site charset if possible
try:
  prop   = getToolByName(context, "portal_properties")
  charsetSite = prop.site_properties.getProperty("default_charset", "utf-8")
except:
  charsetSite ="utf-8"

if charsetSite.lower() in ("utf-8", "utf8"):
    charsetSite ="utf-8"

# 2. utils

def RemoveFromStart(sourceString,charToRemove ):
  return sourceString.lstrip(charToRemove)

def utf8Encode(chaine) :
    # encode in utf8 string
    return encodeString(chaine, charsetSite, "utf-8")

def utf8Decode(chaine) :
    # decode from utf8 (fck forms) to charset
    return encodeString(chaine, "utf-8", charsetSite)



# 3. io



def GetUrlFromPath( folderPath ) :

    return ('%s/%s' %(portal_path,folderPath)).rstrip("/")


def RemoveExtension( fileName ):

   sprout=fileName.split(".")
   return '.'.join(sprout[:len(sprout)-1])

def  IsAllowedExt( extension, resourceType ) :
  
   sAllowed = ConfigAllowedExtensions[resourceType]
   sDenied = ConfigDeniedExtensions[resourceType]

   if (sAllowed is None or extension in sAllowed) and (sDenied is None or extension not in sDenied) :
     return 1
   else :
     return 0

def FindExtension (fileName):

   sprout=fileName.split(RemoveExtension(fileName))
   return ''.join(sprout).lstrip('.')

  
# 6. upload

def UploadFile(resourceType, currentFolder, data, title, description, thumbsize ) :

        user=context.REQUEST['AUTHENTICATED_USER']
        if currentFolder != "/" :
            obj = browser_root.restrictedTraverse(currentFolder.lstrip('/'))
        else :
            obj = browser_root
        error=""
        fileUrl=""
        customMsg=""
        idObj=""
        folderUrl=GetUrlFromPath(currentFolder)+ "/"
        smallSizeUrl = ''
        mediumSizeUrl = ''

        if (obj.meta_type not in pa_meta_types and
            obj.portal_type not in rd_portal_types):
            # define Portal Type to add

            # TODO portal_type for Media Resource Type in FCK control panel
            if resourceType in ('File', 'Media'):
                typeToAdd = file_portal_type
            elif resourceType == 'Flash':
                typeToAdd = flash_portal_type
            elif resourceType == 'Image' :
                if obj.meta_type=="CMF ZPhotoSlides":
                    typeToAdd = 'ZPhoto'
                elif obj.meta_type=="Photo Album":
                    typeToAdd = 'Photo'
                elif obj.meta_type=="ATPhotoAlbum":
                    typeToAdd = 'ATPhoto'
                else:
                    typeToAdd = image_portal_type
                    smallSizeUrl = '/image_thumb'
                    mediumSizeUrl = '/image_preview'
        

            if not user.has_permission('Add portal content', obj) and not user.has_permission('Modify portal content', obj):
               error = "1"
               customMsg="upload denied - insufficient privileges"

            if resourceType == 'Image' and not allow_image_upload:
               error = "1"
               customMsg="image upload denied - contact your site admin"

            if resourceType == 'Flash' and not allow_flash_upload:
               error = "1"
               customMsg="flash upload denied - contact your site admin"

            if resourceType not in ('Flash','Image') and not allow_file_upload:
               error = "1"
               customMsg="file upload denied - contact your site admin"

            if not data:
              #pas de fichier 
              error= "1"        
              customMsg="no file uploaded"


            titre_data=''
            filename=utf8Decode(getattr(data,'filename', ''))
            titre_data=filename[max(string.rfind(filename, '/'),
                            string.rfind(filename, '\\'),
                            string.rfind(filename, ':'),
                            )+1:]                  

            idObj=fckCreateValidZopeId(utf8Encode(titre_data))

            if title :
               titre_data=title

            if not IsAllowedExt( FindExtension(idObj), resourceType ):
                  error= "202"        
                  customMsg="Invalid file type"

            if not error :              
                error="0"
                indice=0
                exemple_titre=idObj
                while exemple_titre in obj.objectIds():
                  indice=indice+1
                  exemple_titre=str(indice) + idObj
                if indice!=0:
                    error= "201"
                    idObj = exemple_titre                        
                    customMsg="an object already exists with the same name, the file has been renamed " + idObj 

                try:
                    obj.invokeFactory(id=idObj, type_name=typeToAdd, title=titre_data )
                    newFile = getattr(obj, idObj)
                    newFile.edit(file=data)
                    newFile.setDescription(description)
                    if linkbyuid and hasattr(newFile.aq_explicit, 'UID'):
                        uid = newFile.UID()
                        fileUrl = "./resolveuid/" + uid
                    else :
                        fileUrl = folderUrl + idObj                          

                except:
                    error = "1"
                    customMsg = "Server error"

        # upload is no more allowed in articles
        # because in Plone3 it becames really complicated to 
        # upload contents inside context during edition
        # it's impossible when using portal_factory
        # it's impossible when using standard edition forms
        # MULTIPAGE schema is responsible (all forms are in hidden fieldsets ...)
        elif obj.meta_type in pa_meta_types:
            error= "103"        
            customMsg="Upload is not allowed in articles, use standard PloneArticle forms"

                             
        elif obj.portal_type in rd_portal_types:
          if not data:
            error="1"
            customMsg="no file uploaded"
          else:
            filename=utf8Decode(getattr(data,'filename', ''))
            titre_data=filename[max(string.rfind(filename, '/'),
                            string.rfind(filename, '\\'),
                            string.rfind(filename, ':'),
                            )+1:]                  

            # idObj can't be cleaned with PloneArticle attachements
            # it's a problem but we do the job
            idObj=fckCreateValidZopeId(utf8Encode(titre_data))
            if title :
                titre_data=title

            if not user.has_permission('Modify portal content', obj):
                error = "103"
            elif not allow_image_upload:
                error = "103"
            elif not IsAllowedExt( FindExtension(idObj), resourceType ):
                error= "202"        
                customMsg="Invalid file type"
            if not error:
               error = "0"
               # [reinout:] somehow error is set to "" at the start,
               # but that wreaks havoc here (javascript syntax
               # error). So we set it to "0", which is the right
               # 'error' when there's no error.
            if error=="0":
              try:
                while idObj in obj.contentIds():
                  idObj = 'copy_of_%s' % idObj

                resource_to_pt = dict(
                  File='FileAttachment',
                  Image='ImageAttachment',
                  Flash='FileAttachment',
                  )
                
                obj.invokeFactory(resource_to_pt[resourceType], idObj)
                attachment = getattr(obj, idObj)
                attachment.setTitle(titre_data)
                if resourceType == 'Image':
                  attachment.setImage(data)
                else:
                  attachment.setFile(data)

                if linkbyuid:
                  fileUrl = "./resolveuid/" + attachment.UID()
                else:
                  fileUrl = attachment.absolute_url()
                
              except Exception, e:
                error="1"
                customMsg="Server error: %s" % e

        if thumbsize=='small':
               fileUrl += smallSizeUrl    
        elif thumbsize=='medium':
               fileUrl += mediumSizeUrl              

        d= '''
        <script type="text/javascript">
        window.parent.OnUploadCompleted(%s,"%s","%s","%s") ;
        </script>
        '''% (error,fileUrl,idObj,customMsg)
        return d


#7. principial 



if ConfigUserFilesPath != "" :
   sUserFilesPath = ConfigUserFilesPath
elif dicoRequest.has_key('ServerPath'):
   sUserFilesPath = dicoRequest ['ServerPath']
else :
   sUserFilesPath = "/"



if dicoRequest.has_key('CurrentPath'):
   sCurrentFolder = dicoRequest ['CurrentPath']
elif queryString.has_key('CurrentPath') :
   sCurrentFolder= queryString['CurrentPath']
else :
   message_error="No CurrentFolder in request"


if sUserFilesPath!='/' and sUserFilesPath.rstrip('/') not in sCurrentFolder:
   sCurrentFolder = sUserFilesPath

sSize=''
if dicoRequest.has_key('Type'):
    sResourceType = dicoRequest ['Type']
    if sResourceType == 'Image':      
       sSize = dicoRequest ['size']
else :
    sResourceType = 'File'

if dicoRequest.has_key('Description'):
    sDescription = utf8Decode(dicoRequest ['Description'])
    
else :
    sDescription = ''



# interception File Upload
if dicoRequest.has_key('NewFile'):
    sData = dicoRequest ['NewFile']
    sTitle = utf8Decode(dicoRequest ['Title'])

    chaineHtmlUpload = UploadFile(sResourceType, sCurrentFolder, sData, sTitle, sDescription, sSize)
    RESPONSE.setHeader('Content-type', 'text/html;charset=%s' % charsetSite)
    return chaineHtmlUpload

else :
    #pas de fichier 
    error= "1"        
    customMsg="no file uploaded"
    fileUrl=""
    fileName=""
    d= '''
    <script type="text/javascript">
    window.parent.OnUploadCompleted(%s,"%s","%s","%s") ;
    </script>
    '''% (error,fileUrl,fileName,customMsg)
    RESPONSE.setHeader('Content-type', 'text/html')
    return d
