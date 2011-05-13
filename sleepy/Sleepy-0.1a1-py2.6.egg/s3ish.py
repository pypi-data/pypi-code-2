import s3
from pylons import cache, config

from sleepy.shorties import s
from sleepy.lonsies import _cache

DEFAULT_BUCKET = "drifty"

def service( bucket=None,
             key=None,
             secret=None,
             use_cache=True ):
    bucket = bucket if bucket is not None else DEFAULT_BUCKET
    def _create():
        return s3.S3Service( key
                              if key is not None
                              else config[ "s3_key" ],
                             secret
                              if secret is not None
                              else config[ "s3_secret" ] )[ bucket ]
    if use_cache:
        return _cache( use_cache ).get_cache( "s3",
                                              expire=60
                                 ).get( key=bucket,
                                        createfunc=_create )
    else:
        return _create()

def upload( key,
            value,
            scale=None ):
    if scale:
        value = scale_image( value,
                             scale )
    service().save( s3.S3Object( key,
                                 value,
                                 {} ),
                    { "x-amz-acl": "public-read" } )

def prefixed( prefix,
              bucket=None,
              key=None,
              secret=None,
              use_cache=True ):
    return service( bucket=bucket,
                    key=key,
                    secret=secret,
                    use_cache=use_cache ).keys( prefix=prefix )

def uri( path,
         bucket=None ):
    return s( "http://s3.amazonaws.com"
               "/{{ bucket }}"
               "/{{ path }}",
              bucket=bucket if bucket is not None else DEFAULT_BUCKET,
              path=path )
