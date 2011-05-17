import logging
import re

from tools.captcha.error import CaptchaError

import settings

RE_SCRIPT = re.compile(r'<script[^>]+recaptcha\.net[^>]+>', re.S)
RE_SRC = re.compile(r'src="([^"]+)"')

captcha_module = __import__(settings.CAPTCHA_MODULE, globals(),
                            locals(), ['foo'])

def solve_captcha(g, url=None, rawdata=None):
    if url:
        logging.debug('Fetching captcha')
        g.request(url=url)
        rawdata = g.response.body
    logging.debug('Solving captcha')
    solution = captcha_module.solve_captcha(key=settings.CAPTCHA_KEY,
                                            fobj=rawdata)
    logging.debug('Captcha solved: %s' % solution)
    return solution


def solve_recaptcha(g):
    def fetch_challenge():
        for x in xrange(5):
            script = RE_SCRIPT.search(g.response.body).group(0)
            url = RE_SRC.search(script).group(1)

            g.request(url=url)
            html = g.response.body

            if not html:
                logging.error('Empty response from recaptcha server')
                continue

            server = re.compile(r'server\s*:\s*\'([^\']+)').search(html).group(1)
            challenge = re.compile(r'challenge\s*:\s*\'([^\']+)').search(html).group(1)
            url = server + 'image?c=' + challenge
            return challenge, url
        raise CaptchaError('Could not get valid response from recaptcha server')

    challenge, url = fetch_challenge()
    g.request(url=url)
    data = g.response.body

    solution = solve_captcha(g, url)
    return challenge, solution
