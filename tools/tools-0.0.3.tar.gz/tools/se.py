# -*- coding: utf-8 -*-
from grab import Grab
from tools.memoized import memoized
from tools.captcha.util import solve_captcha
from urlparse import urlsplit, urljoin, urlunsplit
import urllib

def strip_www(value):
    if value.startswith('www.'):
        value = value[4:]
    return value

def yandex_request(query_url):
    g = Grab(cookiefile='var/yandex.cookies')
    g.go(query_url)

    while g.search(u'<title>Ой!') is not None:
        url = g.css('.b-captcha__image').get('src')
        solution = solve_captcha(g.clone(), url)
        g.set_input('rep', solution)
        g.submit()
        if g.search(u'<title>Ой!') is None:
            g.go(query_url)
    return g


@memoized
def yandex_index_size(host):
    def calc():
        api_url = 'http://yandex.ru/yandsearch?site=%s' % urllib.quote(host)
        print api_url
        g = yandex_request(api_url)

        text = g.css_text('.b-head-logo__text')
        try:
            count = int(g.css_number('.b-head-logo__text'))
        except AttributeError:
            return 0
        if u'тыс' in text:
            count = count * 1000
        if u'млн' in text:
            count = count * 1000000
        return count
    # Make two reqeests to avaid strange situation
    # when sometimes yandex returns 10
    return max(calc(), calc())


def google_request(query_url):
    g = Grab(cookiefile='var/google.cookies', log_dir='log')
    g.go(query_url)

    while g.search('please type the characters below') is not None:
        url = g.get_xpath('//img', lambda x: 'sorry' in x.get('src')).get('src')
        solution = solve_captcha(g.clone(), url)
        g.set_input('captcha', solution)
        g.submit()
        if g.search('please type the characters below') is None:
            g.go(query_url)

    return g


@memoized
def google_index_size(host):
    host = strip_www(host)
    www_host = 'www.' + host
    query = 'site:%s | site:%s' % (host, www_host)
    api_url = 'http://www.google.ru/search?hl=ru&safe=off&q=%s' % urllib.quote(query)
    g = google_request(api_url)

    if g.search(u'Не найдено ни одного') > -1:
        return 0
    else:
        count = int(g.get_xpath_number(u'//div[contains(text(), "Результатов:")]', ignore_spaces=True))
        return count


@memoized
def in_yandex_index(url):
    parts = list(urlsplit(url))
    parts[1] = strip_www(parts[1])
    non_www_url = urlunsplit(parts) 
    parts[1] = 'www.' + parts[1]
    www_url = urlunsplit(parts) 
    query = 'url:%s | url:%s' % (www_url, non_www_url)
    api_url = 'http://yandex.ru/yandsearch?text=%s' % urllib.quote(query)
    g = yandex_request(api_url)
    count = len(g.itercss('.b-serp-item'))
    return count > 0


@memoized
def in_google_index(url):
    query = 'info:%s' % url
    api_url = 'http://www.google.ru/search?hl=ru&safe=off&q=%s' % urllib.quote(query)
    g = yandex_request(api_url)
    count = len(g.itercss('#res li.g'))
    return count > 0
