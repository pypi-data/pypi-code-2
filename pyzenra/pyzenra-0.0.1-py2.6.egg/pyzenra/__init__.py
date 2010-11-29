#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import urllib2
import xml.dom.minidom

class Zenra(object):
    def __init__(self, yahoo_appid, position=u'動詞', text=u'全裸で',
                 base_url = 'http://jlp.yahooapis.jp/MAService/V1/parse'):
        self.appid = yahoo_appid
        self.position = position
        self.text = text
        self.base_url = base_url

    def zenrize(self, sentence):
        if ( len(self.appid) == 0 ):
            raise Exception('yahoo_appid is necessary!')
        elif ( len(sentence) == 0 ):
            raise Exception('Japanese sentece is necessary!')
        sentence = sentence.encode('utf-8')
        query = {"appid": self.appid ,
                 "sentence": sentence,
                 }
        query = urllib.urlencode(query)
        resp = urllib2.urlopen(self.base_url, query) 
        
        obj = xml.dom.minidom.parseString(resp.read())
        words = obj.getElementsByTagName('word')
        
        # 結果があることを確認
        if ( len(words) == 0 ):
            return sentence

        result = u''

        for i in range(len(words)):
            # 形態素の品詞を取得
            position = words[i].childNodes[2].childNodes[0].data
            if position == self.position :
                # ターゲットとなる品詞なら文字列を前に追加
                result += self.text
            result += words[i].childNodes[0].childNodes[0].data

        return result

if __name__ == "__main__":
    pass
