# -*- coding: cp1251 -*-
from zope.traversing.browser import absoluteURL
from zope.component import getUtility,getMultiAdapter
from qreature.interfaces import ISlotQuiz, IScaleQuiz, IAnswerDepends, IQuizResult,IQreatureUtility
#from zope.app.intid.interfaces import IIntIds
from qreature.interfaces import IQreatureIntIds,IQuizQuestion,IQuizAnswer
from qreature.browser.result.result_interval import INTERVAL_KEY
from zope.annotation.interfaces import IAnnotations
from zope.security.proxy import removeSecurityProxy
from qreature.browser.user_quiz.utilities import extract_previous_answers,extract_answers
from zope.interface import Interface,implements
from qreature.browser.user_quiz.interfaces import IResult, IOtherResult
from zope.app.component.hooks import getSite
from zope.app.pagetemplate import ViewPageTemplateFile
from countable.interfaces import ICounterExplorer
from zope.event import notify
from qreature.browser.events import ResultShown

class Result(object):
    
    implements(IResult)
    int_ids = None
    result = None
        
    @property
    def quizURL(self):
        return absoluteURL(self.context, self.request)
    
    def __call__(self):
#        try:
        self.update()
        return self.render()
#        except:
#            return self.request.response.redirect(self.quizURL + u'/go.html')
            

    def update(self):
        previous_answers = extract_previous_answers(self.request)
        #previous_answers = previous_answers[1:]
        answers = extract_answers(self.request)
        previous_answers += answers
        self.calculate(previous_answers)
            
        
    def calculate(self, answers):
        if ISlotQuiz.providedBy(self.context):
            self.calculate_for_slots(answers)
        elif IScaleQuiz.providedBy(self.context):
            self.calculate_for_scale(answers)
        
    
    
    def calculate_for_scale(self, received_answers):
        answers = self.getAnswers(received_answers)
        values = 0
        for answer in answers:
            if answer.has_key('value'):
                values += int(answer['value'].value)
        self.values = values
        results = [result for result in self.context.values() if IQuizResult.providedBy(result)]
        results.sort(key=lambda x: IAnnotations(removeSecurityProxy(x)).get(INTERVAL_KEY))
        
        if values == 0:
            self.result = results[0]
            return
        
        if values >= IAnnotations(removeSecurityProxy(results[-1])).get(INTERVAL_KEY):
            self.result = results[-1]
            return

        for i,v in enumerate(results):
            if i == 0:bottom_border = 0
            else: bottom_border = IAnnotations(removeSecurityProxy(results[i-1])).get(INTERVAL_KEY)
            top_border = IAnnotations(removeSecurityProxy(v)).get(INTERVAL_KEY)
            if bottom_border <= values <= top_border:
                self.result = v
                return
                
    def calculate_for_slots(self, received_answers):
        answers = self.getAnswers(received_answers)
        result_map = {}
        depends = [[d for d in a.values() if IAnswerDepends.providedBy(d)]
                   for a in answers]
        flatten = getUtility(IQreatureUtility, name="Flatten")
        depends = flatten(depends)
        for depend in depends:
            result_map[depend.result_id] = result_map.get(depend.result_id, 0) + depend.depend_value
        result_id = max = 0
        for id, value in result_map.items():
            if value >max:
                max = value
                result_id = id
        self.result = self.int_ids.getObject(result_id)
        
        
    def getAnswers(self, received_answers):
        answers = []
        self.int_ids = getUtility(IQreatureIntIds, context=self.context)
        for answer in received_answers:
            a = self.int_ids.getObject(int(answer))
            answers.append(a)
        return answers
    
    def render(self):
        result = getMultiAdapter((self.result, self.request),Interface, name="preview.html")
        result.need_button = False
        if IScaleQuiz.providedBy(self.context): result.values = self.values
        result.update()
        result = result.render()
        cookie_content_for_result = str(self.int_ids.getId(self.result))
        site_int_ids = getUtility(IQreatureIntIds, context = self.context.__parent__)
        cookie_name_for_quiz = str(site_int_ids.getId(self.context))
        cookie = self.request.get(cookie_name_for_quiz,None)
        if cookie is None:
            self.request.response.setCookie(cookie_name_for_quiz,cookie_content_for_result + "_",path='/')
            notify(ResultShown(self.result))
        else:
            if cookie_content_for_result in cookie.split("_"):
                pass
            else:
                new_cookie = cookie + cookie_content_for_result + "_"
                self.request.response.setCookie(cookie_name_for_quiz,new_cookie + "_",path='/')
                notify(ResultShown(self.result))
                
        return result



    
class OpenValues(object):
    def gimmeValues(self):
        return self.__parent__.values
    def gimmeTotalValues(self):
        quiz = getSite()
        values = 0
        questions = [q for q in quiz.values() if IQuizQuestion.providedBy(q)]
        for q in questions:
            max_value = 0
            for a in q.values():
                if IQuizAnswer.providedBy(a):
                    value = int(a['value'].value)
                    if value > max_value:
                        max_value = value
            values+=max_value
        return values

class OpenResults(object):
    def gimmeResults(self):
        quiz = getSite()
        this_result = removeSecurityProxy(self.__parent__.context)
        results = [r for r in quiz.values() if IQuizResult.providedBy(r)]
        for r in results:
            if r is this_result: continue
            title = r.title
            url = absoluteURL(r,self.request) + '/other_result.html'
            yield {'title':title, 'url':url}

from commentable.interfaces import IHeadView
            
class OtherResult(object):
    implements(IOtherResult, IHeadView)
    rolled = True
    root = False
    render = ViewPageTemplateFile('./templates/result.pt')
    result = None
    def __call__(self):
        self.update()
        return self.render()
    def update(self):
        result = getMultiAdapter((self.context, self.request),Interface, name="preview.html")
        result.need_button = False
        result.source = False
        result.update()
        self.result = result
        return result.render()


from goog.chart.interfaces import IGoogChart

  
class Chart(object):
    
    def update(self):
        quiz = getSite()
        int_ids = getUtility(IQreatureIntIds, context=self.context)
        ce = getUtility(ICounterExplorer, context=self.context)
        results= [r for r in quiz.values() if IQuizResult.providedBy(r)]
        self.titles = [r.title.encode('utf-8') for r in results]
        self.counters = [ce.getCounter(r, key=int_ids.getId(r)) for r in results]
        
        
    def render(self):
        gc = getUtility(IGoogChart,name='GoogChart')
        chart = gc('p',self.counters,chdl='|'.join(self.titles),chdlp='bv').output_encoding('UTF-8')
        chart.color('e9942a')
        if len(self.titles) > 10: chart.size('150','450')
        else: chart.size('150','300')
        return u'<h2>Распределение пользователей по результатам</h2><div>' + unicode(chart.img()) + u'</div>'
