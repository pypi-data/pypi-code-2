# -*- coding: utf-8 -*-
from time import time
from json import loads as loadj, dumps as dumpj

from bottle import response, request, route

from zima import kv
from errors import InvalidCaptchaError, Captcha404Error

# Конструктор перехватчиков
def maker(cfg, hook):
    if not cfg.captcha:
        return []
    exec("from captcha.%s import generate, check" 
         % (cfg.captcha.type)) in locals()

    @route('/'.join(cfg.prefix + [cfg.captcha.url]))
    def f():
        """ Сгенерировать и отдать капчу """
        def regen():
            captcha, mime, answer = generate(cfg)
            kv[hid] = captcha
            kv[hid+'.meta'] = dumpj([mime, 
                                     answer, 
                                     time() + cfg.expires*60])
            return captcha, mime
    
        hid = 'c:%s' % request.environ['REMOTE_ADDR']
        captcha = None
        try:
            [mime, answer, expires] = loadj(kv[hid+'.meta'])
            if time() > expires:
                captcha, mime = regen()
        except KeyError:
            captcha, mime = regen()
        response.content_type = mime
        return capthca or kv[hid]

    def check(kval):
        """ Проверяет капчу """
        k, v = kval
        if k <> 'c':
            return kval
        hid = 'c:%s' % request.environ['REMOTE_ADDR']
        try:
            [mime, answer, expires] = loadj(kv[hid+'.meta'])
        except:
            raise Captcha404Error()
        
        if check(answer, v):
            kv[hid+'.passed'] = time()
            del kv[hid]
            del kv[hid+'.meta']
        else:
            raise InvalidCaptchaError()
        return kval

    return [('customField', check)]