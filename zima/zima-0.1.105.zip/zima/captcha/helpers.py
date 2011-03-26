# -*- coding:utf-8 -*-
# Captcha help functions
import random

#------------------------------------------------------------------
# Мутаторы
def mutateToImg(text, cfg):
    import Image, ImageDraw, ImageFont
    # 'cmunrb.otf'
    font = ImageFont.truetype(cfg.fontName, 16, encoding='unic')
    rect = font.getsize(text)
    img = Image.new('RGBA', rect)
    draw = ImageDraw.Draw(img)
    draw.text((0,0), unicode(text, 'utf-8'), fill='black', font=font)
    return img.rotate(
        random.randint(-cfg.rotateFactor, cfg.rotateFactor), expand=True)

def mutateToFormulaImg(text):
    import matplotlib.mathtext as mtext
    import Image, ImageDraw, ImageFont
    parser = mtext.MathTextParser('Bitmap')
    res = parser.parse(r'$%s$' % (text,), dpi=100)[0]
    return Image.fromstring(
        'RGBA', (res.get_width(), res.get_height()), res.as_rgba_str())

#------------------------------------------------------------------
# Исключения
class CaptchaExpiredError(Exception):
    def __init__(self):
        self.value = ''
    def __str__(self):
        return repr(self.value)
