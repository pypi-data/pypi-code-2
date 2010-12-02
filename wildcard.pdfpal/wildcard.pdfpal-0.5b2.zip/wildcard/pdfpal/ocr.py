from commandrunner import command_subprocess
import logging
from settings import PDFSettings
from DateTime import DateTime
import os
import tempfile

logger = logging.getLogger('wildcard.pdfpal')

class ghostscript_subprocess(command_subprocess):
    bin_name = 'gs'

    options = [
        '-dSAFER',
        '-dBATCH',
        '-dNOPAUSE',
        '-sDEVICE=tiffgray',
        '-r250',
        '-dTextAlphaBits=4',
        '-dGraphicsAlphaBits=4',
        '-dMaxStripSize=8192',
        '-sOutputFile=%(outputfilename)s',
        "-"
        ]

try:
    ghostscript = ghostscript_subprocess()
except IOError:
    logger.exception("No GhostScript installed. PDF Pal will not be able to create thumbnails.")
    ghostscript = None
    
class tesseract_subprocess(command_subprocess):
    bin_name = 'tesseract'
    
    options = [
        '%(imagefilename)s',
        '%(txtfilename)s'
    ]
    
try:
    tesseract = tesseract_subprocess()
except IOError:
    logger.exception("No Tesseract installed. PDF Pal will not be able to index PDFs.")
    tesseract = None
    
def index_pdf(context):
    """
    Index PDF using OCR
    """
    settings = PDFSettings(context)
    if not DateTime(settings.ocr_last_updated) < DateTime(context.ModificationDate()):
        return # skip out if already done...
    
    result_directory = tempfile.mkdtemp()
    output_path = os.path.join(result_directory, 'image_%04d.tif')
    text_path = os.path.join(result_directory, 'output')
    
    filedata = str(context.getFile().data)
    
    process, output = ghostscript.run_command(stdin=filedata, opt_values={'outputfilename' : output_path})
    return_code = process.returncode
    if return_code == 0:
        logger.info("Converted PDF to tif files.")
    else:
        logger.warn("Ghostscript process did not exit cleanly! Error Code: %d" % (return_code))


    files = os.listdir(result_directory)
    files.sort()

    txtoutput = ''
    for tif in files:
        path = os.path.join(result_directory, tif)
        
        process, output = tesseract.run_command(opt_values={'imagefilename' : path, 'txtfilename' : text_path})

        file = open(text_path + '.txt')
        txtoutput += file.read()
        file.close()

        os.remove(text_path + '.txt')
        os.remove(path)

    # Clean-up temp dir
    os.rmdir(result_directory)

    if txtoutput:
        field = context.getField('ocrText')
        field.set(context, txtoutput)
        context.reindexObject() 
    