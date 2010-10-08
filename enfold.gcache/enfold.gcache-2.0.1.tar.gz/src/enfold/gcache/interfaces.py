################################################################################
#
# Copyright (c) 2010 Enfold Systems, LLC
# All Rights Reserved.
#
# enfold.gcache interfaces
#
# $Id: httpcacheprovider.py -1   $
#
################################################################################

from zope import interface

HEADERS_LOG_LEVEL = 13


class Uncachable(Exception):
    """ key is not cachable """


class ValidationError(KeyError):
    """ can't validate key """


class ValidationGotNewItem(ValidationError):
    """ raised when the validation of an item fails, but new data is provided."""


class HTTPValidationError(ValidationError):
    """ can't validate http request """


class ICacheProvider(interface.Interface):
    """ cache records provider """

    def provide(key):
        """ provide cache value for key
        return: new_key, meta, data """

    def validate(key, meta, data, validator=None, *args, **kw):
        """ validate cached record """


class IHTTPCacheProvider(ICacheProvider):
    """ http cache provider, key is Request-URI """

    metadataFactory = interface.Attribute("Metadata factory")

    def open_host(scheme, host, port=None):
        """ open host """

    def done_with_host(connection, response):
        """ close host """

    def host_failed(connection):
        """ notify host is failed """

    def do_provide(schema, host, url):
        """ load data from url """

    def do_validate(scheme, host, url, meta, data, request_headers=None):
        """ validate http url """


class IMetadata(interface.Interface):
    """ generic cache metadata """


class IHTTPMetadata(IMetadata):
    """ metadata """

    def __init__(requestTime, request, response):
        """ create new metadata object """
