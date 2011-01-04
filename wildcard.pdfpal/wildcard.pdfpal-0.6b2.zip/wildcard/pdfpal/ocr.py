from commandrunner import command_subprocess
import logging
from settings import PDFSettings
from DateTime import DateTime
import os
import tempfile
import shutil
from Products.CMFCore.utils import getToolByName
from settings import PDFPalConfiguration

try:
    from wc.pageturner.events import queue_job
    from wc.pageturner.events import convert as pageturner_convert
    pageturner_installed = True
except:
    pageturner_installed = False

logger = logging.getLogger('wildcard.pdfpal')

class ghostscript_subprocess(command_subprocess):
    bin_name = 'gs'

    logging = {
        'info' : "Converted PDF to tiff files.",
        'warn' : "Ghostscript process did not exit cleanly! Error Code: %d"
    }

    options = [
        '-dSAFER',
        '-dBATCH',
        '-dNOPAUSE',
        '-sDEVICE=tiff24nc',
        '-r300',
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
class hocr_subprocess(tesseract_subprocess):
    options = [
        '%(imagefilename)s',
        '%(txtfilename)s',
        'hocr'
    ]

class tesseract_version_subprocess(tesseract_subprocess):
    options = ['-v']

try:
    tesseract = tesseract_subprocess()
    hocr = hocr_subprocess()
    tess_version = tesseract_version_subprocess()
    try:
        process, output = tess_version.run_command()
        _, version = output.strip().split('-', 1) # should be in the form of -- tesseract-3.01\n
        if version.startswith('3') and int(version[-1]) >= 1:
            hocr_enabled = True
    except:
        hocr_enabled = False
except IOError:
    logger.exception("No Tesseract installed. PDF Pal will not be able to index PDFs or make PDFs searchable.")
    tesseract = None
    hocr = None
    hocr_enabled = False
    
class hocr2pdf_subprocess(command_subprocess):
    """
        hocr2pdf -i "$page" -o "$base.pdf" < "$base.html" 
    
        input - input tiff filename
        output - output pdf filename
        hocr_file - stdin 
    """
    bin_name = 'hocr2pdf'
    
    options = [
        '-i',
        '%(input)s',
        '-s',
        '-o',
        '%(output)s'
    ]
try:
    hocr2pdf = hocr2pdf_subprocess()
except IOError:
    logger.exception("No hocr2pdf installed. PDF Pal will not be able to make PDFs searchable.")
    hocr2pdf = None
    
class dumpPdfMetadata_subprocess(command_subprocess):
    """
    pdftk 5percent1.pdf dump_data output info.txt
    
    output - filename for info file
    the input pdf comes from the stdin
    """
    bin_name = 'pdftk'
    throw_exception = True
    
    options = [
        '-',
        'dump_data',
        'output',
        '%(output)s'
    ]
try:
    dumpPdfMetadata = dumpPdfMetadata_subprocess()
except IOError:
    logger.exception("No pdftk installed. PDF Pal will not be able to make PDFs searchable.")
    dumpPdfMetadata = None
    
class copyPdfMetadata_subprocess(command_subprocess):
    """
    pdftk z.pdf update_info info.txt output test.pdf
    
    info_file - filename for pdf info file
    input is stdin
    outputs to stdout
    """
    bin_name = 'pdftk'
    throw_exception = True
    
    options = [
        '%(input)s',
        'update_info',
        '%(info_file)s',
        'output',
        '%(output)s'
    ]
try:
    copyPdfMetadata = copyPdfMetadata_subprocess()
except IOError:
    copyPdfMetadata = None

class combinePDFs_subprocess(command_subprocess):
    """
    gs -q -dNOPAUSE -dBATCH -sDEVICE=pdfwrite -sOutputFile="$output" "$tmpdir"/page-*.pdf
    
    input_files - wildcard filename to specify files to combine
    output - output filename
    """
    shell=True
    throw_exception = True
    bin_name = 'gs'
    
    options = [
        '-q',
        '-dNOPAUSE',
        '-dBATCH',
        '-sDEVICE=pdfwrite',
        '-dPDFSETTINGS=%(conversion_type)s',
        '-sOutputFile=%(output)s',
        '%(input_files)s'
    ]
try:
    combinePDFs = combinePDFs_subprocess()
except IOError:
    combinePDFs = None

if hocr and hocr_enabled and combinePDFs and copyPdfMetadata and dumpPdfMetadata:
    hocr_enabled = True
else:
    hocr_enabled = False
    
_tiff_output_filename = 'image_%04d.tiff'
_pdf_output_filename = 'image_*.tiff.pdf'

def index_pdf(context):
    """
    Index PDF using OCR
    """
    settings = PDFSettings(context)
    if not DateTime(settings.ocr_last_updated) < DateTime(context.ModificationDate()):
        return # skip out if already done...
    
    configuration = PDFPalConfiguration(context)
 
    result_directory = tempfile.mkdtemp()
    output_path = os.path.join(result_directory, _tiff_output_filename)
    text_path = os.path.join(result_directory, 'output')
    textfilepath = os.path.join(result_directory, 'output.txt')
    hocrfilepath = os.path.join(result_directory, 'output.html')
    pdfinfo_filepath = os.path.join(result_directory, 'pdf_info.txt')
    
    
    filedata = str(context.getFile().data)
    
    process, output = ghostscript.run_command(stdin=filedata, opt_values={'outputfilename' : output_path})

    files = os.listdir(result_directory)
    files.sort()

    txtoutput = ''
    try:
        for tif in files:
            path = os.path.join(result_directory, tif)
        
            process, output = tesseract.run_command(opt_values={'imagefilename' : path, 'txtfilename' : text_path})
            
            if configuration.overwrite_pdf_with_searchable_version and hocr_enabled:
                hocr.run_command(opt_values={'imagefilename' : path, 'txtfilename' : text_path})
                hocr_file = open(hocrfilepath)
                hocr2pdf.run_command(opt_values={'input' : path, 'output' : path + '.pdf'}, stdin=hocr_file.read())
                hocr_file.close()
            
            if os.path.exists(textfilepath):
                file = open(textfilepath)
                txtoutput += file.read()
                file.close()
                os.remove(textfilepath)
            
            os.remove(path)
    except:
        logger.exception("There was an error running OCR for %s" % context.getId())

    if configuration.overwrite_pdf_with_searchable_version and hocr_enabled:
        # now combine the new pdf
        field = context.getField('file')
        orig_filename = field.getFilename(context)
        _, tmpfile = tempfile.mkstemp()
        new_pdffilename = os.path.join(result_directory, orig_filename)
        try:
            process, output = combinePDFs.run_command(opt_values={
                'input_files' : os.path.join(result_directory, _pdf_output_filename), 
                'output' : tmpfile,
                'conversion_type' : configuration.pdf_conversion_type
            })
            dumpPdfMetadata.run_command(stdin=filedata, opt_values={'output' : pdfinfo_filepath})
            process, output = copyPdfMetadata.run_command(opt_values={'info_file' : pdfinfo_filepath, 'input': tmpfile, 'output' : new_pdffilename})
            pdf = open(new_pdffilename)
            import transaction
            transaction.begin()
            field.set(context, pdf)
            transaction.commit()
        except:
            logger.exception("There was an error making the PDF '%s' searchable " % context.getId())

    # Clean-up temp dir
    shutil.rmtree(result_directory)

    import transaction
    transaction.begin()
    if txtoutput:
        field = context.getField('ocrText')
        field.set(context, txtoutput)
        context.reindexObject(idxs=['SearchableText']) 
    
    settings.ocr_last_updated = DateTime().ISO8601()
    transaction.commit()
    
    qi = getToolByName(context, 'portal_quickinstaller')
    if pageturner_installed and qi.isProductInstalled('wc.pageturner'):
        # When both products are installed at the same time, page turner defers to 
        # pdfpal to convert the pdf first so it can create the correct flexpaper
        pageturner_convert(context)
        
