from flea import TestAgent

import string
from swab import Swab, show_variant

def test_identity_set_and_preserved():

    def app(environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/plain')])
        return []

    s = Swab('/tmp/.swab-test-data')

    agent = TestAgent(s.middleware(app))
    r = agent.get('/')

    assert 'swab=' in r.response.get_header('Set-Cookie'), \
            "Swab cookie not set on first request"

    r = r.get('/')
    assert 'swab=' not in r.response.get_header('Set-Cookie'), \
            "Swab cookie reset on subsequent request"

def test_override_identity():

    def app(environ, start_response):
        environ['swab.id'] = '1234567890'
        start_response('200 OK', [('Content-Type', 'text/plain')])
        return []

    s = Swab('/tmp/.swab-test-data')
    agent = TestAgent(s.middleware(app))
    assert 'swab=1234567890;' in agent.get('/').response.get_header('Set-Cookie')

def test_show_variants_produces_all_variants():

    def app(environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/plain')])
        return [show_variant('exp', environ)]

    s = Swab('/tmp/.swab-test-data')
    s.addexperiment('exp', string.digits, 'goal')

    variants = set()
    for i in range(100):
        agent = TestAgent(s.middleware(app))
        variants.add(''.join(agent.get('/').response.content))
    assert len(variants) == 10

def test_show_variant_returns_requested_variant_in_debug_mode():

    def app(environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/plain')])
        return [show_variant('exp', environ)]

    s = Swab('/tmp/.swab-test-data', debug=True)
    s.addexperiment('exp', ['a', 'b'], 'goal')

    variants = set()
    for i in range(100):
        agent = TestAgent(s.middleware(app))
        variants.add(''.join(agent.get('/?swab.exp=a').response.content))
    assert variants == set('a')
