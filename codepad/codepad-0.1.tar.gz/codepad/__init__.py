#encoding: utf-8

import sys
import requests

class CodePad(object):
  def __init__(self, code=None, lang="C"):
    self.code = code
    self.lang = lang
    self.data = {'code': self.code, 'lang': self.lang, 'submit': 'Submit'}

  def save(self):
    r = requests.post("http://codepad.org/", data = self.data)
    if r.ok:
      return r.url
    return None


