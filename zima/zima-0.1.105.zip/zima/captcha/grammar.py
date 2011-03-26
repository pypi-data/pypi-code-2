# -*- coding: utf-8 -*-
# Grammar captcha

import random
import re

class Captcha():

    """ Граммар капча  """

    def __init__(self, cfg):

        self._cfg = cfg

        self._dict = []

        for pattern in re.split(
            '[\.\?\!]', 
            open(self._cfg.source).read().decode('utf-8').replace('\n',' ')):
            if 30 < len(pattern) < 100:
                self._dict.append(
                    pattern.replace('\n', ' ').replace('  ', ' '))

    def _mutate(self, text):
        
        # Единичные мутаторы

        def strip_commas(text):
            """ Убирает запятые """
            if text.find(',') <> -1:
                return True, text.replace(',', ' ')
            else:
                return False, text

        def swapchars(text):
            """ Обменивает местами пару букв"""
            pos = random.randint(0, len(text))
            if re.search(r'(\S)(\S)', text):
                return True, text[:pos] +  (re.sub(
                        r'(\S)(\S)', r'\2\1', text[pos:], count=1))
            else:
                return False, text

        def toggleParts(parts, inWord=True):
            """ Рандомно меняет спорные части, типа -тся и -ться, -н-
            и -нн- и т.п."""

            if inWord:
                parts = (u'\\S', parts[0], parts[1], u'\\S')
            else:
                parts = (u'', parts[0], parts[1], u'')

            def fun(text):
                def replacer(m):
                    val = parts[random.randint(1,2)]
                    return u'%s%s%s' % (m.group(1), val, m.group(3))

                if re.search(u'(%s)(%s|%s)(%s)' % parts, text):
                    return True, re.sub(
                        u'(%s)(%s|%s)(%s)' % parts, replacer, text)
                else:
                    return False, text

            return fun

        tsya = toggleParts([u'тся', u'ться'], inWord=False)
        ts = toggleParts([u'тс', u'ц'], inWord=False)
        nnn = toggleParts([u'нн', u'н'])
        zh = toggleParts([u'жы', u'жи'])
        sh = toggleParts([u'шы', u'ши'])
        mzn = toggleParts([u'чь', u'ч'], inWord=False)
        mzn1 = toggleParts([u'шь', u'ш'], inWord=False)

        mutators = [swapchars, tsya, mzn, nnn, ts, zh, zh, sh,
                    nnn, ts, mzn, ts, tsya, tsya, tsya, zh, sh,
                    tsya, tsya, mzn, mzn1]

        applied = 0
        tries = 100

        while applied < self._cfg.mutationsNum and tries > 0:
            mutateResult = random.sample(mutators, 1)[0](text)
            if mutateResult[0]:
                applied += 1
                text = mutateResult[1]
            tries -= 1

        return applied == self._cfg.mutationsNum, text

    def generate(self):
        successfullyMutated = False
        while not successfullyMutated:
            target = random.sample(self._dict, 1)[0]
            mutationResult = self._mutate(target)
            successfullyMutated = mutationResult[0]
        return target, mutationResult[1]

    def check(self, userAnswer, rightAnswer):
        return userAnswer.strip() == rightAnswer.strip()


def test():
    class Cls():
        pass
    a = Cls()
    a.source = 'karam.txt'
    a.mutationsNum = 4
    cap = Captcha(a)
    return cap.generate()[1]

if __name__ == '__main__':
    print test().encode('utf-8')
