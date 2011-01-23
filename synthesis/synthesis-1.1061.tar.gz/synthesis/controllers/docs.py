use_encryption = False
import os
import logging
from pylons import request, response, config
from lib.base import BaseController
import datetime
from lxml import etree
import urllib
from webob import Request
if use_encryption:
    from lib import decrypt3des
from conf import settings 

server_root = config['here']
schema_file = 'OCC_Extend_HUD_HMIS.xsd'
schema_path = config['here'] + '/schema/'
schema_full_path = schema_path + schema_file
schema_url = 'http://xsd.alexandriaconsulting.com/repos/trunk/HUD_HMIS_XML/OCC_Extend_HUD_HMIS.xsd'
log = logging.getLogger(__name__)


class DocsController(BaseController):
    """REST Controller styled on the Atom Publishing Protocol"""
    # To properly map this controller, ensure your config/routing.py
    # file has a resource setup:
    #     map.resource('doc', 'docs')

    def index(self, format='html'):
        """GET /docs: All items in the collection"""
        print "docs/index called"
        return "you're at the docs index"

    def create(self, format='text'):
        """POST /docs: Create a new item"""
        req = Request(request.environ)
        log.debug('Received HTTP Request: %s', req)
        print 'these are the request.params: ', request.params
        print "FULL RAW POST Data:"
        print request.environ['wsgi.input'].read(int(request.environ['CONTENT_LENGTH']))
        print "FULL request.POST Data:"
        print request.POST
        postdatakeys = request.POST.keys()
        print "keys are:", postdatakeys
        #accept only one posted file per request for now
        stream_fieldstorage = request.POST[postdatakeys[0]]
        
        #print "CGI FileStorage uploaded is: ", myfile
        
        #Create a file in a permanent location, moving it out of CGI FieldStorage
        #make file
        file_prefix = 'OCC_' + str(datetime.datetime.now())
        file_prefix = file_prefix.replace(' ', '_')
        file_suffix_enc = '_encrypted.xml'
        file_suffix_unenc = '_unencrypted.xml'
        if use_encryption:
            print "using encryption"
            file_name = file_prefix + file_suffix_enc
        elif not use_encryption:
            print "not using encryption"
            file_name = file_prefix + file_suffix_unenc
        else: 
            print "not sure if using encrypted file or not"
        
        if not os.path.exists(settings.WEB_SERVICE_INPUTFILES_PATH[0]):
                os.mkdir(settings.WEB_SERVICE_INPUTFILES_PATH[0])
        file_full_path = os.path.join(settings.WEB_SERVICE_INPUTFILES_PATH[0], file_name)
        print 'file_full_path: ', file_full_path
        
        #open file 
        if use_encryption:
            try:
                print "trying to open encrypted file"
                encrypted_file = open(file_full_path, 'w')
            except:
                print "Error opening encrypted instance file for writing"
        if not use_encryption:
            try:
                print "trying to open unencrypted file"
                unencrypted_file = open(file_full_path, 'w')
            except:
                print "Error opening unencrypted instance file for writing"
                
        #write to file
        if use_encryption:
            print 'writing', file_name, 'to', server_root, 'for decryption'
            print 'encrypted_file is', encrypted_file
            encrypted_file.write(stream_fieldstorage.value)
            encrypted_file.close()
            
        if not use_encryption:
            print 'writing', file_name, 'to', server_root, 'server root for parsing'
            print 'unencrypted_file is', unencrypted_file
            unencrypted_file.write(stream_fieldstorage.value)
            unencrypted_file.close()
        
        #check if a file was written, regardless of encryption    
        if not os.path.exists(file_full_path):
            print "An file wasn't written"
        else:
            print "A file was written at: ", file_full_path
        
        #decrypt file if using decryption
        #assume file is encrypted, since it can be difficult to tell if it is.  We could look for XML structures, but how do you easily tell bad/invalid  XML apart from encrypted?  If not encrypted, that's a problem.
        #decrypt file
        if use_encryption:
            try:
                encrypted_file = open(file_full_path, 'r') 
            except: 
                print "couldn't open encrypted file for reading/decryption"
            decrypted_stream = decrypt3des.decryptFile(encrypted_filepath = None, encrypted_stream=encrypted_file)
            file_suffix_unenc = '_decrypted.xml'
            file_name = file_prefix + file_suffix_unenc
            file_full_path =  settings.INPUTFILES_PATH + file_name
            try:
                decrypted_file = open(file_full_path, 'w')
            except:
                print "Error opening decrypted instance file for writing"
            #write to file
            print 'writing', file_name, 'to', server_root, 'to validate'
            decrypted_file.write(decrypted_stream)
            decrypted_file.close()
            if not os.path.exists(file_full_path):
                print "An decrypted file wasn't written"
            else:
                print "A file was written at: ", file_full_path
        
        #read in candidate XML file
#        if use_encryption:
#            try:
#                unencrypted_file = open(file_full_path, 'r') 
#            except: 
#                print "couldn't open decrypted file for reading"
#            
#        if not use_encryption:
#            try:
#                unencrypted_file = open(file_full_path, 'r') 
#            except: 
#                print "couldn't open unencrypted file for reading"
            
        #validate  XML instance
        if not os.path.exists(schema_path):
            #print "schema folder already exists at: ", schema_path
            try:
                print "creating schema folder at: ", schema_path
                os.mkdir(schema_path)
            except:
                print "couldn't create: ", schema_path
        
        #Get the schema if it doesn't exist in the folder
        try:    
            try:
                schema = open(schema_full_path, 'r')
                #schema = open(schema_full_path,'r')
            except:        
                urllib.urlretrieve(schema_url, schema_full_path)
                schema = open(schema_full_path,'r')
        except:
            print "Error locating schema file"
        schema_parsed = etree.parse(schema)
        schema.close()
        schema_parsed_xsd = etree.XMLSchema(schema_parsed)
        
        file_name = file_prefix + file_suffix_unenc
        try:
            validation_candidate_file = open(file_full_path, 'r')
        except Exception, e: 
            print "couldn't open file for validation"
            return e    
        try:
            instance_parsed = etree.parse(validation_candidate_file)
            validation_candidate_file.close()
            results = schema_parsed_xsd.validate(instance_parsed)
            if results == True:
                message = '202: The posted xml (locally at %s) successfully validated against %s .' % (file_name, schema_url)
                response.status_int = 202
                print message
                #move valid file over to regular synthesis input_files directory for shredding
                print "moving valid file ", file_name, "over to input_files for shredding"
                import fileutils
                fileutils.moveFile(file_full_path, settings.INPUTFILES_PATH[0])
                return message
            elif results == False:
                message = 'The posted xml (locally at %s) did not successfully validate against %s .' % (file_name, schema_url)
                try:
                    message = message + schema_parsed_xsd.assertValid(instance_parsed)
                    response.status_int = 200
                    print message
                    return message
                except etree.DocumentInvalid, error:
                    message = '452: Document Invalid Exception.  Here is the detail:' + str(error)
                    response.status_int = 200
                    print message
                    return message
            elif results == None:
                message = "500: The validator erred and couldn't determine if the xml \
                was either valid or invalid."
                response.status_int = 500
                print message
                return message
            else:
                fallback_message = "500: You should not see this, since it means the request wasn't handled properly"
                return fallback_message
        except etree.XMLSyntaxError, error:
            message =  '452: XML Parse Error.  Here is the detail:  ' + str(error)
            print message            
            return message
        except etree.XMLSyntaxError, error:
            message =  '452: Document Invalid Exception.  Here is the detail:  ' + str(error)
            print message
            response.status_int = 200
            return message
    
