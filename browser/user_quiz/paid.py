# -*- coding: utf-8 -*-

from zif.jsonserver import minjson
from zope.component import getMultiAdapter
import urllib
from zope.traversing.browser import absoluteURL
import re


#the request string from js is good enough (see paid.js)
#it only need to get it as a string and make a call with such request (without trailing result=result) :)
class Paid(object):
    
    def __call__(self):
        if self.request.get('result') is not None:
            page_name = 'result.html'
        else:
            page_name = 'go.html'
        #local!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#        paid_url = re.sub(u'http://localhost:8080/\+\+skin\+\+Qreature/qreature/',\
#                            u'http://localhost:8080/++skin++Paid/qreature/',\
#                            unicode(self.request.URL))
        #remote!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        paid_url = re.sub(u'http://qreature.ru/',\
                            u'http://91.189.177.18:11080/++skin++Paid/qreature/',\
                            unicode(self.request.URL))
        paid_url = re.sub('paidQuiz', page_name,paid_url)
        user_quiz = urllib.urlopen(paid_url).read()
        if self.request.get('result') is not None:
            r = re.compile('<i>HTML Код для блога или сайта</i>')
            user_quiz = user_quiz[:r.search(user_quiz).start()]
        return 'makeUpdate(' + minjson.write({'user_quiz':user_quiz}) + ');'