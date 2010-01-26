# -*- coding: cp1251 -*-
from z3c.form import button, form
from qreature.interfaces import  IScaleQuiz, ISlotQuiz
from zope.component import getUtility, adapts
from zope.security.proxy import removeSecurityProxy
from zope.traversing.browser.absoluteurl import absoluteURL
from zope.app.pagetemplate import ViewPageTemplateFile
from qreature.interfaces import ILeadedQuiz
from z3c.form import field,  interfaces
from qreature.interfaces import IQuiz
from zope.interface import implements
from z3c.form.datamanager import AttributeField
from z3c.form.converter import NumberDataConverter, _
from qreature.browser.quiz_constructor.interfaces import IQuizPages,IPages
from zope.annotation.interfaces import IAnnotations
from qreature.browser.links import QreaturePictureLink
from qreature.interfaces import IQreatureUtility
from qreature.browser.quiz_constructor.interfaces import ITexturedQuestionsQuiz,ITexturedAnswersQuiz
from zope.event import notify
from qreature.browser.events import CachedObjectChangedEvent
from qreature.browser.actions import unpublish, QuizChecker
from qreature.browser.actions import QuizAction as CommonQuizAction
from qreature.interfaces import IQuizAnswer,IQuizQuestion,IQuizResult
from qreature.browser.user_quiz.interfaces import IPublished
from qreature.browser.events import CleanCacheEvent
from qreature.interfaces import IAnswerLeads

class QuizAction(CommonQuizAction):
    template = ViewPageTemplateFile('templates/right_button.pt')
    @property
    def site_url(self):
        return self.request.get('HTTP_REFERER')
        #return absoluteURL(self.context,self.request) + '/constructor.html'

def clean_answers_viewlets(quiz):
    answers = [[answer for answer in question.values() if IQuizAnswer.providedBy(answer)]
               for question in quiz.values() if IQuizQuestion.providedBy(question)]
    flatten = getUtility(IQreatureUtility, name="Flatten")
    answers = [answer for answer in flatten(answers)]
    notify(CachedObjectChangedEvent(answers))    

def clean_questions_viewlets(quiz):
    questions = [question for question in quiz.values() if IQuizQuestion.providedBy(question)]
    notify(CachedObjectChangedEvent(questions))

def clean_results_viewlets(quiz):
    results = [result for result in quiz.values() if IQuizResult.providedBy(result)]
    notify(CachedObjectChangedEvent(results))    


class Scale(QuizAction,form.Form):  
    """ """    
    button_title = u'Схема шкала'
    buttons = button.Buttons(button.ImageButton
                             (name='scale_button',title=u'ScaleButton',image=u'scale_button.jpg'))
    
    @button.handler(buttons['scale_button'])
    def scale(self, action):
        self.swapInterface(ISlotQuiz)
        self.swapInterface(IScaleQuiz)
        clean_answers_viewlets(self.context)
        clean_results_viewlets(self.context)
        return self.request.response.redirect(self.site_url)
   
    
class Slots(QuizAction,form.Form):  
    """ """
    button_title = u'Схема слоты'
    buttons = button.Buttons(button.ImageButton
                             (name='slots_button',title=u'SlotsButton',image=u'slots_button.jpg'))
    
    @button.handler(buttons['slots_button'])
    def slots(self, action):
        self.swapInterface(ISlotQuiz)
        self.swapInterface(IScaleQuiz)
        clean_answers_viewlets(self.context)
        clean_results_viewlets(self.context)
        return self.request.response.redirect(self.site_url)
    


class Leaded(QuizAction,form.Form):  
    """ """
    button_title = u'Перемещения'
    buttons = button.Buttons(button.ImageButton
                             (name='lead_button',title=u'LeadedButton',image=u'lead_button.jpg'))
    
    @button.handler(buttons['lead_button'])
    def leaded(self, action):
        self.swapInterface(ILeadedQuiz)
        unpublish(self.context)
        clean_answers_viewlets(self.context)
        return self.request.response.redirect(self.site_url)





