from pswinpy.request import Request
from pswinpy.http_sender import HttpSender

class API(object):

  def __init__(self, username, password):
    self.request = Request(username, password)

  def sendSms(self, to=None, text=None, sender='', TTL='', tariff='', serviceCode='', deliveryTime=''):
    if to and text:
      self.request.addMessage(to, text, sender, TTL, tariff, serviceCode, deliveryTime)

    sender = HttpSender()
    result = sender.send(self.request)

    return result
