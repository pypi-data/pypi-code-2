from pipestack.ensure import ensure_function_marble
import urlconvert
import urllib

@ensure_function_marble('errordocument')
def return_401_response(marble):
    # Set an error document page
    marble.bag.errordocument.render(status='401 Unauthorised')

@ensure_function_marble('errordocument')
def redirect_to_signin(marble):
    # Set an error document page
    marble.bag.errordocument.render(status='401 Unauthorised')
    # But change the behaviour to redirect instead
    marble.bag.http_response.status = '301 Redirect'
    marble.bag.http_response.header_list = [
        dict(
            name='Location', 
            value='/auth/login?referrer=%s'%(
                urllib.quote(urlconvert.build_url(**marble.url_parts))
            )
        )
    ]

