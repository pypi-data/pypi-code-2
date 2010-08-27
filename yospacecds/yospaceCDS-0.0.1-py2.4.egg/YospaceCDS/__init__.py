#!/usr/bin/python

import ws

# The names this package exports
__all__ = [
# WebService Proxies
	'ContentService',
	'MediaItemService',
# Simple Helper Functions
	'CreateMediaItem',
	'StatusMediaItem',
	'DeleteMediaItem',
	'GetMediaItems',
# MediaItem Status values
	'MEDIAITEM_INVALID',
	'MEDIAITEM_VALID',
	'MEDIAITEM_UNKNOWN',
]

ContentService = ws.ContentService
MediaItemService = ws.MediaItemService

MEDIAITEM_INVALID = 0
MEDIAITEM_VALID = 1
MEDIAITEM_UNKNOWN = 2

# Quick helper functions - MediaItemService

def CreateMediaItem( # {{{
	username,
	password,
	ContentURL,
	ContentGroupID,
	HQ=False,
	LargeFormat=None,
	MIMEType=None,
	RSSPublishDate=None,
	RSSItemTitle=None,
	RSSItemDescription=None,
	RSSTeaserText=None,
	ThumbnailURL=None,
	debug=0):
	"""Creating a MediaItem

	All MediaItem object must belong to a Content Group.  If you are intending to use yospaceCDS as an unstructured store, then you simply need to create a single Content Group in your account and assign all MediaItems to that.  There is no limit to the number of MediaItem objects that can exist within a Content Group.  

	However, if you would like to output items from yospaceCDS within feeds, then you will need to create the Content Groups you need, and assign these to the appropriate Output Feeds.  More information can be found on our chapters covering Content Groups and Output Feeds.

	To create a MediaItem within yospaceCDS the following parameters are supported:
	
Account Name / Password

URL to Asset to Upload
    an internet accessible URL of the video content.  Supported video formats are described in our Quick Start Guide.

Content Group ID
    you must create at least one Content Group within the yospaceCDS Content Management interface and use this ID.

HQ Processing Required
    specify true or false depending on whether you want H.264 processing on your video content. H.264 processing improves the quality of video for modern SmartPhone devices.

Large Format Required (optional)
    specify true or false depending on whether you want the video available in a large format suitable for the iPad. This option makes the content available in 640x360 (or 512x384 for 4:3) subject to the source content being available in the same or higher resolution.  This parameter is optional, and defaults to false if not supplied.

MIME type (optional)
    the MIME type of the uploaded content (if different from the MIME type given by the server)

RSS Publish Date
    the publishDate of the video (used for RSS output feeds to determine ordering).  If you do not set this, the time and date of ingestion is used instead. [

    Dates are specified in the format as determined by xsd:dateTime which follows the form defined by Chapter 5.4 in ISO 8601, which is:

     [-]CCYY-MM-DDThh:mm:ss[Z|(+|-)hh:mm] 

     The time zone may be specified as Z (UTC) or (+|-)hh:mm. Time zones that aren't specified are considered undetermined.

     Example valid timestamps are:

         * 2009-10-26T21:32:52
         * 2009-10-26T21:32:52+02:00
         * 2009-10-26T19:32:52Z
         * 2009-10-26T19:32:52+00:00

RSS Item Title (optional)
     the title of the video, as shown in an RSS Feed or on the User Choice Page

RSS Item Description (optional)
     the description of the video, as shown in an RSS Feed or on the User Choice Page

RSS Teaser Text (optional)

Thumbnail URL (optional)
     a URL of a thumbnail image that will be associated with the video within an RSS Feed.  If you do not set this and publish this item via an RSS Feed, a default thumbnail grabbed from a few seconds into the video will be used instead. 


The return value is the MediaItem ID
	"""
	_proxy = MediaItemService(username, password, throw_faults=1, debug=debug)
	_params = {
		'contentUrl': ContentURL,
		'contentGroupId': ContentGroupID,
		'hq': HQ,
	}
	if LargeFormat != None:
		_params['largeFormat'] = LargeFormat
	if MIMEType != None:
		_params['mimeType'] = MIMEType
	if RSSPublishDate != None:
		_params['rssPubDate'] = RSSPublishDate
	if RSSItemTitle != None:
		_params['rssTitle'] = RSSItemTitle
	if RSSItemDescription != None:
		_params['rssItemDescription'] = RSSItemDescription
	if RSSTeaserText != None:
		_params['rssTeaserText'] = RSSTeaserText
	if ThumbnailURL != None:
		_params['thumbnailUrl'] = ThumbnailURL
	_response = _proxy.createMediaItem(**_params)
	return _response.mediaItemId
# }}}

def StatusMediaItem( # {{{
	username,
	password,
	MediaItemID,
	debug=0):
	"""Checking MediaItem Status

A MediaItem object will not be immediately available for end-users after creating it. yospaceCDS must perform intermediate processing work on the clip before it is available. In order to determine whether the clip is ready for end-user access, you can check it status using the statusMediaItemRequest call.

It requires:

Account Name / Password
MediaItem ID
    The ID that you will have received from a successful MediaItem creation. 


The return value is a tuple of state code (From the table below) and a descriptive word
State Code      State Description
    0           Invalid (The processing failed)
	1           Valud (Ready for use)
	2           Unknown (Processing is currently in progress)
	"""
	_proxy = MediaItemService(username, password, throw_faults=1, debug=debug)
	_params = {
		'mediaItemId': MediaItemID,
	}
	_response = _proxy.statusMediaItem(**_params)
	return (int(_response.mediaItemStateCode), _response.mediaItemStateDescription)
# }}}

def DeleteMediaItem( # {{{
	username,
	password,
	MediaItemID,
	debug=0):
	"""MediaItem Deletion

If you no longer need a MediaItem object, it is necessary to delete it using the deleteMediaItemRequest method.

The call requires:

Account Name / Password
MediaItem ID
    The ID that you will have received from a successful MediaItem creation

There is no return value
	"""
	_proxy = MediaItemService(username, password, throw_faults=1, debug=debug)
	_params = {
		'mediaItemId': MediaItemID,
	}
	_response = _proxy.statusMediaItem(**_params)
	return True
# }}}

# vim:foldmethod=marker
