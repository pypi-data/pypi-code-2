import os
import sys
import mimetypes
import tempfile
import urllib2

try:
    import json
except ImportError:
    import simplejson as json

from poster.encode import multipart_encode, MultipartParam
from poster.streaminghttp import register_openers

from socialtext import exceptions
from socialtext.resources.base import Resource, Manager, get_id
from socialtext.urls import make_data_url


class UploadManager(Manager):
    """
    Upload files to the Socialtext Appliance.
    """
    def create(self, filename_or_url):
        """
        Upload a local file to the Socialtext appliance.
        
        :param: filename_or_url: Either the path to a file on the local
                                 file system or a public URL.
        :rtype: An ID-hash string
        """
        
        register_openers()
        
        user_agent = self.api.client.USER_AGENT
        authorization = self.api.client.authorization()
        url = self.api.client._get_full_url(make_data_url("uploads"))
        
        file_param = None
        
        # really basic check to see if a URL was provided.
        is_url = (filename_or_url.find("http") == 0)
        
        if is_url:
            # get the filename from the end of the URL
            file_name = filename_or_url[filename_or_url.rfind('/') + 1:]
            
            # GET the file at the URL
            file_req = urllib2.Request(filename_or_url)
            file_resp = None
            try:
                file_resp = urllib2.urlopen(file_req)
            except urllib2.HTTPError, exc:
                raise exceptions.from_urllib2_exception(exc)
            
            # create a temporary directory
            temp_dir = tempfile.mkdtemp()
            
            temp_file_path = os.path.join(temp_dir, file_name)
            
            # create a file in the temporary directory
            temp_file = open(temp_file_path, "wb")
            
            # stream the URL response to the temp file
            chunk_size = 16 * 1024
            while True:
                chunk = file_resp.read(chunk_size)
                if not chunk:
                    break
                temp_file.write(chunk)
            
            # we need to close the file so it can be opened
            # for reading
            temp_file.close()
            
            # some URLs might not have an extension
            # so let's use the Content-Type header
            # just to be safe
            file_type = file_resp.info().gettype()
            
            file_param = MultipartParam("file",
                filename=file_name,
                filetype=file_type,
                fileobj=open(temp_file_path, "rb")
            )
        else:
            # we are using a local file
            file_param = MultipartParam.from_file("file", filename_or_url)
        
        # create the multipart form headers and data
        datagen, headers = multipart_encode([file_param])
        
        # create a new Request to send the file to Socialtext
        request = urllib2.Request(url, datagen, headers)
        request.get_method = lambda: "POST"
        request.add_header("Authorization", authorization)
        
        resp = None
        
        # execute the request
        try:
            resp = urllib2.urlopen(request)
        except urllib2.HTTPError, exc:
            raise exceptions.from_urllib2_exception(exc)
        
        # transform the JSON response to a dict
        json_resp = json.loads(resp.read())
        
        return json_resp['id']  # the hash-ID
