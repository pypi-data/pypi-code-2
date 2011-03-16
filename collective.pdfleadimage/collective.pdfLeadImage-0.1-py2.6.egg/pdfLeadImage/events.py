from utils import addLeadImage
from utils import ghostscript_transform
from async import get_queue, Job

try:
    from collective.contentleadimage.config import IMAGE_FIELD_NAME
    from collective.contentleadimage.config import IMAGE_CAPTION_FIELD_NAME
    from collective.contentleadimage.interfaces import ILeadImageable
    import collective.contentleadimage
    LEADIMAGE_EXISTS = True
except ImportException:
    LEADIMAGE_EXISTS = False
    
def createLeadImage(object, event):
    """
        Creates a lead image from the pdf
    """
    #debug
    print("Running the handler for pdf lead image")
    if not LEADIMAGE_EXISTS:
        print("Problem importing lead image product")
    if not object.portal_type == 'File':
        print("Object is not a file")
    if object.getFile().getContentType() != "application/pdf":
        print("Object is not a pdf, it is a:" + object.getFile().getContentType())
    
    if LEADIMAGE_EXISTS and object.portal_type == 'File':
        field = object.getField(IMAGE_FIELD_NAME)
        if field is not None:
                    value = field.get(object)
                    hasLeadImage = not not value
        else:
            hasLeadImage = False
        
        if not hasLeadImage:
            file = str(object.getFile())
            if file != "":
                jpeg = ghostscript_transform(file, 1)
                addLeadImage(object, jpeg)
            else:
                print ("file is nothing")
                
def createLeadImageAsync(object, event):
    """
        Creates a lead image from the pdf asyncronously
    """
    #debug
    print("Running the handler for pdf lead image")
    if not LEADIMAGE_EXISTS:
        print("Problem importing lead image product")
    if not object.portal_type == 'File':
        print("Object is not a file")
    if object.getFile().getContentType() != "application/pdf":
        print("Object is not a pdf, it is a: " + object.getFile().getContentType())
    
    if LEADIMAGE_EXISTS and object.portal_type == 'File':
        field = object.getField(IMAGE_FIELD_NAME)
        if field is not None:
                    value = field.get(object)
                    hasLeadImage = not not value
        else:
            hasLeadImage = False
        
        if not hasLeadImage:
            file = str(object.getFile())
            if file != "":
                #ADD TO QUEUE HERE
                # get the queue
                conversion_queue = get_queue('collective.pdfLeadImage.conversion')
                # create a converter job
                converter_job = Job(createLeadImage, object)
                # add it to the queue
                conversion_queue.pending.append(converter_job)
                print("Document Conversion Job Queued")
            else:
                print ("file is nothing")
