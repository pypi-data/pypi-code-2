#! -*- coding: UTF-8 -*-
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from StringIO import StringIO

# Change these values to match your needs
cert_file = '/home/apyb/certificado%s.png'
font_file = '/home/apyb/verdana.ttf'

def generate(name, role, year=2010, url=None):

    img = Image.open(cert_file % year)
    draw = ImageDraw.Draw(img)

    font = ImageFont.truetype(font_file, 128)

    pos = 1750, 1620
    draw.text(pos, name, font=font)

    pos = 3500 ,2230
    draw.text(pos, role, font=font)

    if url:
        pos = 3060, 3400
        font = ImageFont.truetype(font_file, 45)
        draw.text(pos, url, font=font)

    output = StringIO()
    img.save(output, format='PNG')

    return output.getvalue()

if __name__ == '__main__':
    print generate('Dorneles Tremea', 'participante', 2010, 'http://www.pythonbrasil.org.br/2010/verifica?n=2')
