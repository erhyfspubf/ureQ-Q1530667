 # -*- coding: cp1251 -*-
from qreature.interfaces import IQuizResult,IQreatureUtility,IQuizAnswer,IAnswerDepends,IQuizQuestion
from z3c.form import form, field, interfaces, button
from qreature.quiz import QuizResult
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.formlib.namedtemplate import NamedTemplateImplementation
from zope.formlib.namedtemplate import NamedTemplate
from zope.traversing.browser import absoluteURL
from zope.component import getUtility, adapts,getMultiAdapter,queryMultiAdapter
from qreature.browser.qreature_views import QreatureAddForm,QreatureEditForm,QreatureContentTitle 
from qreature.skin.interfaces import IScaleLayer, ISlotLayer
from zope.app.component.hooks import getSite
from qreature.interfaces import IQreatureIntIds
from qreature.browser.events import CachedObjectChangedEvent
from zope.event import notify



def clean_depends():
    site = getSite()
    flatten = getUtility(IQreatureUtility, name="Flatten")
    
    answers = [[a for a in q.values() if IQuizAnswer.providedBy(a)] for q in site.values() if IQuizQuestion.providedBy(q)]
    answers = [a for a in flatten(answers)]
    depends = [[d for d in a.values() if IAnswerDepends.providedBy(d)] for a in answers]
    depends = [d for d in flatten(depends)]
    for d in depends:
        a = d.__parent__
        if a in answers:
            answers.remove(a)
    notify(CachedObjectChangedEvent(answers + depends))
    


class QuizResultAddForm(QreatureAddForm):
    
    fields = field.Fields(IQuizResult).omit('__parent__')
    form_name=u'Добавление результата'
    button_name = u'Создать результат'
    def create(self, data):
        #when i add result, it SlotLayer, it need to destroy all viewlets for
        #dependencies and add forms
        if ISlotLayer.providedBy(self.request):
            clean_depends()
        return QuizResult(**data)


class QuizResultEditForm(QreatureEditForm):
    fields = field.Fields(IQuizResult).omit('__parent__')
    form_name=u'Редактирование результата'
    buttons = button.Buttons(button.ImageButton
                         (name='apply',title=u'Apply',image=u'apply.jpg'))
    @button.handler(buttons['apply'])
    def handleApply(self, action):
        super(QuizResultEditForm,self).handleApply(self,action)
        if ISlotLayer.providedBy(self.request):
            clean_depends()
        

#This is a viewlet for another viewlet: ResultsForConstructor
class ResultForConstructor(QreatureContentTitle):
    @property
    def picture(self):
        if ISlotLayer.providedBy(self.request): return"slots"
        elif IScaleLayer.providedBy(self.request): return "scale"
    css_class="result"

class ResultCollect(object):
    render = ViewPageTemplateFile('templates/result_collect.pt')
    
    def update(self):
        int_ids = getUtility(IQreatureIntIds, context = self.context)
        self.id = int_ids.getId(self.context)
    
    def gimmeDependValue(self):
        quiz = getSite()
        depends = [[[d for d in a.values() if IAnswerDepends.providedBy(d)]
                      for a in q.values() if IQuizAnswer.providedBy(a)]
                      for q in quiz.values() if IQuizQuestion.providedBy(q)]
        flatten = getUtility(IQreatureUtility, name="Flatten")
        depends = flatten(depends)
        depends_values = [d.depend_value for d in depends if d.result_id == self.id]
        depend_value = 0
        for d in depends_values:
            depend_value += d
        return unicode(depend_value)



class WidgetFactoryForResultInsertForm(object):
    def __init__(self, result):
        self.result = result
    def gimmeWidget(self, field, request):
        widget = getMultiAdapter((field, request), interfaces.IFieldWidget)
        def gimmeValue():
            quiz = self.result.__parent__
            quiz_url = absoluteURL(quiz, request)
            return self.result.result + u'<div><a href="' + quiz_url + u'">' + quiz.title +u'</a></div>'
        widget.extract = gimmeValue
        return widget
        
class ResultInsertForm(form.Form):
    @property
    def fields(self):
        fields = field.Fields(IQuizResult['result'])
        fields['result'].widgetFactory = WidgetFactoryForResultInsertForm(self.context).gimmeWidget
        return fields
    
    template = NamedTemplate('qreature.result_insert_form')  

insert_form_template = NamedTemplateImplementation(
    ViewPageTemplateFile('templates/result_insert_form.pt'))