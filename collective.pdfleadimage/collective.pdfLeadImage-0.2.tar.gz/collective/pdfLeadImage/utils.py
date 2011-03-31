import subprocess
from Acquisition import aq_inner
try:
    from collective.contentleadimage.config import IMAGE_FIELD_NAME
    from collective.contentleadimage.config import IMAGE_CAPTION_FIELD_NAME
    from collective.contentleadimage.interfaces import ILeadImageable
    import collective.contentleadimage
    LEADIMAGE_EXISTS = True
except ImportException:
    LEADIMAGE_EXISTS = False

class FieldNotInitializedException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


def addLeadImage(item, imageData):
    #set the lead image if necessary and if lead image product is installed
    if LEADIMAGE_EXISTS and imageData != "":
        #print("I have data, creating lead image")
        #add the image as leadImage
        if ILeadImageable.providedBy(item):
            field = aq_inner(item).getField(IMAGE_FIELD_NAME)
            if field is not None:
                field.set(item, imageData)
                item.reindexObject()
                #if field.getFilename(item) is None:
                    #print "Added Image but the stupid filename field is still None"
            else:
                raise FieldNotInitializedException("The leadImage Field is None.")
        #else:
            #print("Item type does not accept leadImage")
            
        return

def ghostscript_transform(pdf, page_num):
    """
    ghostscript_transform
    args:
    pdf = pdf data
    page_num = number of the page to #print to jpg
    returns:
    jpg data
    """
    #print("Extracting page 1")
    
    first_page = "-dFirstPage=%s" % (page_num)
    last_page = "-dLastPage=%s" % (page_num)
    gs_cmd = [
        "gs",
        "-q",
        "-sDEVICE=jpeg",
        "-dJPEGQ=99",
        "-dGraphicsAlphaBits=4",
        "-dTextAlphaBits=4",
        "-dDOINTERPOLATE",
        "-dSAFER",
        "-dBATCH",
        "-dNOPAUSE",
        first_page,
        last_page,
        "-r59x56",
        "-sOutputFile=%stdout",
        "-",
        ]
    jpeg = None
    gs_process = subprocess.Popen(gs_cmd,stdout=subprocess.PIPE,stdin=subprocess.PIPE,)
    gs_process.stdin.write(pdf)
    jpeg = gs_process.communicate()[0]
    gs_process.stdin.close()
    return_code = gs_process.returncode
    if return_code == 0:
        print("Ghostscript processed one page of a pdf file.")
    else:
        print("Ghostscript process did not exit cleanly! Error Code: %d" % (return_code))
        jpeg = None
    return jpeg