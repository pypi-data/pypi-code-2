def process_template(code):
    '''Return title/page_title/extra integrated into template'''
    title, page_title, extra = process_messages(code)

    return TEMPLATE % {
        'title': title,
        'page_title': page_title,
        'extra_info': extra,
        'status_code': code
    }


def process_messages(code):
    if code == 400:
        title = page_title = 'Bad request'
        extra = 'Your browser sent a request that this server could not understand.'
    elif code == 401:
        title = page_title = 'Unauthorized'
        extra = 'This server could not verify that you are authorized to access the document requested. Either you supplied the wrong credentials (e.g., bad password), or your browser doesn\'t understand how to supply the credentials required.'
    elif code == 402:
        title = page_title = 'Payment required'
        extra = 'The server is requesting you pay some toll fees before you can see this resource'
    elif code == 403:
        title = page_title = 'Forbidden'
        extra = 'You don\'t have permission to access {{ request.path }} on this server.'
    elif code == 405:
        title = page_title = 'Method not allowed'
        extra = 'The requested method {{ request.META.REQUEST_METHOD }} is not allowed for the URL {{ request.path }}.'
    elif code == 406:
        title = page_title = 'Not acceptable'
        extra = 'An appropriate representation of the requested resource {{ request.path }} could not be found on this server.'
    elif code == 407:
        title = page_title = 'Proxy authentication required'
        extra = 'This server could not verify that you are authorized to access the document requested. Either you supplied the wrong credentials (e.g., bad password), or your browser doesn\'t understand how to supply the credentials required.'
    elif code == 408:
        title = page_title = 'Request timeout'
        extra = 'Server timeout waiting for the HTTP request from the client.'
    elif code == 409:
        title = page_title = 'Conflict'
        extra = 'The request could not be processed because of conflict in the request.'
    elif code == 410:
        title = page_title = 'Gone'
        extra = 'The requested resource {{ request.path }} is no longer available on this server and there is no forwarding address. Please remove all references to this resource.'
    elif code == 411:
        title = page_title = 'Length required'
        extra = 'A request of the requested method {{ request.META.REQUEST_METHOD }} requires a valid Content-length.'
    elif code == 412:
        title = page_title = 'Precondition failed'
        extra = 'The precondition on the request for the URL {{ request.path }} evaluated to false.'
    elif code == 413:
        title = page_title = 'Request entity too large'
        extra = 'The requested resource {{ request.path }} does not allow request data with {{ request.META.REQUEST_METHOD }} requests, or the amount of data provided in the request exceeds the capacity limit.'
    elif code == 414:
        title = page_title = 'Request-URI too large'
        extra = 'The requested URL\'s length exceeds the capacity limit for this server.'
    elif code == 415:
        title = page_title = 'Unsupported media type'
        extra = 'The supplied request data is not in a format acceptable for processing by this resource.'
    elif code == 416:
        title = page_title = 'Requested range not satisfiable'
        extra = 'Portion of file requested is not satisfiable.'
    elif code == 417:
        title = page_title = 'Expectation failed'
        extra = 'The expectation given in the Expect request-header field could not be met by this server.'
    elif code == 418:
        title = page_title = 'I\'m a teapot'
        extra = 'Unfortunately this coffee machine is out of coffee.'
    elif code == 422:
        title = page_title = 'Unprocessable entity'
        extra = 'The server understands the media type of the request entity, but was unable to process the contained instructions.'
    elif code == 423:
        title = page_title = 'Locked'
        extra = 'The requested resource is currently locked. The lock must be released or proper identification given before the method can be applied.'
    elif code == 424:
        title = page_title = 'Failed dependency'
        extra = 'The method could not be performed on the resource because the requested action depended on another action and that other action failed.'
    elif code == 425:
        title = page_title = 'Unordered collection'
        extra = ''
    elif code == 426:
        title = page_title = 'Ugrade required'
        extra = 'The requested resource can only be retrieved using SSL. The server is willing to upgrade the current connection to SSL, but your client doesn\'t support it. Either upgrade your client, or try requesting the page using https:// .'
    elif code == 501:
        title = page_title = 'Not implemented'
        extra = '{{ request.META.REQUEST_METHOD }} to {{ request.path }} not supported.'
    elif code == 502:
        title = page_title = 'Bad gateway'
        extra = 'The proxy server received an invalid response from an upstream server.'
    elif code == 503:
        title = page_title = 'Service unavailable'
        extra = 'The server is temporarily unable to service your request due to maintenance downtime or capacity problems. Please try again later.'
    elif code == 504:
        title = page_title = 'Gateway timeout'
        extra = 'The proxy server did not receive a timely response from the upstream server.'
    elif code == 505:
        title = page_title = 'HTTP version not supported'
        extra = 'The server does not support the HTTP protocol version used in this request.'
    elif code == 507:
        title = page_title = 'Insufficient storage'
        extra = 'The method could not be performed on the resource because the server is unable to store the representation needed to successfully complete the request. There is insufficient free space left in your storage allocation.'
    elif code == 509:
        title = page_title = 'Bandwidth limit exceeded'
        extra = 'The server is temporarily unable to service your request due to the site owner reaching his/her bandwidth limit. Please try again later.'
    elif code == 510:
        title = page_title = 'Not extended'
        extra = 'A mandatory extension policy in the request is not accepted by the server for this resource.'

    return (title, page_title, extra)


TEMPLATE = '''
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html lang="en">
<head>
  <meta http-equiv="content-type" content="text/html; charset=utf-8">
  <title>%(title)s</title>
  <meta name="robots" content="NONE,NOARCHIVE">
  <style type="text/css">
    html * { padding:0; margin:0; }
    body * { padding:10px 20px; }
    body * * { padding:0; }
    body { font:small sans-serif; background:#eee; }
    body>div { border-bottom:1px solid #ddd; }
    h1 { font-weight:normal; margin-bottom:.4em; }
    h1 span { font-size:60%%; color:#666; font-weight:normal; }
    table { border:none; border-collapse: collapse; width:100%%; }
    td, th { vertical-align:top; padding:2px 3px; }
    th { width:12em; text-align:right; color:#666; padding-right:.5em; }
    #info { background:#f6f6f6; }
    #summary { background: #ffc; }
    #explanation { background:#eee; border-bottom: 0px none; }
  </style>
</head>
<body>
  <div id="summary">
    <h1>%(page_title)s <span>(%(status_code)s)</span></h1>
    <table class="meta">
      <tr>
        <th>Request Method:</th>
        <td>{{ request.META.REQUEST_METHOD }}</td>
      </tr>
      <tr>
        <th>Request URL:</th>
      <td>{{ request.build_absolute_uri|escape }}</td>
      </tr>
    </table>
  </div>
  <div id="info">
    <p>
      %(extra_info)s
    </p>
  </div>
  <div id="explanation">
    <p>
      You're seeing this error because you have <code>DEBUG = True</code> in
      your Django settings file. Change that to <code>False</code>, and Django
      will display a standard %(status_code)s page.
    </p>
  </div>
</body>
</html>
'''
