"""
QRcode Django filter
========================

- Copyright (c) 2011 Zenobius Jiricek
    - Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php


## Usage

_filter_

{{ Text|qrcode }}

{{ Text|qrcode:size }}

_block tag_

{% QrCode text size %}


ie :

{{ '555-35432'|qrcode:2 }}
{% QrCode '555-35432' 2 %}


or without pixel size

{{ '555-35432'|qrcode }}
{% QrCode '555-35432' %}

returns
    <img src="data:image/png;base64,blahblahblah" title="555-35432"/>
"""

import re
import cStringIO
from base64 import b64encode

from django import template
from django.template import Context, loader
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from django_qrcode_filter.lib.QrCodeLib import QRCode

IMAGE_ERROR = """<img width="22" height="22" title="%(title)s" alt="%(message)s" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABYAAAAWCAYAAADEtGw7AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAN1wAADdcBQiibeAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAASdEVYdFRpdGxlAFBhcGVyIFNoZWV0c7mvkfkAAAAXdEVYdEF1dGhvcgBMYXBvIENhbGFtYW5kcmVp35EaKgAAACd0RVh0RGVzY3JpcHRpb24Ad2l0aCBhIEhVR0UgaGVscCBmcm9tIEpha3VihlQHswAAA4RJREFUOI2lldtrXUUUxn9rzT7nJGmwDyZFGsWalkYQk+Z6kvoi1CdRChYrFPRPEClI/wZfBME3waAi+KA2tYpSBLEa7SX3nBZKUkTU1vokJkZzMjPLh9l7m+uLDszew157f/Ot71uztpgZAJ99ceGgqr4WYzwdo1XBKGJmhoisiMiSRZsKMXxrxgfPnXx+gz2GFB9/+vnE+NEjPS8dOdyjqrrjxRA83nvWm+vcufvL+o2bi7/HEM8Z9t7pU2finsATFz/88+Qzp9pWVlcIwRNjTNMiMQYajUWGh+pUqzUqWQUzo3FzYX1p+dbPIcTjZ1548bfNwCU170NVRNjYaBJCIMRAtIjFiJnR29tHiIHVtT/44cfbrK6u0N83WBsaqHeDffXu++NtuwKHEAArmVo0zBJoSkpwojhxtO/bx/LtZUSEw91H5NGjj/UAn4y/85bbBdhjuVEJMAdNT5mfmyViiCq1Wg0fQ2luX+8x13Ww6wkfwpM7gX0AI2lqlm+QszXoPdaHFMaI0tbayqUvL3H58teICA89eKjFzJ7eqXEIaVEwxvKIsdhYBITpmakCmQOdnXTe38G9e79yfuI8++/bD/DsHhqzCTAxFREGBgZQEXof78txhZbWVg498jAnnjpBvT6MqhK8737jzdcruwIXgAkBnMtQVebn50ovREBVUFVUlfb2djo6OhBRgg9um8Y+xxKQxOpGo4FziojQ3z+Icw5VZWZ6GhXFqcOpQ9WBQDMvVYBsM+NUBQlUEAYGh1ARECmNQ/Ln6hKJXDxBiCHig9/dPKeJSaVSIcsynMtwzjE7N4uqwzlH5lK5qirqHM5pSa5gvFVjAVHHwuIClUo1pepSuvWRUbKsQub+3ez61DVEJEmRkwt+uxQ+IAgqQn1kFNWk7ZaZ659fGK2PIaKl23szhtIgFS1dV3Vcu34VUcVpRubyTJwjWZBgog+lpFs0FhGyLEOkYFbWCWP146gUWWi5RoQrV7/DzAgx7KyKmDchoOwBeYSIIoBY2FIhRW8ZGa4jInjvy7ItGccYN2K0Yr1tBr6/MokPnhBSuj6E1LdDIMbU59ebTQvlEU7sKq+eO/vR3PxsjDHafxlLS7fslbMvTwI1MyMTEQE6L0xc/Hht7a8DLa0tYxajS/tZeWjYfC9jhSDE5oafmfxm8m3gARH5SfIfZRXoAir8v+GBO2b29z8Itzjug3adCgAAAABJRU5ErkJggg==" />"""
IMAGE_QRCODE="""<img src="%(datauri)s" title="%(title)s" alt="%(message)s">"""

register = template.Library()

@register.tag(name="QrCode")
def QrCodeTag ( parser, token ):
	"""
		QrCode Tag
			@ tag_name : provided by default by the Django Template System
			@ tag_data : the data to encode into the qrcode
			[@ tag_size] : the size of each pixel in the qrcode

		Syntax :
			{% QrCode data [pixel_size] %}
	"""
	try:
		tokens = token.split_contents()
		tag_name = tokens[0]
		tag_data = tokens[1]
		if len(tokens) > 2:
			tag_size = tokens[2]

	except ValueError:
		raise template.TemplateSyntaxError, __doc__

	return QrCodeNode( data = tag_data, size = tag_size )

class NavigationBarNode ( template.Node ):
	def __init__ ( self, data = None, size=None ):
		self.data = data
		self.size = size

	def render ( self, context ):
		return RenderQrcode(data = self.data, size = self.size)


@register.filter(name="qrcode")
def QrCodeFilter(value=None):
	size = None
	if ":" in value :
	
		try :
			tokens = value.split(":")
			data = tokens[0]
			size = tokens[1]
		except:
			return ""
	else :
		data = value
		
	return RenderQrcode(data = data, size = size)
	

def RenderQrcode(data=None, size=None):
	image = None
	error = None
	
	try :
		qrCodeObject = QRCode(self.size, QRErrorCorrectLevel.L)
		qrCodeObject.addData( self.data )
		qrCodeObject.make()
		qrCodeImage = qrCodeObject.makeImage(
			pixel_size = self.size,
			dark_colour = "#000000"
		)
		qrCodeImage_File = StringIO.StringIO()
		qrCodeImage.save( qrCodeImage_File , format= 'PNG')
		datauri ="data:image/png;base64,%s" % b64encode( qrCodeImage_File.getvalue() )
		qrCodeImage_File.close()

		image = """<img src="%(uri)s" title="%(data)s">""" % {
			"title" : self.data,
			"message" : "QrCode",
			"datauri" : datauri
		}
	except :
		error = IMAGE_ERROR % {
			"title" : data,
			"message" : "Failed to create qrcode for provided data."
		}

	if image :
		output = image
	else:
		output = error
		
	return mark_safe(outputmark_safe)

