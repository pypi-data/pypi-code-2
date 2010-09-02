from pipestack.ensure import ensure_function_marble as ensure
import urlconvert
import urllib

@ensure('errordocument')
def return_401_response(marble):
    # Set an error document page
    marble.bag.errordocument.render(status='401 Unauthorised')

@ensure('errordocument')
def redirect_to_signin(marble):
    # Set an error document page
    marble.bag.errordocument.render(status='401 Unauthorised')
    # But change the behaviour to redirect instead
    marble.bag.http.response.status = '301 Reirect'
    marble.bag.http.response.headers = [('Location', '/auth/login?referrer=%s'%(urllib.quote(urlconvert.build_url(**marble.url_parts))))]