class TexturedButtonQuestions(QuizAction,form.Form):  
    """ """
    button_title = u'Текст вопросов'
    buttons = button.Buttons(button.ImageButton
                             (name='text_button_questions',title=u'TextButtonQuestions',image=u'text_button_questions.jpg'))
    

    @button.handler(buttons['text_button_questions'])
    def textured(self, action):
        self.swapInterface(ITexturedQuestionsQuiz)
        clean_questions_viewlets(self.context)
        return self.request.response.redirect(self.site_url)

class TexturedButtonAnswers(QuizAction,form.Form):  
    """ """
    button_title = u'Текст ответов'
    buttons = button.Buttons(button.ImageButton
                             (name='text_button_answers',title=u'TextButtonAnswers',image=u'text_button_answers.jpg'))
    

    @button.handler(buttons['text_button_answers'])
    def textured(self, action):
        self.swapInterface(ITexturedAnswersQuiz)
        clean_answers_viewlets(self.context)
        return self.request.response.redirect(self.site_url)


class QuizPages(object):
    """ This object represent the interval, extracted from result annotation,
    via adapter. It is adapter itself"""
    implements(IQuizPages)
    adapts(IQuiz)
    def __init__(self, context):
        self.context = context

PAGES_KEY = 'pages'

class QuizPagesForm(form.EditForm):
    
    def __init__(self, context,request,view,manager):
        self.context = context
        self.request = request
        self.view = view
        self.manager = manager
        
    template = ViewPageTemplateFile('templates/pages_form.pt')
    fields = field.Fields(IQuizPages)
    buttons = button.Buttons(button.ImageButton
                             (name='quiz_pages',title=u'QuizPages',image=u'apply.jpg'))
    
    @button.handler(buttons['quiz_pages'])
    def handlePages(self, action):
        super(QuizPagesForm,self).handleApply(self,action)
        notify(CleanCacheEvent(self.context))
        return self.request.response.redirect(self.request.URL)


class PagesDataManager(AttributeField):
    adapts(IQuiz, IPages)
    def get(self):
        pages = IAnnotations(removeSecurityProxy(self.context)).get(PAGES_KEY)
        return pages

    def set(self, value):
        ann = IAnnotations(removeSecurityProxy(self.context))
        ann[PAGES_KEY] = value

class PagesDataConverter(NumberDataConverter):
    """A data converter for integers."""
    adapts(IPages, interfaces.IWidget)
    type = int
    errorMessage = _('The entered value is not a valid integer literal')
    def toFieldValue(self, value):
        try:
            return int(value)
        except:
            super(PagesDataConverter,self).toFieldValue(value) 



class CheckButton(QuizAction,form.Form): 
    """ """
    button_title = u'Проверить'
    buttons = button.Buttons(button.ImageButton
                             (name='check',title=u'Check',image=u'check_button.jpg'))
    
    
    @button.handler(buttons['check'])
    def check(self,action):
        checker = QuizChecker(self.context,self.request)
        response = checker.check()
        if response is None:
            self.status = checker.status




class PublishButton(QuizAction,form.Form):  
    """ """
    button_title = u'Опубликовать'
    buttons = button.Buttons(button.ImageButton
                             (name='publish',title=u'Publish',image=u'publish_button.jpg'))
    
    @button.handler(buttons['publish'])
    def publish(self, action):
        self.swapInterface(IPublished)
        if IPublished.providedBy(self.context):
            notify(CleanCacheEvent(self.context))
            url = absoluteURL(self.context,self.request)
            return self.request.response.redirect(url + '/preview.html')
        else:
            status = u'Доступ к тесту закрыт'
        self.status = status
        notify(CleanCacheEvent(self.context))

    
class PreviewButton(QreaturePictureLink):
    title=u'Просмотр'
    url='/go.html'
    image='preview_button'
    render = ViewPageTemplateFile('templates/preview.pt')


